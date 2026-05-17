import json

from aws_cdk import (
    Stack,
    Duration,
    BundlingOptions,
    CfnOutput,
    aws_lambda as lambda_,
    aws_logs as logs,
    aws_iam as iam,
)
from constructs import Construct


class CdkStack(Stack):
    """
    Lambda + Function URL + IAM ロール + CloudWatch Log Group を作成する。
    既存リソース (S3 / CloudFront / Neon / SSM の値本体) は CDK 管理外。
    Lambda はそれらを env vars 経由で参照する。
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        env_name: str,
        env_vars: dict,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        s3_bucket_name = env_vars["S3_BUCKET_NAME"]
        cors_origins = json.loads(env_vars["CORS_ALLOW_ORIGINS"])
        ssm_prefix = f"/blog-platform-backend/{env_name}"

        # ===== Lambda 関数 =====
        fn = lambda_.Function(
            self,
            "ApiHandler",
            runtime=lambda_.Runtime.PYTHON_3_12,
            architecture=lambda_.Architecture.ARM_64,
            handler="app.main.handler",
            code=lambda_.Code.from_asset(
                "..",  # backend/ ルートを bundle 対象に
                bundling=BundlingOptions(
                    image=lambda_.Runtime.PYTHON_3_12.bundling_image,
                    command=[
                        "bash",
                        "-c",
                        " && ".join(
                            [
                                # ARM64 用 wheel を強制取得 (Linux 以外のホストでも動作)
                                "pip install "
                                "--platform manylinux2014_aarch64 "
                                "--target /asset-output "
                                "--only-binary :all: "
                                "-r requirements.txt",
                                # アプリコードを同梱 (alembic は Lambda では使わないので除外)
                                "cp -r app /asset-output/",
                            ]
                        ),
                    ],
                ),
            ),
            memory_size=512,
            timeout=Duration.seconds(30),
            environment={
                # .env から読んだ値 (deploy 時に固定で Lambda env に埋まる)
                "APP_ENV": env_vars["APP_ENV"],
                "ALGORITHM": env_vars.get("ALGORITHM", "HS256"),
                "S3_BUCKET_NAME": s3_bucket_name,
                "CLOUDFRONT_DOMAIN": env_vars["CLOUDFRONT_DOMAIN"],
                "CORS_ALLOW_ORIGINS": env_vars["CORS_ALLOW_ORIGINS"],
                # secret は SSM パスのみ Lambda env に渡し、本体は runtime fetch
                "DATABASE_URL_SSM": f"{ssm_prefix}/DATABASE_URL",
                "SECRET_KEY_SSM": f"{ssm_prefix}/SECRET_KEY",
            },
            log_retention=logs.RetentionDays.ONE_WEEK,
        )

        # ===== IAM 権限 =====
        # SSM Parameter Store 読み取り (環境別パス配下のみ)
        fn.add_to_role_policy(
            iam.PolicyStatement(
                actions=["ssm:GetParameter"],
                resources=[
                    f"arn:aws:ssm:{self.region}:{self.account}:parameter{ssm_prefix}/*"
                ],
            )
        )
        # SecureString の復号 (AWS マネージド SSM キー経由のみ)
        fn.add_to_role_policy(
            iam.PolicyStatement(
                actions=["kms:Decrypt"],
                resources=[f"arn:aws:kms:{self.region}:{self.account}:key/*"],
                conditions={
                    "StringEquals": {
                        "kms:ViaService": f"ssm.{self.region}.amazonaws.com"
                    }
                },
            )
        )
        # S3 (画像アップ・取得・削除)
        fn.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "s3:PutObject",
                    "s3:GetObject",
                    "s3:DeleteObject",
                ],
                resources=[f"arn:aws:s3:::{s3_bucket_name}/*"],
            )
        )

        # ===== Function URL =====
        fn_url = fn.add_function_url(
            auth_type=lambda_.FunctionUrlAuthType.NONE,
            cors=lambda_.FunctionUrlCorsOptions(
                allowed_origins=cors_origins,
                allowed_methods=[lambda_.HttpMethod.ALL],
                allowed_headers=["*"],
                allow_credentials=True,
            ),
        )

        # ===== 出力 =====
        CfnOutput(
            self,
            "FunctionUrl",
            value=fn_url.url,
            description=f"Lambda Function URL ({env_name})",
        )
