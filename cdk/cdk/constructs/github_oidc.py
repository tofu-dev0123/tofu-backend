"""
GithubOidc Construct: GitHub Actions 用 OIDC Provider と
CDK デプロイ用 IAM Role を構築する。

GitHub Actions が長期 IAM キーなしで cdk deploy できるようにするための
OIDC フェデレーション一式。CI/CD 構築前にローカルから一度だけ deploy する。
"""
from aws_cdk import (
    CfnOutput,
    Duration,
    aws_iam as iam,
)
from constructs import Construct

GITHUB_OIDC_AUD = "sts.amazonaws.com"
# OIDC Provider の URL ホスト部 (ARN・条件キーの prefix に使う)
OIDC_DOMAIN = "token.actions.githubusercontent.com"


class GithubOidc(Construct):
    """
    GitHub Actions OIDC フェデレーション一式。

    Attributes:
        provider: OpenID Connect Provider
        role: GitHub Actions から AssumeRole される CDK デプロイ用 Role
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        github_owner: str,
        github_repo: str,
        environments: list[str],
    ) -> None:
        super().__init__(scope, construct_id)

        stack = self.node.scope  # 親 Stack 参照 (api_lambda.py 踏襲)
        region = stack.region  # type: ignore[union-attr]
        account = stack.account  # type: ignore[union-attr]

        # ===== OIDC Provider =====
        # GitHub OIDC Provider はアカウントで URL ごとに一意の共有リソース。
        # 既にアカウントに存在するため新規作成せず ARN でインポートする
        # (このスタックが共有 Provider のライフサイクルを握らないようにする)。
        provider_arn = (
            f"arn:aws:iam::{account}:oidc-provider/{OIDC_DOMAIN}"
        )
        self.provider = iam.OpenIdConnectProvider.from_open_id_connect_provider_arn(
            self,
            "Provider",
            provider_arn,
        )

        # ===== 信頼ポリシーの sub 条件 (GitHub Environments ベース) =====
        allowed_subs = [
            f"repo:{github_owner}/{github_repo}:environment:{e}"
            for e in environments
        ]

        principal = iam.OpenIdConnectPrincipal(
            self.provider,
            conditions={
                "StringEquals": {
                    f"{OIDC_DOMAIN}:aud": GITHUB_OIDC_AUD,
                },
                "StringLike": {
                    f"{OIDC_DOMAIN}:sub": allowed_subs,
                },
            },
        )

        # ===== デプロイ用 Role =====
        self.role = iam.Role(
            self,
            "DeployRole",
            role_name="github-actions-cdk-deploy",
            assumed_by=principal,
            description=(
                "Assumed by GitHub Actions (OIDC) to run cdk deploy "
                f"for {github_owner}/{github_repo}"
            ),
            max_session_duration=Duration.hours(1),
        )

        # ===== 権限: CDK bootstrap ロールへの AssumeRole に限定 =====
        # モダン CDK の cdk deploy は bootstrap 時生成の execution ロール群を
        # AssumeRole して実行する。よって CI ロールには以下で十分。
        self.role.add_to_policy(
            iam.PolicyStatement(
                actions=["sts:AssumeRole"],
                resources=[
                    f"arn:aws:iam::{account}:role/cdk-hnb659fds-*-{account}-{region}",
                ],
                conditions={
                    "StringEquals": {
                        "iam:ResourceTag/aws-cdk:bootstrap-role": [
                            "deploy",
                            "file-publishing",
                            "image-publishing",
                            "lookup",
                        ],
                    },
                },
            )
        )

        # cdk が bootstrap version を確認する SSM パラメータの読取
        self.role.add_to_policy(
            iam.PolicyStatement(
                actions=["ssm:GetParameter"],
                resources=[
                    f"arn:aws:ssm:{region}:{account}:parameter/cdk-bootstrap/hnb659fds/version",
                ],
            )
        )

        # ===== 出力 =====
        CfnOutput(
            self,
            "DeployRoleArn",
            value=self.role.role_arn,
            description="GitHub Actions が assume する CDK デプロイ用 Role ARN",
        )
        CfnOutput(
            self,
            "OidcProviderArn",
            value=self.provider.open_id_connect_provider_arn,
            description="GitHub Actions OIDC Provider ARN",
        )
