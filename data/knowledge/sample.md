# Azure 学習メモ

Azure App Service は Web アプリケーション、REST API、バックエンドサービスをホストするための PaaS です。OS や Web サーバーの管理を最小化しながら、アプリケーションコードのデプロイ、スケール、監視を行えます。

Azure Functions はイベント駆動で小さな処理を実行するサーバーレスコンピューティングサービスです。HTTP 要求、Storage Queue、Timer、Event Grid などをトリガーにできます。

Azure Blob Storage は非構造化データを保存するオブジェクトストレージです。PDF、テキスト、画像、ログなどをコンテナに保存できます。

このサンプルの Teams Bot は、Teams からの質問を App Service で受け取り、Azure Functions に渡します。Functions は Foundry の inquiry-agent で検索クエリを作り、Foundry の rag-agent に問い合わせます。rag-agent は組み込み File search Tool で保存済みナレッジを検索し、Teams に返す回答を作成します。
