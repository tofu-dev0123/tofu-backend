---
name: implement
description: Issue 番号を受け取り、実装計画の提示 → 承認 → 実装 → テスト → code-reviewer agent によるレビュー → 指摘修正 → develop 向け PR 作成までを一気通貫で行うスキル。「Issue #N を実装して」「/implement N」「この Issue に着手」などと言われたときは必ずこのスキルを使う。
argument-hint: <Issue番号>
---

Issue `#$ARGUMENTS` を実装し、PR を作成するまでを行う。
フロー全体は `.claude/rules/dev-flow.md` を参照。
このスキルの実行は、手順内のコミット・push・PR 作成・Issue へのコメント/ラベル操作をユーザーが依頼したものとして扱う。

## 1. Issue の確認

- `$ARGUMENTS` が空なら Issue 番号を確認する
- `gh issue view <番号> --comments --json number,title,body,labels,state,comments` で内容を取得する
  - クローズ済みなら停止して報告する
  - 既に `<!-- claude:plan -->` を含むコメントがあれば、承認済みの計画として扱い、再開か再計画かをユーザーに確認する
- `git status --porcelain` で作業ツリーを確認し、未コミットの変更があれば停止して報告する

## 2. 実装計画の提示 ⏸

既存コードを読み、以下を含む実装計画を提示する。

- 変更内容（ファイル単位、レイヤー別）
- 追加・修正するテスト
- 既存 API 仕様・データモデルへの影響（あれば明示。CLAUDE.md により事前確認が必須）
- コミットの分け方（1 コミット 1 論理変更）
- Issue から判断を補った点・未決事項

**ユーザーの承認を得るまで実装に着手しない。** 修正を求められたら計画を直して再提示する。

## 3. 計画の記録とブランチ作成

承認後に以下を行う。

1. 承認された計画を Issue にコメントする（本文の先頭行に `<!-- claude:plan -->` を入れる）

   ```bash
   gh issue comment <番号> --body-file <一時ファイル>
   gh issue edit <番号> --add-label "status:in-progress"
   ```

2. develop を最新化してブランチを作成する

   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b "feature/issue#<番号>"
   ```

   - 既にブランチが存在する場合は `git checkout "feature/issue#<番号>"` で再開する

## 4. 実装

- 計画に沿って実装する。**計画にない変更（無関係なリファクタ等）はしない**
- 規約: `.claude/rules/coding-guidelines.md` / `architecture.md` / `logging-guidelines.md` / `testing-guidelines.md`
- 実装中に計画の変更が必要になったら、作業を止めてユーザーに確認する
- 論理的なまとまりごとにコミットする
  - `git add <対象ファイル>` で必要なファイルだけをステージする（`git add -A` は使わない）
  - メッセージは日本語で `feat:` / `fix:` / `refactor:` / `test:` / `docs:` / `chore:` などのプレフィックスを付ける
  - `Co-Authored-By` 行は付けない

## 5. テスト

```bash
scripts/check.sh
```

- pyright と Docker 上の pytest を実行し、成功すると HEAD の sha を `.claude/.last-check` に記録する
- 未コミットの変更があると記録されないため、コミット後に実行する
- 失敗したら原因を調べて修正・コミットし、再実行する
- `git push` / `gh pr create` は、HEAD で check.sh が成功していないと hook でブロックされる
  - hook はコマンド実行前に判定するため、`scripts/check.sh && git push` のように 1 コマンドにまとめるとブロックされる。**check.sh と push / PR 作成は別々のコマンドで実行する**

## 6. レビュー（code-reviewer agent）

1. Agent ツールで `code-reviewer` エージェントを呼び出す。プロンプトには以下を渡す
   - Issue 番号と承認済み計画
   - レビュー対象: `git diff develop...HEAD`
   - 2 回目以降は前回の指摘と対応内容
2. 指摘への対応
   - `must` / `should`: 修正してコミットする。対応しない場合は理由を記録する
   - `nit`: 妥当なものだけ対応する
3. 修正したら手順 5（テスト）→ 手順 6（レビュー）を繰り返す
   - **最大 3 回**で打ち切る。残った指摘は PR 本文の「未対応事項」に記載する
4. 判定が `APPROVE`、または上限に達したら次へ進む

## 7. PR 作成

1. 最終状態で `scripts/check.sh` が成功していることを確認する（hook でも確認される）
2. `.github/pull_request_template.md` の見出し構成に沿って本文を作成する（`<!-- -->` コメントは除く）
   - `Closes #<番号>` を必ず含める
   - 「レビュー結果」に code-reviewer の指摘と対応状況、「未対応事項」に残った指摘を書く
   - `🤖 Generated with Claude Code` などの生成フッターは付けない
3. push して PR を作成する

   ```bash
   git push -u origin "feature/issue#<番号>"
   gh pr create --base develop --title "<タイトル>" --body-file <一時ファイル>
   gh issue edit <番号> --remove-label "status:in-progress" --add-label "status:review"
   ```

4. PR の URL を表示し、マージ後は `/cleanup <番号>` を実行するよう案内する
