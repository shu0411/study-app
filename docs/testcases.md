# テストケース仕様書（testcases.md）

## 対象フェーズ

MVP（Phase1）

## ステータス

承認待ち

## 前提

- ベースURL: `/api/v1/`
- 認証: JWT（Bearer トークン）
- テストフレームワーク: pytest + pytest-django
- 正常系: 期待通りの入力・操作
- 異常系: 不正入力・権限違反・存在しないリソース等

---

## 1. 認証（Auth）

### TC-AUTH-001: 子どもアカウント登録（正常系）

- **対象**: `POST /auth/register/child/`
- **入力**:

  ```json
  {
    "username": "taro123",
    "email": "taro@example.com",
    "password": "Pass1234",
    "nickname": "たろう",
    "grade": 3
  }
  ```

- **期待結果**: HTTP 201、`id`・`role: "child"` を含むレスポンス
- **確認事項**: DBに User（role=child）と ChildProfile が作成される

---

### TC-AUTH-002: 保護者アカウント登録（正常系）

- **対象**: `POST /auth/register/parent/`
- **入力**:

  ```json
  {
    "username": "parent01",
    "email": "parent@example.com",
    "password": "Pass1234",
    "display_name": "田中 花子"
  }
  ```

- **期待結果**: HTTP 201、`role: "parent"` を含むレスポンス
- **確認事項**: DBに User（role=parent）と ParentProfile が作成される

---

### TC-AUTH-003: ログイン（正常系）

- **対象**: `POST /auth/login/`
- **入力**: `{ "username": "taro123", "password": "Pass1234" }`
- **期待結果**: HTTP 200、`access` と `refresh` トークンを返す

---

### TC-AUTH-004: アクセストークン更新（正常系）

- **対象**: `POST /auth/token/refresh/`
- **入力**: `{ "refresh": "<valid_refresh_token>" }`
- **期待結果**: HTTP 200、新しい `access` トークンを返す
- **確認事項**: 古い refresh トークンは無効化される（ローテーション）

---

### TC-AUTH-005: ログアウト（正常系）

- **対象**: `POST /auth/logout/`
- **入力**: `{ "refresh": "<valid_refresh_token>" }` + Bearerトークン
- **期待結果**: HTTP 204
- **確認事項**: logout後にその refresh トークンで更新するとHTTP 401

---

### TC-AUTH-006: 重複 username で登録（異常系）

- **対象**: `POST /auth/register/child/`
- **入力**: 既存の username を指定
- **期待結果**: HTTP 400、エラーメッセージに `username` フィールドのエラーを含む

---

### TC-AUTH-007: パスワード不正で登録（異常系）

- **対象**: `POST /auth/register/child/`
- **入力**: `"password": "abc"` （7文字・数字なし）
- **期待結果**: HTTP 400、パスワードバリデーションエラー

---

### TC-AUTH-008: 誤ったパスワードでログイン（異常系）

- **対象**: `POST /auth/login/`
- **入力**: 正しい username・誤った password
- **期待結果**: HTTP 401

---

### TC-AUTH-009: 期限切れ refresh トークンで更新（異常系）

- **対象**: `POST /auth/token/refresh/`
- **期待結果**: HTTP 401

---

### TC-AUTH-010: username バリデーション（異常系）

- **対象**: `POST /auth/register/child/`
- 2文字以下 → HTTP 400
- 31文字以上 → HTTP 400
- 記号含む（例: `ta ro!`） → HTTP 400

---

## 2. ユーザー情報（Users）

### TC-USER-001: 自分のプロフィール取得・子ども（正常系）

- **対象**: `GET /users/me/`
- **認証**: child の access トークン
- **期待結果**: HTTP 200、`nickname`・`grade`・`avatar`・`role: "child"` を含む

---

### TC-USER-002: 自分のプロフィール取得・保護者（正常系）

- **対象**: `GET /users/me/`
- **認証**: parent の access トークン
- **期待結果**: HTTP 200、`display_name`・`role: "parent"` を含む

