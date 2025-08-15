# News2Discord

RSSフィードから記事を取得し、AIで要約・品質判定を行ってDiscordに通知する非同期処理ツールです。

## 🚀 機能

- **RSSフィード処理**: 複数のRSSフィードから記事を自動取得
- **記事解析**: newspaper3kを使用した記事本文の抽出
- **AI要約**: LangChain + OpenAIによる記事の要約とキーワード抽出
- **品質判定**: AIによる記事品質の自動判定（高品質記事のみ通知）
- **Discord通知**: レート制限対応のDiscord Webhook通知
- **非同期処理**: 効率的な非同期処理による高速化

## 🏗️ アーキテクチャ

### システム全体構成

```mermaid
graph TB
    subgraph "外部サービス"
        RSS[RSSフィード]
        OpenAI[OpenAI API]
        Discord[Discord Webhook]
    end
    
    subgraph "News2Discord"
        subgraph "データ処理"
            FeedParser[feedparser]
            Newspaper[newspaper3k]
            Pandas[pandas]
        end
        
        subgraph "AI処理"
            LangGraph[LangGraph]
            Summarize[要約処理]
            Judge[品質判定]
        end
        
        subgraph "通知"
            DiscordClient[aiohttp + discord.py]
        end
        
        subgraph "設定管理"
            Config[TOML設定]
            Models[Pydanticモデル]
        end
    end
    
    RSS --> FeedParser
    FeedParser --> Pandas
    Pandas --> Newspaper
    Newspaper --> LangGraph
    LangGraph --> Summarize
    Summarize --> Judge
    Judge --> DiscordClient
    DiscordClient --> Discord
    OpenAI --> LangGraph
    Config --> Models
    Models --> News2Discord
    
    style RSS fill:#e1f5fe
    style OpenAI fill:#f3e5f5
    style Discord fill:#e8f5e8
    style LangGraph fill:#fff3e0
```

### 非同期処理フロー

```mermaid
sequenceDiagram
    participant M as main.py
    participant N as News2Discord
    participant F as FeedParser
    participant A as AI Pipeline
    participant D as Discord
    
    M->>N: 非同期実行開始
    N->>F: RSSフィード取得
    F-->>N: 記事リスト
    
    loop 各記事
        N->>N: 記事本文抽出
        N->>A: AI要約・品質判定
        A-->>N: 結果
        
        alt 高品質記事
            N->>D: Discord通知
            D-->>N: 送信完了
        else 低品質記事
            N->>N: スキップ
        end
    end
    
    Note over N,D: レート制限対応<br/>通知間に待機時間
```

### データフロー

```mermaid
flowchart TD
    A[RSSフィード] --> B[feedparser]
    B --> C[記事エントリ取得]
    C --> D[時間フィルタリング]
    D --> E[newspaper3k]
    E --> F[記事本文抽出]
    F --> G[LangGraph]
    G --> H[AI要約]
    H --> I[品質判定]
    I --> J{高品質?}
    J -->|Yes| K[Discord通知]
    J -->|No| L[スキップ]
    K --> M[aiohttp]
    
    style A fill:#e1f5fe
    style G fill:#f3e5f5
    style K fill:#e8f5e8
    style M fill:#fff3e0
```

### 処理フロー詳細

1. **フィード取得**: 設定されたRSSフィードから記事を取得
2. **時間フィルタリング**: 指定時間（デフォルト1時間前）以降の記事を抽出
3. **記事解析**: 各記事のURLから本文、タイトル、画像を抽出
4. **AI処理**: LangGraphを使用した要約と品質判定のパイプライン
5. **通知送信**: 高品質と判定された記事のみDiscordに通知

## 📋 セットアップ

### 前提条件

- Python 3.12以上
- OpenAI API キー（環境変数 `OPENAI_API_KEY` で設定）

### 1. 依存関係のインストール

```bash
# uvを使用（推奨）
uv sync
```

### 2. 設定ファイルの準備

```bash
cp config/example.config.toml config/config.toml
```

### 3. 設定ファイルの編集

`config/config.toml` を編集して以下を設定：

```toml
[ai.summarization]
model = "gpt-5-mini"  # 使用するOpenAIモデル
temperature = 0.1
system_prompt = "記事の要約プロンプト"

[ai.judge]
model = "gpt-5-mini"
temperature = 0.1
system_prompt = "品質判定プロンプト"

[notifications.discord]
webhook_url = "https://discord.com/api/webhooks/your-webhook-url"
rate_limit_delay = 0.4  # 通知間の待機時間（秒）
max_retries = 3  # 最大リトライ回数

[[feeds]]
name = "TechCrunch"
url = "https://techcrunch.com/feed/"
```

## 🚀 使用方法

### 基本実行

```bash
# 1時間前からの記事を処理
uv run main.py
```

### カスタムオフセット

```bash
# 3時間前からの記事を処理
uv run main.py --offset=3
```

### コマンドライン引数

- `--offset`: 処理対象の時間範囲（時間単位、デフォルト: 1）

## ⚙️ 設定詳細

### AI設定

#### 要約設定 (`[ai.summarization]`)
- `model`: 使用するOpenAIモデル（例: "gpt-5"）
- `temperature`: 生成のランダム性（0.0-1.0）
- `system_prompt`: 要約用のシステムプロンプト

#### 品質判定設定 (`[ai.judge]`)
- `model`: 使用するOpenAIモデル（例： "gpt-5-mini"）
- `temperature`: 生成のランダム性
- `system_prompt`: 品質判定用のシステムプロンプト

### Discord設定 (`[notifications.discord]`)
- `webhook_url`: Discord Webhook URL
- `rate_limit_delay`: 通知間の待機時間（秒）
- `max_retries`: 送信失敗時の最大リトライ回数

### フィード設定 (`[[feeds]]`)
- `name`: フィードの表示名
- `url`: RSSフィードのURL

## 🔧 開発

### 開発環境のセットアップ

```bash
# 開発用依存関係のインストール
uv sync --group dev

# コードフォーマット
uv run ruff format .

# リント
uv run ruff check .
```

### プロジェクト構造

```
news2discord/
├── main.py                 # エントリーポイント
├── news2discord/
│   ├── __init__.py        # メインクラス
│   ├── models/            # データモデル
│   │   ├── config.py      # 設定モデル
│   │   ├── record.py      # 記事データモデル
│   │   ├── flow.py        # AI処理モデル
│   │   └── notification.py # 通知モデル
│   ├── flow/              # AI処理パイプライン
│   │   ├── __init__.py    # LangGraph設定
│   │   ├── summarize.py   # 要約処理
│   │   └── judge.py       # 品質判定
│   └── notification/      # 通知機能
│       └── discord.py     # Discord通知
└── config/
    ├── config.toml        # 設定ファイル
    └── example.config.toml # 設定例
```

## 🐛 トラブルシューティング

### よくある問題

1. **設定ファイルが見つからない**
   ```
   設定ファイルが見つかりません: config/config.toml
   ```
   → `config/example.config.toml` を `config/config.toml` にコピーしてください

2. **Discord Webhook URLが設定されていません**
   → 設定ファイルの `webhook_url` を正しく設定してください

3. **OpenAI API エラー**
   → 環境変数 `OPENAI_API_KEY` が正しく設定されているか確認してください

4. **レート制限エラー**
   → `rate_limit_delay` の値を増やしてレート制限を回避してください

## 📝 ログ

アプリケーションは以下のログレベルで情報を出力します：

- `INFO`: 処理の進行状況
- `WARNING`: 記事取得失敗などの警告
- `ERROR`: エラー情報

ログフォーマット: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

## 🤝 貢献

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。