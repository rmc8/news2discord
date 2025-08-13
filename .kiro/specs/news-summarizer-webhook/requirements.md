# Requirements Document

## Introduction

ニュース要約・配信システムは、複数のRSSフィード（Yahoo News、Google News、Smart News、Qiita、Zenなど）およびnewspaper3kを使用したWebスクレイピングから記事情報を自動取得し、生成AIを使用して要約・カテゴライズを行い、Webhookを通じて配信するシステムです。重複処理を防ぐためのデータベース管理機能も含みます。

## Requirements

### Requirement 1

**User Story:** システム管理者として、複数のニュースソース（RSSフィードとWebスクレイピング対象URL）を設定できるようにしたい。これにより、様々なニュースソースから情報を収集できる。

#### Acceptance Criteria

1. WHEN システムが起動される THEN システム SHALL 設定ファイルから複数のRSSフィードURLとスクレイピング対象URLを読み込む
2. WHEN 新しいニュースソースが追加される THEN システム SHALL そのソースを監視対象に追加する
3. IF ニュースソースが無効または到達不可能 THEN システム SHALL エラーログを記録し、他のソースの処理を継続する

### Requirement 2

**User Story:** システムとして、RSSフィードとWebスクレイピングから記事情報を定期的に取得したい。これにより、最新のニュースを常に監視できる。

#### Acceptance Criteria

1. WHEN 定期実行タイマーが発火する THEN システム SHALL 全てのRSSフィードをチェックする
2. WHEN RSSフィードに新しい記事が発見される THEN システム SHALL 記事のURL、タイトル、内容、公開日時を取得する
3. WHEN スクレイピング対象URLが処理される THEN システム SHALL newspaper3kを使用して記事内容を抽出する
4. WHEN 記事取得に失敗する THEN システム SHALL エラーを記録し、次の記事の処理を継続する

### Requirement 3

**User Story:** システムとして、処理済みの記事を記録して重複処理を防ぎたい。これにより、同じ記事を何度も処理することを避けられる。

#### Acceptance Criteria

1. WHEN 記事が処理される前 THEN システム SHALL データベースで記事URLの存在をチェックする
2. IF 記事URLが既に存在する THEN システム SHALL その記事の処理をスキップする
3. WHEN 記事処理が完了する THEN システム SHALL 記事URLと処理日時をデータベースに保存する

### Requirement 4

**User Story:** システムとして、LangChainとLangGraphを使用して記事を要約・カテゴライズしたい。これにより、大量の記事を効率的に処理でき、状態管理とトークン数の節約ができる。

#### Acceptance Criteria

1. WHEN 新しい記事が取得される THEN システム SHALL LangChainを使用して記事内容を要約する
2. WHEN 要約が生成される THEN システム SHALL LangGraphの状態管理機能を使用して要約テキストを次の処理に渡す
3. WHEN カテゴライズ処理が実行される THEN システム SHALL 要約されたテキストを使用してカテゴリを分類する
4. WHEN AI処理に失敗する THEN システム SHALL エラーを記録し、元の記事情報を保持する
5. WHEN 要約とカテゴリが決定される THEN システム SHALL 結果をデータベースに保存する
6. WHEN LangGraphワークフローが実行される THEN システム SHALL 状態を適切に管理し、処理の進行状況を追跡する

### Requirement 5

**User Story:** システム管理者として、処理された記事をWebhookで外部システムに送信したい。これにより、Slack、Discord、その他のサービスに自動配信できる。

#### Acceptance Criteria

1. WHEN 記事の要約・カテゴライズが完了する THEN システム SHALL 設定されたWebhook URLに結果を送信する
2. WHEN Webhook送信が失敗する THEN システム SHALL リトライ機能を実行する
3. IF リトライが最大回数に達する THEN システム SHALL エラーログを記録し、次の記事処理を継続する
4. WHEN Webhook送信が成功する THEN システム SHALL 送信ログをデータベースに記録する

### Requirement 6

**User Story:** システム管理者として、システムの動作状況を監視したい。これにより、エラーや処理状況を把握できる。

#### Acceptance Criteria

1. WHEN システムが動作する THEN システム SHALL 処理状況をログファイルに記録する
2. WHEN エラーが発生する THEN システム SHALL エラーの詳細情報をログに記録する
3. WHEN 処理統計が必要 THEN システム SHALL 処理済み記事数、エラー数、成功数を提供する