---

### TC-USER-003: プロフィール更新（正常系）

- **対象**: `PATCH /users/me/`
- **認証**: child の access トークン
- **入力**: `{ "nickname": "けんた", "grade": 4 }`
- **期待結果**: HTTP 200、更新後の値を返す
- **確認事項**: DBの ChildProfile が更新される

---

### TC-USER-004: 認証なしでプロフィール取得（異常系）

- **対象**: `GET /users/me/`
- **認証**: なし
- **期待結果**: HTTP 401

---

### TC-USER-005: grade に範囲外の値を設定（異常系）

- **対象**: `PATCH /users/me/`
- **入力**: `{ "grade": 0 }` / `{ "grade": 10 }`
- **期待結果**: HTTP 400

---

## 3. 保護者↔子ども紐付け（ParentChild）

### TC-PC-001: 子ども一覧取得（正常系）

- **対象**: `GET /parents/me/children/`
- **前提**: 保護者に2人の子どもが紐付き済み
- **認証**: parent の access トークン
- **期待結果**: HTTP 200、2件のリストを返す

---

### TC-PC-002: 子どもを紐付け（正常系）

- **対象**: `POST /parents/me/children/`
- **入力**: `{ "child_id": "<child_user_id>" }`
- **期待結果**: HTTP 201、ParentChildRelation が作成される

---

### TC-PC-003: 紐付け解除（正常系）

- **対象**: `DELETE /parents/me/children/{child_id}/`
- **期待結果**: HTTP 204、DBから対象の ParentChildRelation が削除される

---

### TC-PC-004: 子どもロールのユーザーが子ども一覧を取得（異常系）

- **対象**: `GET /parents/me/children/`
- **認証**: child の access トークン
- **期待結果**: HTTP 403

---

### TC-PC-005: 既に紐付き済みの子どもを再度紐付け（異常系）

- **対象**: `POST /parents/me/children/`
- **期待結果**: HTTP 400、重複エラー

---

### TC-PC-006: 存在しない child_id で紐付け（異常系）

- **対象**: `POST /parents/me/children/`
- **入力**: `{ "child_id": "<存在しないUUID>" }`
- **期待結果**: HTTP 404

---

### TC-PC-007: 他の保護者の紐付けを解除しようとする（異常系）

- **対象**: `DELETE /parents/me/children/{child_id}/`
- **前提**: child_id は自分ではない別の保護者が紐付けている子ども
- **期待結果**: HTTP 404（自分のリレーションに存在しないため）

---

## 4. クイズ（Quiz）

### TC-QUIZ-001: 教科一覧取得（正常系）

- **対象**: `GET /quiz/subjects/`
- **認証**: child の access トークン
- **期待結果**: HTTP 200、`id`・`name`・`order` のリスト（order 昇順）

---

### TC-QUIZ-002: 単元一覧取得（正常系）

- **対象**: `GET /quiz/subjects/{id}/units/`
- **期待結果**: HTTP 200、対象教科に属する Unit のリスト

---

### TC-QUIZ-003: 小単元一覧取得（正常系）

- **対象**: `GET /quiz/units/{id}/topics/`
- **期待結果**: HTTP 200、対象単元に属する Topic のリスト（`target_grade` 含む）

---

### TC-QUIZ-004: 問題一覧取得（正常系）

- **対象**: `GET /quiz/topics/{id}/questions/`
- **期待結果**: HTTP 200、`id`・`body`・`question_type`・`difficulty` のリスト（選択肢は含まない）

---

### TC-QUIZ-005: 問題詳細取得（正常系）

- **対象**: `GET /quiz/questions/{id}/`
- **期待結果**: HTTP 200、問題情報 + `choices`（`id`・`body`・`order`）を返す
- **確認事項**: `is_correct` はレスポンスに含まない（解答前に正解を返さない）

---

### TC-QUIZ-006: 存在しない教科IDで単元一覧取得（異常系）

