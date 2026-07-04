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
                                    └ cloudflared 常駐 = CI デプロイ用 SSH トンネル (localhost:22)
DB: Neon(外部) / 画像: S3 + CloudFront (据え置き) / secrets: .env.production 直置き
```

### 箱への接続方法 (22番はインターネット非公開)

| 用途 | 方法 |
|---|---|
| 管理・初回セットアップ (対話操作) | **Lightsail コンソールのブラウザ SSH**。FW は 22 を `lightsail-connect` にのみ許可しているため、AWS ログイン経由で接続できる |
| CI の自動デプロイ | **Cloudflare Tunnel**。cloudflared が箱内の `localhost:22` に繋ぐ (FW とは無関係) |
| 手元からの scp 等 (任意) | Tunnel 経由: `ssh/scp ... -o ProxyCommand="cloudflared access ssh --hostname ssh.api.tofubase.com"` (Access に自分の email 許可が必要) |

## PART 0: Cloudflare 事前設定 (Zero Trust)

CFN デプロイや PART 2 の前に、Cloudflare 側を用意する。無料の Zero Trust プランで足りる。

1. **Tunnel 作成** — Zero Trust → Networks → Tunnels → Create a tunnel (Cloudflared 型)。
   名前例 `tofu-prod`。発行される**接続トークン**を控える (PART 2 (a) で使用・秘密)。
2. **Public Hostname 追加** — その Tunnel に:
   - Subdomain `ssh` / Domain `api.tofubase.com` (→ `ssh.api.tofubase.com`)
   - Type: **SSH** / URL: `localhost:22`
3. **Access アプリ (self-hosted)** — Access → Applications → Add:
   - Application domain: `ssh.api.tofubase.com`
4. **サービストークン発行** (CI 用) — Access → Service Auth → Create Service Token。
   Client ID/Secret を GitHub Environment `prod` の `CF_ACCESS_CLIENT_ID` / `CF_ACCESS_CLIENT_SECRET` へ。
5. **Access ポリシー** — 上記アプリに:
   - Service Auth: 発行したサービストークンを許可 (CI 用)
   - Allow: 自分の email を許可 (自分の対話 SSH / scp 用)
6. **Origin Certificate 発行** — SSL/TLS → Origin Server → Create Certificate (`api.tofubase.com`)。
   pem/key を box の `/srv/app/certs/origin.pem` / `origin-key.pem` に配置 (PART 2 (d))。
7. **SSL/TLS モード** を **Full (strict)** に設定。
8. **DNS (カットオーバー時に切替)** — `api.tofubase.com` を A レコード = Lightsail 静的IP、**orange (proxied)** に。
   ※ 切替は旧構成を残したまま行う (詳細は #75 / カットオーバー手順)。

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

## PART 3: DB マイグレーション (Neon main)

deploy とは分離済み。GitHub Actions の **`Migrate DB` ワークフローを手動実行** (environment=`prod`) する。
`prod` の承認ゲートを通ると `alembic upgrade head` が Neon main に適用される。

- Actions → `Migrate DB` → Run workflow → environment: `prod`
- 前提: GitHub Environment `prod` に `DATABASE_URL` (Neon main の pooled URL) を登録済み
- カットオーバー窓では**後方互換 (expand) のみ**適用し、破壊的変更は撤去後に回す

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
- [ ] PART 0 (Cloudflare Tunnel / Access / Origin Cert / Full strict) を実施
- [ ] GitHub Environment `prod`/`dev` に Secrets を登録 (SSH_PRIVATE_KEY / CF_ACCESS_* / DATABASE_URL)

## 実行順序 (まとめ)

1. PART 0: Cloudflare 事前設定
2. CFN デプロイ (Lightsail Instance + StaticIp、UserData 自動プロビジョニング)
3. PART 2: 起動後の手動手順 (ブラウザ SSH でトンネル常駐・鍵配置・資材配置・起動)
4. PART 3: DB マイグレーション (Migrate DB ワークフロー, env=prod)
5. カットオーバー (DNS を Lightsail に切替) → #75 で旧 CDK/Lambda/CloudFront/ACM/SSM 撤去
