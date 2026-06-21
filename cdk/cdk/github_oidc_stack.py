"""
GithubOidcStack: GitHub Actions OIDC ブートストラップ専用スタック。

.env 非依存・env context 非依存。CI/CD 構築前にローカルから一度だけ deploy する。
"""
from aws_cdk import Stack
from constructs import Construct

from cdk.constructs.github_oidc import GithubOidc


class GithubOidcStack(Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        github_owner: str,
        github_repo: str,
        environments: list[str],
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        GithubOidc(
            self,
            "GithubOidc",
            github_owner=github_owner,
            github_repo=github_repo,
            environments=environments,
        )
