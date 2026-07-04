# infra/ — 本番インフラ (Lightsail VPS)

Issue #74「Lambda → Lightsail VPS 移行」の生 CloudFormation 定義一式。
CDK は #75 で全廃予定。**現状は雛形（TODO 多数）**であり、実デプロイ前に各値の確定が必要。

## 構成

| ファイル | 役割 |
|---|---|
| `cloudformation/cfn-tofu-lightsail.yaml` | Lightsail インスタンス + 静的IP の CloudFormation (S3用 IAM は既存・管理外)。初回プロビジョニングは `UserData` に直書き |
| `docker-compose.production.yml` | 本番実行構成 (api = GHCR イメージ + Caddy) |
| `Caddyfile` | 443 終端 → `api:8000` リバースプロキシ (Cloudflare Origin Cert) |

初回ブート時の自動プロビジョニング (Docker / cloudflared バイナリ / deploy ユーザー / sshd 締め /
アプリ配置ディレクトリ / 自動更新) は `cfn-tofu-lightsail.yaml` の `UserData` に記述している。
秘密が必要な処理は自動化せず、下記「PART 2: 起動後の手動手順」で行う。

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
# 1. インフラ (Lightsail Instance + StaticIp) を作成
#    ※ UserData の自動プロビジョニングが初回ブートで走る
aws cloudformation deploy \
  --region ap-northeast-1 \
  --template-file infra/cloudformation/cfn-tofu-lightsail.yaml \
  --stack-name tofu-infra-prod

# 2. 出力 (静的IP / インスタンス名) を確認
aws cloudformation describe-stacks --region ap-northeast-1 \
  --stack-name tofu-infra-prod --query 'Stacks[0].Outputs'
```

## PART 2: 起動後の手動手順 (秘密が必要な処理)

UserData の自動プロビジョニング完了後に実施する。SSH は Cloudflare Tunnel 経由。
事前に Cloudflare 側で Tunnel / Public Hostname(SSH→localhost:22) / Access を設定しておく。

```bash
# (a) Cloudflare Tunnel を常駐させる (接続トークン)
sudo cloudflared service install <TUNNEL_TOKEN>

# (b) デプロイ用公開鍵を配置 (GitHub Secrets の SSH_PRIVATE_KEY と対)
echo "<DEPLOY_PUBLIC_KEY>" | sudo tee /home/deploy/.ssh/authorized_keys
sudo chmod 600 /home/deploy/.ssh/authorized_keys
sudo chown deploy:deploy /home/deploy/.ssh/authorized_keys

# (c) GHCR ログイン (docker compose pull 用)
echo "<GHCR_PAT>" | sudo -u deploy docker login ghcr.io -u <github_user> --password-stdin

# (d) アプリ資材を配置 (Tunnel 経由の scp)
#   /srv/app/docker-compose.production.yml
#   /srv/app/Caddyfile
#   /srv/app/.env.production          (chmod 600)
#   /srv/app/certs/origin.pem, origin-key.pem

# (e) 起動
cd /srv/app && sudo -u deploy docker compose -f docker-compose.production.yml up -d
```

### 手動で投入する秘密の一覧

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
- [ ] Cloudflare Tunnel / Access / Public Hostname(SSH) の設定
- [ ] Origin Certificate 発行・配置、Cloudflare SSL を Full (strict) に

## 後続フェーズ (本タスク=雛形のスコープ外)

- アプリ改修: Mangum 剥がし (`app/main.py` の `handler`、`requirements.txt`)
- CI/CD 刷新: GHCR build/push + Tunnel 経由 SSH deploy + マイグレ分離 workflow
- カットオーバー (DNS 切替) → #75 で旧 CDK/Lambda/CloudFront/ACM/SSM 撤去
