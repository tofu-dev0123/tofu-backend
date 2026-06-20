#!/usr/bin/env python3
"""
CDK エントリポイント

使い方:
    cdk deploy -c env=dev          # .env.dev を読んで dev Stack を deploy
    cdk deploy -c env=prod         # .env.prod を読んで prod Stack を deploy
    cdk synth  -c env=dev          # 同じく synth

    # env context なし → GitHub Actions OIDC ブートストラップスタック
    cdk deploy BlogPlatformBackend-GithubOidc
"""
import os
from pathlib import Path

import aws_cdk as cdk
from dotenv import dotenv_values

from cdk.cdk_stack import CdkStack
from cdk.github_oidc_stack import GithubOidcStack


app = cdk.App()

# account/region は全スタック共通 (cdk CLI の AWS 認証情報から自動補完)
cdk_env = cdk.Environment(
    account=os.getenv("CDK_DEFAULT_ACCOUNT"),
    region=os.getenv("CDK_DEFAULT_REGION", "us-east-1"),
)

# ===== 環境名の取得 =====
env_name = app.node.try_get_context("env")

if env_name:
    # ===== 環境別デプロイ設定の読み込み =====
    # 非機密のデプロイ設定は cdk/config/<env_name>.env にコミットして管理する
    # (どのマシン/CI からでも同じ設定でデプロイできるようにするため)。
    # 機密値 (DATABASE_URL / SECRET_KEY) は SSM Parameter Store 側で管理し、
    # Lambda 実行時に取得する (app/core/config.py の _populate_env_from_ssm 参照)。
    config_path = Path(__file__).parent / "config" / f"{env_name}.env"

    if not config_path.exists():
        raise FileNotFoundError(
            f"{config_path} が存在しません。"
            " cdk/config/<env>.env を作成してください。"
        )

    env_vars = {k: v for k, v in dotenv_values(config_path).items() if v}

    # CDK が Lambda env に乗せるために必要な最低限のキー
    required = [
        "APP_ENV",
        "S3_BUCKET_NAME",
        "S3_REGION",
        "CLOUDFRONT_DOMAIN",
        "CORS_ALLOW_ORIGINS",
    ]
    missing = [k for k in required if not env_vars.get(k)]
    if missing:
        raise ValueError(
            f".env.{env_name} に以下のキーが不足しています: {missing}"
        )

    # ===== Stack を環境別の名前で作成 =====
    CdkStack(
        app,
        f"BlogPlatformBackend-{env_name}",
        env_name=env_name,
        env_vars=env_vars,
        env=cdk_env,
    )
else:
    # ===== env context なし → OIDC ブートストラップのみ =====
    GithubOidcStack(
        app,
        "BlogPlatformBackend-GithubOidc",
        github_owner="tofu-dev0123",
        github_repo="tofu-backend",
        environments=["dev", "prod"],
        env=cdk_env,
    )

app.synth()
