# App Service Bot

Teams / Azure Bot Service からの Bot Framework Activity を `/api/messages` で受け取り、Azure Functions の `/api/ask` に質問を転送します。

## App settings

```text
MicrosoftAppId=<Azure Bot の Microsoft App ID>
MicrosoftAppPassword=<Azure Bot の client secret>
FUNCTION_ASK_URL=https://<function-app>.azurewebsites.net/api/ask
BOT_FUNCTION_SHARED_SECRET=<Function App と同じ共有シークレット>
```

Teams テナントと Azure リソーステナントが別の場合、Azure Bot / App registration は Teams 側から利用できるように multi-tenant app として作成します。`MicrosoftAppId` と `MicrosoftAppPassword` は Teams から Bot Connector 経由で到達する Bot 用 app の値です。Foundry を呼ぶための `AZURE_CLIENT_ID` / `AZURE_CLIENT_SECRET` とは分けてください。

## Local run

Bot Framework Emulator やトンネルを使う場合のローカル実行例です。

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r app-service-bot/requirements.txt
export FUNCTION_ASK_URL="http://localhost:7071/api/ask"
python app-service-bot/app.py
```

App Service の Startup command:

```bash
python app.py
```
