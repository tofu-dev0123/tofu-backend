#!/usr/bin/env python3
"""
CDK エントリポイント

使い方:
    cdk deploy -c env=develop      # .env.develop を読んで dev Stack を deploy
    cdk deploy -c env=production   # .env.production を読んで prod Stack を deploy
    cdk synth -c env=develop       # 同じく synth
"""
import os
from pathlib import Path

import aws_cdk as cdk
from dotenv import dotenv_values

from cdk.cdk_stack import CdkStack


app = cdk.App()

# ===== 環境名の取得 =====
env_name = app.node.try_get_context("env")
if not env_name:
    raise ValueError(
        "env context が必要です。例: cdk deploy -c env=develop"
    )

# ===== 環境別 .env ファイルの読み込み =====
# .env.<env_name> は backend/ ルートに置く (gitignore 済)
backend_root = Path(__file__).parent.parent
env_path = backend_root / f".env.{env_name}"

if not env_path.exists():
    raise FileNotFoundError(
        f"{env_path} が存在しません。.env.example を参考に作成してください。"
    )

env_vars = {k: v for k, v in dotenv_values(env_path).items() if v}

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
    env=cdk.Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"),
        region=os.getenv("CDK_DEFAULT_REGION", "us-east-1"),
    ),
)

app.synth()
