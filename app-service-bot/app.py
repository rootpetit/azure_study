import json
import os
from http import HTTPStatus

import aiohttp
from aiohttp import web
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.core.integration import aiohttp_error_middleware
from botbuilder.core.teams import TeamsActivityHandler
from botbuilder.schema import Activity, ActivityTypes


APP_ID = os.environ.get("MicrosoftAppId", "")
APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
FUNCTION_ASK_URL = os.environ["FUNCTION_ASK_URL"]
FUNCTION_SHARED_SECRET = os.environ.get("BOT_FUNCTION_SHARED_SECRET")

SETTINGS = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
ADAPTER = BotFrameworkAdapter(SETTINGS)


class TeamsRagBot(TeamsActivityHandler):
    async def on_message_activity(self, turn_context: TurnContext):
        user_text = (turn_context.activity.text or "").strip()
        if not user_text:
            await turn_context.send_activity("質問を入力してください。")
            return

        await turn_context.send_activity(Activity(type=ActivityTypes.typing))

        try:
            answer = await ask_function(user_text, turn_context)
        except Exception as exc:
            answer = f"すみません、回答の生成中にエラーが発生しました。\n\n`{exc}`"

        await turn_context.send_activity(answer)


async def ask_function(user_text: str, turn_context: TurnContext) -> str:
    headers = {"Content-Type": "application/json"}
    if FUNCTION_SHARED_SECRET:
        headers["x-bot-shared-secret"] = FUNCTION_SHARED_SECRET

    payload = {
        "text": user_text,
        "conversation_id": turn_context.activity.conversation.id,
        "user_id": turn_context.activity.from_property.id,
    }

    timeout = aiohttp.ClientTimeout(total=120)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(FUNCTION_ASK_URL, headers=headers, json=payload) as response:
            response_text = await response.text()
            if response.status >= 400:
                raise RuntimeError(
                    f"Function returned HTTP {response.status}: {response_text}"
                )

            body = json.loads(response_text)
            return body.get("answer") or "回答が空でした。"


BOT = TeamsRagBot()


async def messages(req: web.Request) -> web.Response:
    if "application/json" not in req.headers.get("Content-Type", ""):
        return web.Response(status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)

    body = await req.json()
    activity = Activity().deserialize(body)
    auth_header = req.headers.get("Authorization", "")
    response = await ADAPTER.process_activity(activity, auth_header, BOT.on_turn)

    if response:
        return web.json_response(data=response.body, status=response.status)
    return web.Response(status=HTTPStatus.OK)


async def health(_: web.Request) -> web.Response:
    return web.json_response({"status": "ok"})


APP = web.Application(middlewares=[aiohttp_error_middleware])
APP.router.add_post("/api/messages", messages)
APP.router.add_get("/healthz", health)


if __name__ == "__main__":
    web.run_app(APP, host="0.0.0.0", port=int(os.environ.get("PORT", 3978)))
