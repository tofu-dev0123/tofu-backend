---
name: cleanup
description: PR マージ後の後片付けを行うスキル。Issue 番号を受け取り、PR のマージと Issue のクローズを確認し、作業ブランチの削除・develop の同期・status ラベルの除去を行う。「マージした」「後片付け」「/cleanup N」「ブランチを消して」などと言われたときは必ずこのスキルを使う。
argument-hint: <Issue番号>
---

Issue `#$ARGUMENTS` のマージ後処理を行う。
フロー全体は `.claude/rules/dev-flow.md` を参照。

## 1. 状態の確認

```bash
BRANCH="feature/issue#<番号>"
gh pr list --head "$BRANCH" --state all --json number,state,mergedAt,url
gh issue view <番号> --json state,labels
git status --porcelain
```

- PR がマージされていなければ、状態（open / closed / 見つからない）を報告して停止する
- 未コミットの変更があれば報告して停止する

## 2. Issue のクローズ確認

- PR の `Closes #<番号>` で自動クローズされているはず
- open のままなら、マージ済み PR を添えてクローズする

  ```bash
  gh issue close <番号> --comment "<PR URL> のマージにより完了"
  ```

- `status:in-progress` / `status:review` ラベルが残っていれば除去する

  ```bash
  gh issue edit <番号> --remove-label "status:in-progress" --remove-label "status:review"
  ```

## 3. ブランチ削除と develop 同期

```bash
git checkout develop
git pull origin develop
git branch -d "$BRANCH"
git push origin --delete "$BRANCH"   # リモートに残っている場合のみ
git fetch --prune
```

- `git branch -d` が「未マージ」で失敗した場合は、squash マージ等が原因か確認したうえでユーザーに `-D` で削除してよいか確認する
- リモートブランチが既に削除済み（GitHub の自動削除）ならスキップする

## 4. 完了報告

実施した内容（Issue の状態・削除したブランチ・develop の最新コミット）を簡潔に表示する。
