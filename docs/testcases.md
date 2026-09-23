# テストケース仕様書（testcases.md）

## 対象フェーズ

MVP（Phase1）

## ステータス

承認待ち

「7. バックエンドの uv 移行」は承認済み。既存の API テストケースは変更しない。

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

---

## 7. バックエンドの uv 移行

### ステータス・前提

テストケース承認済み（2026-09-23）。対応仕様は [バックエンド仕様書の第9節](spec.md#9-バックエンドの-uv-移行)。
以下は環境構築・コマンド実行による受け入れ検証とし、API の回帰検証には既存の pytest を使用する。
変更前の依存一覧と既存テスト・pylint の結果を記録し、変更後と比較する。
検証時のエラーは、依存関係取得などの環境要因と設定・アプリの問題を区別する。

### TC-UV-001: ロックファイルに基づく開発環境の構築

- **操作**: `backend/` で `uv sync --locked` を実行する。
- **期待結果**: 成功し、`backend/.venv` に Python 3.12 系の環境が作成される。仕様で定めた実行用・開発用の依存が利用できる。
- **確認事項**: 直接依存のバージョンが移行前と一致する。推移的依存の差分があれば理由とともに記録する。再実行してもロックファイルに差分が発生しない。仮想環境は Git 管理対象外である。

### TC-UV-002: 実行用の依存関係のみの環境構築

- **操作**: 開発環境とは別の一時仮想環境を `UV_PROJECT_ENVIRONMENT` で指定し、`backend/` で `uv sync --locked --no-dev` を実行する。
- **期待結果**: 成功し、実行用の依存をインポートできる。pytest・pytest-django・pylint はインストールされない。
- **確認事項**: インストール内容は一時環境の Python で確認する。通常の `uv run` による開発用依存の再同期を避ける。

### TC-UV-003: Django 管理コマンドの実行

- **操作**: `backend/study_app_backend/` で `uv run --locked python manage.py check` と `uv run --locked python manage.py migrate --plan` を実行する。
- **期待結果**: 両方が成功し、Django 設定・アプリ・マイグレーションを読み込める。
- **確認事項**: 親ディレクトリの uv プロジェクトと仮想環境を使用する。

### TC-UV-004: 既存 API テストと静的解析の実行

- **操作**: `backend/study_app_backend/` で `uv run --locked pytest` と `uv run --locked pylint apps study_app_backend tests manage.py` を実行する。
- **期待結果**: 既存テストがすべて成功し、既存の `.pylintrc` に従って静的解析が実行される。移行に起因する新たな指摘がない。
- **確認事項**: 既存の失敗・警告・静的解析の指摘がある場合は変更前との比較を記録し、未解決事項として報告する。

### TC-UV-005: ロックファイルの不整合検出

- **操作**: 一時ディレクトリに移行後の uv 管理ファイルをコピーし、直接依存のバージョン指定をロック済みバージョンと矛盾する値に変更して `uv sync --locked` を実行する。
- **期待結果**: ロックファイルの更新が必要なため失敗し、ロックファイルを自動更新しない。
- **確認事項**: リポジトリ内の管理ファイル・開発環境は変更しない。

### TC-UV-006: 開発手順と依存関係の管理元の確認

- **操作**: README のバックエンド手順・構成図を管理ファイルと照合する。記載した起動コマンドで開発サーバーを一時的に起動し、起動確認後に停止する。
- **期待結果**: セットアップ・起動・テスト・静的解析の作業ディレクトリとコマンドが実際の配置に一致する。サーバーが正常に起動する。
- **確認事項**: `requirements.txt` は削除され、依存の定義元が `pyproject.toml` に統一されている。README に旧 pip 導入手順が残っていない。

### uv 移行の検証結果

実施日: 2026-09-23。環境: Linux、uv 0.11.32、Python 3.12.13。

設定変更前に `uv sync --locked` が `pyproject.toml` 不在で失敗することを確認した。
アプリコードの追加・変更はなく、承認済みのコマンド検証と既存 API テストで移行を確認した。

| ケース | 結果 |
| --- | --- |
| TC-UV-001 | 成功。開発環境を構築でき、再同期でもロックファイルの内容は不変。`.venv` が Git 管理対象外であることを確認。 |
| TC-UV-002 | 成功。一時環境で実行用依存のインポートと Python 3.12 を確認。pytest・pytest-django・pylint は未導入。 |
| TC-UV-003 | 成功。Django システムチェックは指摘なし。マイグレーション計画を取得できた。 |
| TC-UV-004 | 移行前後とも API テスト 49 件成功。pylint の出力は移行前後で完全一致。既存の指摘による失敗は下記参照。 |
| TC-UV-005 | 成功。一時コピーの Django 指定を変更すると `--locked` が更新必要エラーで終了し、ロックファイルを保持した。 |
| TC-UV-006 | 成功。README と配置を照合し、旧 pip 手順と `requirements.txt` を削除。開発サーバーを一時ポート・自動再起動なしで起動し、未認証の API リクエストへの HTTP 401 応答を確認後、停止した。 |

依存バージョンは推移的依存を含め全 22 件を維持した。
Linux の開発環境へのインストールは 20 件。`colorama` と `tzdata` は依存元の Windows 条件に従い、ロックには残るが Linux では導入されない。

既存の未解決事項:

- pylint は移行前後とも終了コード 30、評価 6.73/10。Django モデルの `objects` の検出、抽象メソッド、長い行、インポート位置などの指摘が残る。比較ではキャッシュ書き込みを避けるため `--persistent=n` を付けた。
- 開発 DB はマイグレーション未適用で、起動時に警告が出る。DB 更新はこの検証では行っていない。通常の初回起動では README の `migrate` 手順を実行する。

仕様との照合レビューでは API・DB モデル・アプリ実装の変更がないことを確認した。成果物の人間承認は未実施。
