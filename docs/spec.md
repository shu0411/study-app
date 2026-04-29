# バックエンド仕様書（spec.md）

## 対象フェーズ

MVP（Phase1）

## ステータス

承認待ち

---

## 1. 技術スタック

| 項目 | 採用技術 |
| --- | --- |
| 言語 | Python 3.12 |
| Webフレームワーク | Django 5.x |
| REST API | Django REST Framework (DRF) |
| 認証 | JWT（djangorestframework-simplejwt） |
| DB（初期） | SQLite |
| DB（将来） | PostgreSQL |

---

## 2. Djangoアプリ構成

```text
backend/study_app_backend/
├── study_app_backend/     # プロジェクト設定
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py / asgi.py
└── apps/
    ├── accounts/          # ユーザー・認証
    ├── quiz/              # 教科・単元・問題
    └── progress/          # 解答履歴・学習進捗
```

ストーリーモード（`apps/story/`）は Phase2 以降に追加。

---

## 3. DBモデル設計

### 3-1. accounts アプリ

#### User（カスタムユーザー）

Django 標準の `AbstractUser` を継承し、`role` フィールドで種別を管理する。
直接のログインは Child / Parent どちらのロールでも可能。

| フィールド | 型 | 説明 |
| --- | --- | --- |
| id | UUID | PK |
| username | str | ログインID（一意） |
| email | str | メールアドレス（一意） |
| password | str | ハッシュ済みパスワード |
| role | str(choice) | `child` / `parent` |
| created_at | datetime | 作成日時 |
| updated_at | datetime | 更新日時 |

#### ChildProfile

| フィールド | 型 | 説明 |
| --- | --- | --- |
| id | UUID | PK |
| user | OneToOne → User | role=child のUser |
| nickname | str | 表示名（ひらがな可） |
| grade | int | 学年（1〜9: 小1〜中3） |
| avatar | str | アバター識別子（初期は文字列コード） |
| created_at | datetime | 作成日時 |

#### ParentProfile

| フィールド | 型 | 説明 |
| --- | --- | --- |
| id | UUID | PK |
| user | OneToOne → User | role=parent のUser |
| display_name | str | 表示名 |
| created_at | datetime | 作成日時 |

#### ParentChildRelation

子ども1人に対して保護者を複数紐付け可能（Many-to-Many の中間テーブル）。

| フィールド | 型 | 説明 |
| --- | --- | --- |
| id | UUID | PK |
| parent | FK → ParentProfile | 保護者 |
| child | FK → ChildProfile | 子ども |
| created_at | datetime | 紐付け日時 |

制約: `(parent, child)` の複合ユニーク

---

### 3-2. quiz アプリ

クイズデータは管理者（Django Admin）が登録する。  
階層: **教科（Subject）> 単元（Unit）> 小単元（Topic）> 問題（Question）**

#### Subject（教科）

| フィールド | 型 | 説明 |
| --- | --- | --- |
| id | UUID | PK |
| name | str | 例: 算数、国語、理科、社会 |
| order | int | 表示順 |

#### Unit（単元）

| フィールド | 型 | 説明 |
| --- | --- | --- |
| id | UUID | PK |
| subject | FK → Subject | 所属教科 |
| name | str | 例: 計算、図形 |
| order | int | 教科内の表示順 |

#### Topic（小単元）

| フィールド | 型 | 説明 |
| --- | --- | --- |
| id | UUID | PK |
| unit | FK → Unit | 所属単元 |
| name | str | 例: 足し算、引き算 |
| order | int | 単元内の表示順 |
| target_grade | int | 対象学年（目安、1〜9） |

#### Question（問題）

| フィールド | 型 | 説明 |
| --- | --- | --- |
| id | UUID | PK |
| topic | FK → Topic | 所属小単元 |
| body | text | 問題文 |
| question_type | str(choice) | `single_choice`（MVP時点） |
| difficulty | int | 難易度（1: やさしい / 2: ふつう / 3: むずかしい） |
| explanation | text | 解説文（任意） |
| order | int | 小単元内の表示順 |

#### Choice（選択肢）

| フィールド | 型 | 説明 |
| --- | --- | --- |
| id | UUID | PK |
| question | FK → Question | 所属問題 |
| body | str | 選択肢テキスト |
| is_correct | bool | 正解フラグ |
| order | int | 選択肢の表示順 |

制約: 1問につき正解選択肢はちょうど1つ（`single_choice` の場合）

---