- **対象**: `GET /quiz/subjects/{id}/units/`
- **入力**: 存在しない UUID
- **期待結果**: HTTP 404

---

### TC-QUIZ-007: 認証なしでクイズ取得（異常系）

- **対象**: `GET /quiz/subjects/`
- **期待結果**: HTTP 401

---

## 5. 解答・進捗（Progress）

### TC-PROG-001: 解答送信・正解（正常系）

- **対象**: `POST /progress/answers/`
- **認証**: child の access トークン
- **入力**:

  ```json
  {
    "question_id": "<uuid>",
    "selected_choice_id": "<正解のchoice_uuid>"
  }
  ```

- **期待結果**: HTTP 201、`{ "is_correct": true }` を含むレスポンス
- **確認事項**: AnswerHistory に `is_correct=True` のレコードが作成される

---

### TC-PROG-002: 解答送信・不正解（正常系）

- **対象**: `POST /progress/answers/`
- **入力**: 不正解の choice_id を指定
- **期待結果**: HTTP 201、`{ "is_correct": false }` を含むレスポンス

---

### TC-PROG-003: 同じ問題を再解答（正常系）

- **対象**: `POST /progress/answers/`
- **前提**: 同じ問題に既に解答済み
- **期待結果**: HTTP 201、新規レコードが追加される（上書きではない）

---

### TC-PROG-004: 自分の学習サマリー取得（正常系）

- **対象**: `GET /progress/summary/`
- **認証**: child の access トークン
- **期待結果**: HTTP 200、教科別の `total`・`correct`・`accuracy_rate` を含むリスト

---

### TC-PROG-005: 保護者が子どもの学習サマリー取得（正常系）

- **対象**: `GET /progress/children/{child_id}/summary/`
- **認証**: parent の access トークン（対象の子どもと紐付き済み）
- **期待結果**: HTTP 200、子どもの教科別サマリーを返す

---

### TC-PROG-006: 別の問題の選択肢IDを使って解答（異常系）

- **対象**: `POST /progress/answers/`
- **入力**: `question_id` と無関係な `selected_choice_id`
- **期待結果**: HTTP 400、バリデーションエラー

---

### TC-PROG-007: 存在しない question_id で解答（異常系）

- **対象**: `POST /progress/answers/`
- **期待結果**: HTTP 404

---

### TC-PROG-008: 保護者ロールが解答送信（異常系）

- **対象**: `POST /progress/answers/`
- **認証**: parent の access トークン
- **期待結果**: HTTP 403

---

### TC-PROG-009: 子どもロールが別の子どものサマリーを取得（異常系）

- **対象**: `GET /progress/children/{child_id}/summary/`
- **認証**: child の access トークン
- **期待結果**: HTTP 403

---

### TC-PROG-010: 紐付けのない子どものサマリーを保護者が取得（異常系）

- **対象**: `GET /progress/children/{child_id}/summary/`
- **認証**: parent の access トークン（対象の子どもと紐付きなし）
- **期待結果**: HTTP 404

---

## 6. 横断テスト観点

### TC-CROSS-001: 期限切れ access トークンでのリクエスト

- **対象**: 認証必須の任意のエンドポイント
- **期待結果**: HTTP 401

---

### TC-CROSS-002: 不正な形式の Bearer トークン

- **対象**: 認証必須の任意のエンドポイント
- **入力**: `Authorization: Bearer invalidtoken`
- **期待結果**: HTTP 401

---

### TC-CROSS-003: UUID形式でないIDをパスパラメータに指定

- **対象**: `GET /quiz/subjects/{id}/units/` 等
- **入力**: `id = "abc"`
- **期待結果**: HTTP 404 または HTTP 400

---

### TC-CROSS-004: 全エンドポイントで OPTIONS メソッド（CORS プリフライト）

- **期待結果**: HTTP 200、適切な CORS ヘッダーを返す（フロントエンドのオリジンを許可）
