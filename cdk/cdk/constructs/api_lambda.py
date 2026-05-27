"""
ApiLambda Construct: FastAPI を実行する Lambda + IAM + Function URL を一括で構築する。
"""
from aws_cdk import (
    Duration,
    BundlingOptions,
    aws_lambda as lambda_,
    aws_logs as logs,
    aws_iam as iam,
)
from constructs import Construct


class ApiLambda(Construct):
    """
    FastAPI バックエンド用 Lambda 関数とその周辺リソースをまとめた Construct。

    Attributes:
        function: Lambda 関数本体
        function_url: Lambda Function URL
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        env_name: str,
        env_vars: dict,
    ) -> None:
        super().__init__(scope, construct_id)

        s3_bucket_name = env_vars["S3_BUCKET_NAME"]
        ssm_prefix = f"/blog-platform-backend/{env_name}"

        # ===== Lambda 関数 =====
        self.function = lambda_.Function(
            self,
            "Handler",
            runtime=lambda_.Runtime.PYTHON_3_12,
            architecture=lambda_.Architecture.ARM_64,
            handler="app.main.handler",
            code=lambda_.Code.from_asset(
                "..",
                bundling=BundlingOptions(
                    image=lambda_.Runtime.PYTHON_3_12.bundling_image,
                    command=[
                        "bash",
                        "-c",
                        " && ".join(
                            [
                                "pip install "
                                "--platform manylinux2014_aarch64 "
                                "--target /asset-output "
                                "--only-binary :all: "
                                "-r requirements.txt",
                                "cp -r app /asset-output/",
                            ]
                        ),
                    ],
                ),
            ),
            memory_size=512,
            timeout=Duration.seconds(30),
            environment={
                "APP_ENV": env_vars["APP_ENV"],
                "ALGORITHM": env_vars.get("ALGORITHM", "HS256"),
                "S3_BUCKET_NAME": s3_bucket_name,
                "S3_REGION": env_vars["S3_REGION"],
                "CLOUDFRONT_DOMAIN": env_vars["CLOUDFRONT_DOMAIN"],
                "CORS_ALLOW_ORIGINS": env_vars["CORS_ALLOW_ORIGINS"],
                "DATABASE_URL_SSM": f"{ssm_prefix}/DATABASE_URL",
                "SECRET_KEY_SSM": f"{ssm_prefix}/SECRET_KEY",
            },
            log_retention=logs.RetentionDays.ONE_WEEK,
        )

        # ===== IAM 権限 =====
        self._grant_permissions(s3_bucket_name=s3_bucket_name, ssm_prefix=ssm_prefix)

        # ===== Function URL =====
        # CORS は FastAPI CORSMiddleware に一本化する (Function URL 側で設定すると
        # アプリ層と二重に CORS ヘッダーが付き、ブラウザがエラー扱いするため)
        self.function_url = self.function.add_function_url(
            auth_type=lambda_.FunctionUrlAuthType.NONE,
        )

    def _grant_permissions(self, *, s3_bucket_name: str, ssm_prefix: str) -> None:
        stack = self.node.scope  # 親 Stack 参照
        region = stack.region  # type: ignore[union-attr]
        account = stack.account  # type: ignore[union-attr]

        # SSM Parameter Store (環境別パス配下のみ)
        self.function.add_to_role_policy(
            iam.PolicyStatement(
                actions=["ssm:GetParameter"],
                resources=[f"arn:aws:ssm:{region}:{account}:parameter{ssm_prefix}/*"],
            )
        )
        # SecureString の復号 (AWS マネージド SSM キー経由のみ)
        self.function.add_to_role_policy(
            iam.PolicyStatement(
                actions=["kms:Decrypt"],
                resources=[f"arn:aws:kms:{region}:{account}:key/*"],
                conditions={
                    "StringEquals": {"kms:ViaService": f"ssm.{region}.amazonaws.com"}
                },
            )
        )
        # S3 (画像アップ・取得・削除)
        self.function.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "s3:PutObject",
                    "s3:GetObject",
                    "s3:DeleteObject",
                ],
                resources=[f"arn:aws:s3:::{s3_bucket_name}/*"],
            )
        )