### 3-3. progress アプリ

#### AnswerHistory（解答履歴）

問題ごとに子どもの解答結果を記録する。

| フィールド | 型 | 説明 |
| --- | --- | --- |
| id | UUID | PK |
| child | FK → ChildProfile | 解答した子ども |
| question | FK → Question | 対象問題 |
| selected_choice | FK → Choice | 選んだ選択肢 |
| is_correct | bool | 正解・不正解 |
| answered_at | datetime | 解答日時 |

インデックス: `(child, question, answered_at)` ※再挑戦を許容するため同一問題の複数レコードを許可

---

## 4. APIエンドポイント設計

ベースURL: `/api/v1/`

### 4-1. 認証（accounts）

| メソッド | パス | 説明 | 認証要否 |
| --- | --- | --- | --- |
| POST | `/auth/register/child/` | 子どもアカウント新規登録 | 不要 |
| POST | `/auth/register/parent/` | 保護者アカウント新規登録 | 不要 |
| POST | `/auth/login/` | ログイン → JWT発行 | 不要 |
| POST | `/auth/token/refresh/` | アクセストークン更新 | 不要（refreshトークン必要） |
| POST | `/auth/logout/` | ログアウト（refreshトークン無効化） | 要 |

### 4-2. ユーザー情報（accounts）

| メソッド | パス | 説明 | 認証要否 |
| --- | --- | --- | --- |
| GET | `/users/me/` | 自分のプロフィール取得 | 要 |
| PATCH | `/users/me/` | 自分のプロフィール更新 | 要 |
| GET | `/parents/me/children/` | 自分の子ども一覧取得（保護者のみ） | 要（parent） |
| POST | `/parents/me/children/` | 子どもを保護者に紐付け | 要（parent） |
| DELETE | `/parents/me/children/{child_id}/` | 紐付け解除 | 要（parent） |

### 4-3. クイズ（quiz）

| メソッド | パス | 説明 | 認証要否 |
| --- | --- | --- | --- |
| GET | `/quiz/subjects/` | 教科一覧 | 要 |
| GET | `/quiz/subjects/{id}/units/` | 単元一覧（教科別） | 要 |
| GET | `/quiz/units/{id}/topics/` | 小単元一覧（単元別） | 要 |
| GET | `/quiz/topics/{id}/questions/` | 問題一覧（小単元別） | 要 |
| GET | `/quiz/questions/{id}/` | 問題詳細（選択肢含む） | 要 |

### 4-4. 解答・進捗（progress）

| メソッド | パス | 説明 | 認証要否 |
| --- | --- | --- | --- |
| POST | `/progress/answers/` | 解答送信・履歴記録 | 要（child） |
| GET | `/progress/summary/` | 自分の学習サマリー（教科別正答率） | 要（child） |
| GET | `/progress/children/{child_id}/summary/` | 子どもの学習サマリー（保護者のみ） | 要（parent） |

---

## 5. 認証フロー

```text
[クライアント]                    [API]
    |                               |
    |-- POST /auth/login/ --------->|
    |   { username, password }      |
    |<-- { access, refresh } -------|
    |                               |
    |-- GET /users/me/ ------------>|  Authorization: Bearer {access}
    |<-- { profile } ---------------|
    |                               |
    |-- POST /auth/token/refresh/ ->|  { refresh }
    |<-- { access } ----------------|
```

- アクセストークン有効期限: **60分**
- リフレッシュトークン有効期限: **7日**
- リフレッシュトークンはローテーション（使用済みは無効化）

---

## 6. 権限設計

| ロール | 許可操作 |
| --- | --- |
| child | 自分のプロフィール参照・更新、クイズ取得、解答送信、自分の進捗参照 |
| parent | 自分のプロフィール参照・更新、紐付き子どもの進捗参照、子ども紐付け管理 |
| admin（Django staff） | Django Admin 経由でクイズデータ管理、全ユーザー管理 |

---

## 7. バリデーション要件

- `username`: 3〜30文字、英数字とアンダースコアのみ
- `password`: 8文字以上、英字+数字を含む
- `grade`: 1〜9の整数
- `difficulty`: 1〜3の整数
- 解答送信時: `selected_choice` が `question` の選択肢に属することを検証

---

## 8. スコープ外（MVP非対象）

- ストーリーモード
- 報酬・コレクション機能
- 通知機能
- ソーシャルログイン（Google等）
- 画像アップロード（アバター等）
- リアルタイム機能（WebSocket）
