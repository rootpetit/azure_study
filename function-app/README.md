# Azure Functions app

`/api/ask` で App Service Bot から質問を受け取り、Microsoft Foundry Agent Service の `inquiry-agent` と `rag-agent` を順番に呼び出します。検索は `rag-agent` に追加した組み込み File search Tool に委譲します。

処理順:

1. `inquiry-agent` で Teams の質問を RAG 検索向けの短いクエリにします。
2. `rag-agent` が Foundry 組み込み File search Tool を使ってナレッジを検索し、回答候補を作ります。
3. `inquiry-agent` で RAG 回答候補を Teams 向けの日本語回答に整えます。

## App settings

```text
FOUNDRY_PROJECT_ENDPOINT=https://<foundry-resource>.services.ai.azure.com/api/projects/<project-name>
FOUNDRY_AUTH_MODE=service_principal
AZURE_TENANT_ID=<Azure リソース側テナント ID>
AZURE_CLIENT_ID=<Foundry 呼び出し用 App registration の client ID>
AZURE_CLIENT_SECRET=<Foundry 呼び出し用 client secret>
INQUIRY_AGENT_NAME=inquiry-agent
RAG_AGENT_NAME=rag-agent
BOT_FUNCTION_SHARED_SECRET=<App Service と同じ共有シークレット>
```

クロステナント想定では、Function App の Managed Identity ではなく、Azure リソース側テナントに作成した App registration / service principal を使います。その service principal に Foundry project/resource の agent を呼び出すための権限を付与してください。

同一 Azure テナント内で学習するだけなら、`FOUNDRY_AUTH_MODE=managed_identity` にして Managed Identity を使う構成も可能です。

## Local run

```bash
cd function-app
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp local.settings.example.json local.settings.json
func start
```
