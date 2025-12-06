# 学習サポート Web アプリ（Django + React）

小学生〜中学生と保護者を対象とした学習サポート Web アプリです。  
クイズ・ストーリーモード・実績/コレクションなどの要素を通じて、学習を継続しやすくすることを目的としています。  
保護者は学習履歴や正答率を確認でき、声かけのきっかけづくりにも役立ちます。

---

## 🚀 概要

本アプリは以下の２つで構成されます。

- **フロントエンド（React）**：ユーザー向け UI を提供する SPA  
- **バックエンド（Django + Django REST Framework）**：REST API、認証、学習データ管理

ローカル開発時は Django と React を別々のサーバーとして起動し、将来的に単一サーバーまたはクラウド構成を採用します。

---

## 🏗 システム構成

### フロントエンド（React）

- SPA（React Router による画面遷移）
- 主な画面
  - クイズ選択（教科・単元）
  - クイズ出題・回答
  - ストーリーモード
  - 実績・コレクション
  - 保護者向けダッシュボード（進捗・統計）
- Django API と HTTP 経由で通信
- 本番環境では静的ファイルとしてホスティング

### バックエンド（Django + DRF）

- REST API の提供
- 認証機能（子ども / 保護者）
- 学習データ（問題・回答履歴・実績）の管理
- Django Admin による管理 UI
- Django ORM による PostgreSQL 操作

### データベース（PostgreSQL）

主なテーブル想定：

- `users` / `profiles_child`
- `subjects`（教科）
- `units`（単元）
- `questions`
- `answers`（解答履歴）
- `rewards` / `user_rewards`
- `stories` / `story_steps`

---

## 📦 技術スタック

### Frontend

- TypeScript / JavaScript
- React
- Vite（ビルドツール）
- React Router
- 状態管理：React Hooks（必要に応じて Zustand / Redux）
- UI：Tailwind CSS または MUI / Chakra UI
- テスト：Jest + React Testing Library

### Backend

- Python
- Django
- Django REST Framework (DRF)
- PostgreSQL
- 認証：Django セッション認証（将来的に JWT も検討）

### Infrastructure / Tools

- GitHub（ソース管理）
- GitHub Actions（CI/CD）
- Docker / docker-compose（任意）
- VS Code（推奨開発環境）

---

## 🛠 ローカル開発手順

### フロントエンド

```bash
cd frontend
npm install
npm run dev
```

### バックエンド

```bash
cd backend
pip install -r requirements.txt
python manage.py runserver
```

- React: [http://localhost:5173](http://localhost:5173)  
- Django API: [http://localhost:8000/api/](http://localhost:8000/api/)  

開発時は CORS 設定で React 側オリジンを許可します。

---

## 🌐 デプロイ方針

### 最初のデプロイ（単一サーバー構成）

- Nginx（静的ファイル配信 & リバースプロキシ）
- Django（Gunicorn）
- PostgreSQL（ローカルまたは外部 DB）

### 将来的なクラウド構成（AWS の例）

- フロント：S3 + CloudFront
- API：ECS Fargate / Elastic Beanstalk / EC2
- DB：RDS (PostgreSQL)
- 監視：CloudWatch, Sentry

---

## 📅 開発フェーズ

1. **プロトタイプ**  
   - Django + React の基本動作  
   - クイズ機能・ログイン機能の実装  

2. **MVP**  
   - 単一サーバー構成でデプロイ  
   - 子ども/保護者の一連の学習導線を構築  

3. **拡張フェーズ**  
   - ストーリーモード強化  
   - 実績・コレクション要素追加  
   - アクセス増加に応じてクラウド化

---

## 📘 今後の予定

- 画面一覧・画面遷移の整理  
- API エンドポイント設計  
- DB スキーマ設計  

---

## 📄 ライセンス

（後で選択）

## 📁 リポジトリ構成

```text
.
├── README.md                 # プロジェクト概要（今回作ったもの）
├── .gitignore
├── package.json              # ルート共通ツール用（任意）
├── docker-compose.yml        # 開発用コンテナ定義（任意）
├── frontend/                 # React フロントエンド
│   ├── package.json
│   ├── vite.config.ts        # Vite 設定（Vite 利用の場合）
│   ├── tsconfig.json
│   ├── public/
│   │   └── index.html
│   └── src/
│       ├── main.tsx          # エントリーポイント
│       ├── App.tsx
│       ├── routes/           # ルーティング定義
│       │   └── index.tsx
│       ├── pages/            # 画面コンポーネント
│       │   ├── HomePage.tsx
│       │   ├── QuizSelectPage.tsx
│       │   ├── QuizPlayPage.tsx
│       │   ├── StoryModePage.tsx
│       │   ├── CollectionPage.tsx
│       │   └── ParentDashboardPage.tsx
│       ├── components/       # 再利用コンポーネント
│       │   ├── layout/
│       │   │   ├── Header.tsx
│       │   │   └── Footer.tsx
│       │   ├── quiz/
│       │   │   ├── QuestionCard.tsx
│       │   │   └── ChoiceButton.tsx
│       │   ├── common/
│       │   │   ├── Button.tsx
│       │   │   └── LoadingSpinner.tsx
│       │   └── charts/
│       │       └── ProgressChart.tsx
│       ├── features/         # 機能単位のロジック
│       │   ├── auth/
│       │   │   ├── hooks.ts
│       │   │   └── api.ts
│       │   ├── quiz/
│       │   │   ├── hooks.ts
│       │   │   └── api.ts
│       │   └── progress/
│       │       ├── hooks.ts
│       │       └── api.ts
│       ├── api/              # API クライアント層
│       │   ├── client.ts     # axios/fetch の共通設定
│       │   └── endpoints.ts  # エンドポイント定義
│       ├── styles/           # グローバルスタイル
│       │   └── index.css
│       └── assets/           # 画像・アイコンなど
│           └── logo.svg
│
└── backend/                  # Django バックエンド
    ├── manage.py
    ├── requirements.txt
    ├── pyproject.toml        # poetry など使う場合（任意）
    ├── config/               # Django プロジェクト設定
    │   ├── __init__.py
    │   ├── settings.py
    │   ├── urls.py
    │   ├── asgi.py
    │   └── wsgi.py
    ├── apps/                 # Django アプリケーション群
    │   ├── accounts/         # 認証・ユーザー関連
    │   │   ├── __init__.py
    │   │   ├── models.py
    │   │   ├── views.py
    │   │   ├── serializers.py
    │   │   ├── urls.py
    │   │   └── tests.py
    │   ├── quiz/             # 問題・単元・回答
    │   │   ├── __init__.py
    │   │   ├── models.py
    │   │   ├── views.py
    │   │   ├── serializers.py
    │   │   ├── urls.py
    │   │   └── tests.py
    │   ├── progress/         # 学習履歴・統計
    │   │   ├── __init__.py
    │   │   ├── models.py
    │   │   ├── views.py
    │   │   ├── serializers.py
    │   │   ├── urls.py
    │   │   └── tests.py
    │   └── story/            # ストーリーモード
    │       ├── __init__.py
    │       ├── models.py
    │       ├── views.py
    │       ├── serializers.py
    │       ├── urls.py
    │       └── tests.py
    ├── api/                  # API ルート定義
    │   ├── __init__.py
    │   ├── urls.py           # /api/... をまとめる
    │   └── schema.py         # API スキーマ（任意）
    └── scripts/              # メンテ・データ投入用スクリプト
        └── load_sample_data.py
```
