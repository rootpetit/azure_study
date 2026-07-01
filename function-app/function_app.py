import json
import logging
import os
from typing import Any

import azure.functions as func
from azure.ai.projects import AIProjectClient
from azure.identity import ClientSecretCredential, DefaultAzureCredential


app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

PROJECT_ENDPOINT = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
INQUIRY_AGENT_NAME = os.environ.get("INQUIRY_AGENT_NAME", "inquiry-agent")
RAG_AGENT_NAME = os.environ.get("RAG_AGENT_NAME", "rag-agent")
SHARED_SECRET = os.environ.get("BOT_FUNCTION_SHARED_SECRET")
FOUNDRY_AUTH_MODE = os.environ.get("FOUNDRY_AUTH_MODE", "service_principal")


def get_azure_credential():
    if FOUNDRY_AUTH_MODE == "service_principal":
        return ClientSecretCredential(
            tenant_id=os.environ["AZURE_TENANT_ID"],
            client_id=os.environ["AZURE_CLIENT_ID"],
            client_secret=os.environ["AZURE_CLIENT_SECRET"],
        )

    return DefaultAzureCredential()


def get_project_client() -> AIProjectClient:
    return AIProjectClient(
        endpoint=PROJECT_ENDPOINT,
        credential=get_azure_credential(),
    )


def invoke_agent(openai_client: Any, agent_name: str, input_text: str) -> str:
    conversation = openai_client.conversations.create()
    response = openai_client.responses.create(
        conversation=conversation.id,
        input=input_text,
        extra_body={"agent_reference": {"name": agent_name, "type": "agent_reference"}},
    )
    return response.output_text


def invoke_inquiry_agent(question: str) -> str:
    project = get_project_client()
    openai_client = project.get_openai_client()

    search_query = invoke_agent(
        openai_client,
        INQUIRY_AGENT_NAME,
        (
            "次の Teams ユーザ質問を、RAG 検索に適した短い検索クエリにしてください。"
            "回答文ではなく検索クエリだけを返してください。\n\n"
            f"ユーザ質問: {question}"
        ),
    )

    rag_answer = invoke_agent(
        openai_client,
        RAG_AGENT_NAME,
        (
            "あなたに設定された組み込み File search Tool を使って、"
            "次のユーザ質問に回答してください。"
            "保存済みナレッジに根拠がない場合は、確認できないと明示してください。\n\n"
            f"ユーザ質問: {question}\n\n"
            f"検索クエリ: {search_query}"
        ),
    )

    return invoke_agent(
        openai_client,
        INQUIRY_AGENT_NAME,
        (
            "次の RAG 検索結果を使って、Teams ユーザへ日本語で回答してください。"
            "検索結果に根拠がない場合は、保存済みナレッジでは確認できないと伝えてください。\n\n"
            f"ユーザ質問: {question}\n\n"
            f"RAG 検索クエリ: {search_query}\n\n"
            f"RAG 検索結果: {rag_answer}"
        ),
    )


def require_shared_secret(req: func.HttpRequest) -> func.HttpResponse | None:
    if not SHARED_SECRET:
        return None

    provided = req.headers.get("x-bot-shared-secret")
    if provided != SHARED_SECRET:
        return func.HttpResponse(
            json.dumps({"error": "Unauthorized"}),
            status_code=401,
            mimetype="application/json",
        )
    return None


@app.route(route="ask", methods=["POST"])
def ask(req: func.HttpRequest) -> func.HttpResponse:
    unauthorized = require_shared_secret(req)
    if unauthorized:
        return unauthorized

    try:
        body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Request body must be JSON."}),
            status_code=400,
            mimetype="application/json",
        )

    question = (body.get("text") or "").strip()
    if not question:
        return func.HttpResponse(
            json.dumps({"error": "text is required."}),
            status_code=400,
            mimetype="application/json",
        )

    try:
        answer = invoke_inquiry_agent(question)
    except Exception as exc:
        logging.exception("Failed to invoke Foundry agents.")
        return func.HttpResponse(
            json.dumps({"error": str(exc)}, ensure_ascii=False),
            status_code=500,
            mimetype="application/json",
        )

    return func.HttpResponse(
        json.dumps({"answer": answer}, ensure_ascii=False),
        status_code=200,
        mimetype="application/json",
    )
