"""the Campus Customs shopping agent: wires the prompt, model and tools together."""
from pathlib import Path

from openai import AsyncOpenAI
import catalogue
from pydantic_ai import Agent, RunContext, Tool
from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    TextPart,
    ToolCallPart,
    ToolReturnPart,
    UserPromptPart,
)
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.usage import UsageLimits

import audit
import config

# loop limit: cap how many model requests one chat turn may make (tool rounds)
REQUEST_LIMIT = 8
from models import ChatReply, CustomerInfo, PageContext, ProductCard
from tools import (
    ChatDeps,
    check_stock,
    find_products_in_budget,
    get_price,
    get_product_details,
    get_store_info,
    search_products,
    whoami,
)

# system prompt lives in its own file so the Campus Customs voice is easy to edit
PROMPT_PATH = Path(__file__).resolve().parent / "prompts" / "prompt.md"
SYSTEM_PROMPT = PROMPT_PATH.read_text(encoding="utf-8")


def _build_model() -> OpenAIChatModel:
    """point pydantic-ai's openai model at the portkey gateway."""
    client = AsyncOpenAI(
        base_url=config.portkey_base_url,
        api_key=config.portkey_api_key,
        default_headers={
            "x-portkey-api-key": config.portkey_api_key,
            "x-portkey-provider": config.portkey_provider,
        },
    )
    return OpenAIChatModel(
        config.chat_model, provider=OpenAIProvider(openai_client=client)
    )


# the agent: model + external prompt + the four catalogue tools
agent = Agent(
    _build_model(),
    deps_type=ChatDeps,
    system_prompt=SYSTEM_PROMPT,
    tools=[
        Tool(search_products),
        Tool(get_product_details),
        Tool(get_price),
        Tool(check_stock),
        Tool(find_products_in_budget),
        Tool(get_store_info),
        Tool(whoami),
    ],
    retries=2,
)


@agent.system_prompt
def who_is_chatting(ctx: RunContext[ChatDeps]) -> str:
    """tell the agent who the shopper is (name/email) for this turn."""
    customer = ctx.deps.customer
    if customer is None:
        return "The shopper is a guest (not logged in). Do not assume a name."
    return (
        f"The signed-in shopper is {customer.name} (email: {customer.email}). "
        "You may greet them by first name when it feels natural."
    )


@agent.system_prompt
def current_page(ctx: RunContext[ChatDeps]) -> str:
    """tell the agent which product the shopper is viewing, so 'this' resolves."""
    product = ctx.deps.current_product
    if not product:
        return "The shopper is not on a specific product page right now."
    return (
        "The shopper is currently viewing this product page, so words like "
        f'"this", "it" or "this one" refer to it: {product["name"]} '
        f'(product_id: {product["product_id"]}). Use this product_id with your '
        "tools when they ask about the item they are looking at."
    )


def to_message_history(history: list[dict[str, str]]) -> list[ModelMessage]:
    """convert stored (role, content) rows into pydantic-ai message history."""
    messages: list[ModelMessage] = []
    for item in history:
        role, content = item.get("role"), item.get("content", "")
        if not content:
            continue
        if role == "user":
            messages.append(ModelRequest(parts=[UserPromptPart(content=content)]))
        elif role == "assistant":
            messages.append(ModelResponse(parts=[TextPart(content=content)]))
    return messages


async def run_chat(
    message: str,
    history: list[dict[str, str]],
    customer: CustomerInfo | None = None,
    context: PageContext | None = None,
) -> ChatReply:
    """run one chat turn and return the typed reply plus any matching products.

    `customer` identifies a logged-in shopper; `context` carries the page they are
    on so the agent can resolve "this" to the product they are viewing.
    """
    current_product = None
    if context and context.product_id:
        current_product = catalogue.get_product(context.product_id)

    deps = ChatDeps(customer=customer, current_product=current_product)
    stop_reason = "completed"
    try:
        result = await agent.run(
            message,
            message_history=to_message_history(history),
            deps=deps,
            usage_limits=UsageLimits(request_limit=REQUEST_LIMIT),
        )
    except Exception as exc:  # usage-limit or model error - degrade gracefully
        stop_reason = f"error: {type(exc).__name__}"
        audit.log_turn(message, [], stop_reason, requests=REQUEST_LIMIT)
        return ChatReply(
            reply=(
                "Sorry, I had trouble with that request. Please try rephrasing, "
                "or ask about a specific product, price or size."
            ),
            products=[],
        )

    _audit_tool_activity(result)
    # count model requests this turn = number of model responses in the run
    requests = sum(
        1 for msg in result.all_messages() if isinstance(msg, ModelResponse)
    )
    tools_used = sorted(
        {
            part.tool_name
            for msg in result.all_messages()
            for part in getattr(msg, "parts", [])
            if isinstance(part, ToolCallPart)
        }
    )
    audit.log_turn(message, tools_used, stop_reason, requests=requests)

    products = [ProductCard.from_dict(p) for p in deps.shown.values()]
    return ChatReply(reply=result.output, products=products)


def _audit_tool_activity(result) -> None:
    """write one audit record per tool call, pairing calls with their results."""
    calls: dict[str, dict] = {}
    for msg in result.all_messages():
        for part in getattr(msg, "parts", []):
            if isinstance(part, ToolCallPart):
                calls[part.tool_call_id] = {"tool": part.tool_name, "args": part.args}
            elif isinstance(part, ToolReturnPart):
                call = calls.pop(part.tool_call_id, {"tool": part.tool_name, "args": None})
                audit.log_tool_call(call["tool"], call["args"], part.content)
    # any calls without a matching return (rare)
    for call in calls.values():
        audit.log_tool_call(call["tool"], call["args"], "<no result>")
