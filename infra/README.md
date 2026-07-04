# infra/ — 本番インフラ (Lightsail VPS)

Issue #74「Lambda → Lightsail VPS 移行」の生 CloudFormation 定義と起動スクリプト群。
CDK は #75 で全廃予定。**現状は雛形（TODO 多数）**であり、実デプロイ前に各値の確定が必要。

## 構成

| ファイル | 役割 |
|---|---|
| `cloudformation/cfn-tofu-lightsail.yaml` | Lightsail インスタンス + 静的IP の CloudFormation (S3用 IAM は既存・管理外) |
| `bootstrap.sh` | 初回起動プロビジョニング (Docker / cloudflared / sshd 締め / アプリ配置) |
| `docker-compose.production.yml` | 本番実行構成 (api = GHCR イメージ + Caddy) |
| `Caddyfile` | 443 終端 → `api:8000` リバースプロキシ (Cloudflare Origin Cert) |

リソース名・タグは `ProjectPrefix`(既定 `tofu`) + `EnvName`(既定 `prod`) で統一し、
コンソール上でどのアプリのスタックか識別できるようにしている。

## アーキテクチャ

```
client → Cloudflare(orange) → Lightsail:443 [Caddy + Origin Cert] → uvicorn(FastAPI):8000
                                    └ cloudflared 常駐 = SSH 専用トンネル (22番は閉鎖)
DB: Neon(外部) / 画像: S3 + CloudFront (据え置き) / secrets: .env.production 直置き
```

## デプロイ手順 (雛形段階のイメージ)

前提: 東京リージョン。CLI から実行 (変更頻度が低いため CI 管理外)。

```bash
# 1. インフラ (Lightsail + IAM) を作成
aws cloudformation deploy \
  --region ap-northeast-1 \
  --template-file infra/cloudformation/cfn-tofu-lightsail.yaml \
  --stack-name tofu-infra-prod \
  --capabilities CAPABILITY_NAMED_IAM

# 2. 出力 (静的IP / IAM ユーザー名) を確認
aws cloudformation describe-stacks --region ap-northeast-1 \
  --stack-name tofu-infra-prod --query 'Stacks[0].Outputs'
```

## 手動で投入するもの (CFN / repo に載せない秘密)

| 項目 | 投入先 | 備考 |
|---|---|---|
| Cloudflare Tunnel トークン | box: `cloudflared service install <token>` | Cloudflare 側で Tunnel/Public Hostname(SSH)/Access を先に設定 |
| デプロイ用 SSH 公開鍵 | box: `deploy` ユーザーの `authorized_keys` | 秘密鍵は GitHub Secrets `SSH_PRIVATE_KEY` |
| GHCR PAT | box: `docker login ghcr.io` | `docker compose pull` 用 |
| IAM アクセスキー | box: `.env.production` | **既存**の S3 画像アップロード用 IAM ユーザー(管理外)で発行 |
| `.env.production` | box: `/srv/app/.env.production` (600) | 手動 scp (22 閉鎖のため Tunnel 経由) |
| Cloudflare Origin Cert | box: `/srv/app/certs/origin.pem` + `origin-key.pem` | Cloudflare で発行、Full (strict) |

### `.env.production` に入れる主な値

`DATABASE_URL`(Neon main) / `SECRET_KEY`(JWT) / `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` /
`AWS_DEFAULT_REGION=ap-northeast-1` / `S3_BUCKET_NAME=tofu-blog-image-prod` / `S3_REGION=ap-northeast-1` /
`CLOUDFRONT_DOMAIN` / `CORS_ALLOW_ORIGINS` / `APP_ENV=production`
（`*_SSM` 系は設定しない = SSM 取得を無効化。詳細は `app/core/config.py`）

## TODO (実デプロイ前に確定)

- [ ] `BundleId` / `BlueprintId` を `aws lightsail get-bundles|get-blueprints` で確定
- [ ] Cloudflare IP レンジ (v4/v6) を公式リストで最新化
- [ ] `cloudformation/cfn-tofu-lightsail.yaml` の `UserData` と `bootstrap.sh` を同期
- [ ] Cloudflare Tunnel / Access / Public Hostname(SSH) の設定
- [ ] Origin Certificate 発行・配置、Cloudflare SSL を Full (strict) に

## 後続フェーズ (本タスク=雛形のスコープ外)

- アプリ改修: Mangum 剥がし (`app/main.py` の `handler`、`requirements.txt`)
- CI/CD 刷新: GHCR build/push + Tunnel 経由 SSH deploy + マイグレ分離 workflow
- カットオーバー (DNS 切替) → #75 で旧 CDK/Lambda/CloudFront/ACM/SSM 撤去
