from django.conf import settings 
from langchain_google_genai import ChatGoogleGenerativeAI
from .langchain_tools import get_order_details, get_refund_history, check_delivery_status, get_customer_risk_profile, search_knowledge_base
from .system_prompts import SUPPORT_SYSTEM_PROMPT
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

llm = ChatGoogleGenerativeAI(model=settings.GEMINI_MODEL, api_key=settings.GEMINI_API_KEY,)

SUPPORT_TOOLS = [get_order_details, get_refund_history, check_delivery_status, search_knowledge_base]

checkpointer = InMemorySaver()

support_agent = create_agent(
    model=llm,
    tools=SUPPORT_TOOLS,
    system_prompt=SUPPORT_SYSTEM_PROMPT,
    checkpointer=checkpointer
)

# The agent is ready now 

def run_support_agent(user_message, conversation_id, order_id, user_id):
    config = {"configurable": {"thread_id": str(conversation_id)}}

    contextual_message = f"[Context: This Conversation is about Order #{order_id}, user: {user_id}]"

    result = support_agent.invoke(
        {"message": [{"role":"user", "content": contextual_message}]}, 
        config=config
    )

    print('result ==> ', result["messages"][-1].content)