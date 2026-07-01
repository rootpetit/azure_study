# Teams app manifest

`manifest.json` は雛形です。Teams にアップロードする前に次を差し替えてください。

- `id`: Teams アプリ自体の GUID。`uuidgen` などで新規作成します。
- `bots[0].botId`: Azure Bot の Microsoft App ID。
- `validDomains[0]`: App Service のドメイン。例: `my-rag-bot.azurewebsites.net`。
- `developer`: 学習用であれば `example.com` のままでも検証できる場合がありますが、組織ポリシーによっては実 URL が必要です。

Teams アプリ package には `manifest.json`、`color.png`、`outline.png` を zip の直下に入れます。

アイコン要件は Teams の manifest バージョンに依存します。Portal または Teams Developer Portal でエラーが出た場合は、Developer Portal の指示に従って PNG アイコンを作り直してください。
