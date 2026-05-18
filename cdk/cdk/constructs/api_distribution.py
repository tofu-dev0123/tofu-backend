"""
ApiDistribution Construct: API を CloudFront でカスタムドメイン公開する。

- ACM 証明書を us-east-1 で取得 (CloudFront 用は us-east-1 必須)
- 検証は DNS validation → Cloudflare 側で検証用 CNAME を手動追加する
- CloudFront Distribution は origin に Lambda Function URL を指定
- キャッシュは無効 (API のため)、Host ヘッダー以外を全て転送
"""
from aws_cdk import (
    aws_certificatemanager as acm,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_lambda as lambda_,
)
from constructs import Construct


class ApiDistribution(Construct):
    """
    Lambda Function URL の前段に CloudFront + ACM 証明書を配置する Construct。

    Attributes:
        certificate: ACM 証明書 (DNS 検証必要)
        distribution: CloudFront Distribution
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        function_url: lambda_.FunctionUrl,
        custom_domain: str,
        comment: str | None = None,
    ) -> None:
        super().__init__(scope, construct_id)

        # ACM 証明書 (CloudFront 用は us-east-1 で発行)
        # validation=from_dns() で DNS 検証用 CNAME が出力される (AWS Console / CFN events で確認)
        self.certificate = acm.Certificate(
            self,
            "Certificate",
            domain_name=custom_domain,
            validation=acm.CertificateValidation.from_dns(),
        )

        # CloudFront Distribution
        self.distribution = cloudfront.Distribution(
            self,
            "Distribution",
            comment=comment or f"API distribution for {custom_domain}",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.FunctionUrlOrigin(function_url),
                # API なのでキャッシュ無効
                cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
                # ヘッダー / Cookie / クエリ全て転送 (Host だけ除外: Lambda Function URL 要求)
                origin_request_policy=cloudfront.OriginRequestPolicy.ALL_VIEWER_EXCEPT_HOST_HEADER,
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL,
            ),
            domain_names=[custom_domain],
            certificate=self.certificate,
            minimum_protocol_version=cloudfront.SecurityPolicyProtocol.TLS_V1_2_2021,
        )
