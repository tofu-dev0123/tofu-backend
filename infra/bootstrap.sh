#!/bin/bash
# =============================================================================
# Lightsail 初回起動プロビジョニングスクリプト (UserData 相当)
# -----------------------------------------------------------------------------
# 役割:
#   - Docker / docker compose plugin 導入
#   - cloudflared 導入 (Cloudflare Tunnel = SSH 経路。22番は開けない)
#   - デプロイ用ユーザー / sshd ハードニング
#   - アプリ配置ディレクトリ準備
#
# 秘密の扱い (このスクリプトに直書きしない):
#   - TUNNEL_TOKEN     : Cloudflare Tunnel 接続トークン
#   - GHCR_PAT         : GHCR pull 用の PAT
#   - .env.production  : DB/JWT/S3 の秘密 (手動 scp)
#   - deploy 公開鍵     : authorized_keys へ
#   詳細は infra/README.md を参照。
#
# ※ 雛形: TODO を埋めて確定する。lightsail.yaml の UserData と同期すること。
# =============================================================================
set -euo pipefail

APP_DIR=/srv/app
DEPLOY_USER=deploy

# ---------------------------------------------------------------------------
# 1. Docker + compose plugin
# ---------------------------------------------------------------------------
if ! command -v docker >/dev/null 2>&1; then
  curl -fsSL https://get.docker.com | sh
fi
# docker compose (v2, plugin) は get.docker.com で同梱される想定

# ---------------------------------------------------------------------------
# 2. cloudflared (ARM64) -> Cloudflare Tunnel を systemd 常駐
#    22番は開けず、Tunnel 経由の SSH のみ許可する (方針B)
# ---------------------------------------------------------------------------
if ! command -v cloudflared >/dev/null 2>&1; then
  curl -fsSL -o /tmp/cloudflared.deb \
    https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64.deb
  dpkg -i /tmp/cloudflared.deb
  rm -f /tmp/cloudflared.deb
fi

# TODO: 接続トークンは秘密。UserData 直書きを避け、初回に手動で以下を実行する:
#   sudo cloudflared service install <TUNNEL_TOKEN>
# (Cloudflare 側で Tunnel / Public Hostname(SSH->localhost:22) / Access を設定済みが前提)

# ---------------------------------------------------------------------------
# 3. デプロイ用ユーザーと SSH 鍵
# ---------------------------------------------------------------------------
if ! id "${DEPLOY_USER}" >/dev/null 2>&1; then
  useradd -m -s /bin/bash "${DEPLOY_USER}"
  usermod -aG docker "${DEPLOY_USER}"
fi
install -d -m 700 -o "${DEPLOY_USER}" -g "${DEPLOY_USER}" "/home/${DEPLOY_USER}/.ssh"
# TODO: デプロイ用公開鍵を配置する (GitHub Secrets の SSH_PRIVATE_KEY と対):
#   echo "<DEPLOY_PUBLIC_KEY>" > /home/${DEPLOY_USER}/.ssh/authorized_keys
#   chmod 600 /home/${DEPLOY_USER}/.ssh/authorized_keys
#   chown ${DEPLOY_USER}:${DEPLOY_USER} /home/${DEPLOY_USER}/.ssh/authorized_keys

# ---------------------------------------------------------------------------
# 4. sshd ハードニング (鍵認証のみ)
# ---------------------------------------------------------------------------
sshd_config=/etc/ssh/sshd_config
sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' "${sshd_config}"
sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' "${sshd_config}"
systemctl reload ssh || systemctl reload sshd || true

# ---------------------------------------------------------------------------
# 5. アプリ配置ディレクトリ
#    docker-compose.production.yml / Caddyfile / .env.production / Origin Cert を配置する場所。
#    配布は CI (SSH デプロイ) or 手動 scp。
# ---------------------------------------------------------------------------
install -d -m 750 -o "${DEPLOY_USER}" -g "${DEPLOY_USER}" "${APP_DIR}"
install -d -m 750 -o "${DEPLOY_USER}" -g "${DEPLOY_USER}" "${APP_DIR}/certs"

# TODO: GHCR ログイン (docker compose pull 用)。PAT は手動投入する:
#   echo "<GHCR_PAT>" | docker login ghcr.io -u <github_user> --password-stdin

echo "[bootstrap] done. 次の手動作業は infra/README.md を参照。"
