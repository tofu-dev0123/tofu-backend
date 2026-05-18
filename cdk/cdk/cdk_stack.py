"""
CdkStack: API 用 Lambda と、オプションで CloudFront カスタムドメインを組み立てる。
"""
from aws_cdk import (
    Stack,
    CfnOutput,
)
from constructs import Construct

from cdk.constructs.api_lambda import ApiLambda
from cdk.constructs.api_distribution import ApiDistribution


class CdkStack(Stack):

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

        # API 用 Lambda + IAM + Function URL
        api = ApiLambda(self, "Api", env_name=env_name, env_vars=env_vars)

        CfnOutput(
            self,
            "FunctionUrl",
            value=api.function_url.url,
            description=f"Lambda Function URL ({env_name}) - 直接アクセス用",
        )

        # カスタムドメイン (CUSTOM_DOMAIN が指定された時のみ)
        custom_domain = env_vars.get("CUSTOM_DOMAIN")
        if custom_domain:
            distribution = ApiDistribution(
                self,
                "Distribution",
                function_url=api.function_url,
                custom_domain=custom_domain,
                comment=f"API distribution for {env_name}: {custom_domain}",
            )

            CfnOutput(
                self,
                "CustomDomainUrl",
                value=f"https://{custom_domain}",
                description="API カスタムドメイン (推奨アクセス先)",
            )
            CfnOutput(
                self,
                "CloudFrontDomain",
                value=distribution.distribution.distribution_domain_name,
                description="Cloudflare で CNAME を設定する先 (xxx.cloudfront.net)",
            )
