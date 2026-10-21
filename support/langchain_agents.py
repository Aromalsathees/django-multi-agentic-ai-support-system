from django.conf import settings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_tool_call
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver

from .event_queue import publish, DONE
from .langchain_tools import (
    get_order_details,
    get_refund_history,
    check_delivery_status,
    get_customer_risk_profile,
    search_knowledge_base,
)
from .models import Conversation, AgentLog
from .system_prompts import SUPPORT_SYSTEM_PROMPT, MANAGER_SYSTEM_PROMPT, RISK_SYSTEM_PROMPT


llm = ChatGoogleGenerativeAI(
    model=settings.GEMINI_MODEL,
    api_key=settings.GEMINI_API_KEY,
)

SUPPORT_TOOLS = [
    get_order_details,
    get_refund_history,
    check_delivery_status,
    search_knowledge_base,
]

checkpointer = InMemorySaver()


# support agent 
def run_support_agent(user_message, conversation_id, order_id, user_id):
    conv = Conversation.objects.get(id=conversation_id)

    @tool
    def escalate_to_manager(case_summary: str) -> str:
        """Escalate the case to a manager for a refund decision."""
        summary_with_user = (
            f"{case_summary}\nCustomer user_id: {user_id}"
        )
        return run_manager_agent(summary_with_user, conversation_id)

    @wrap_tool_call
    def log_tools_call_middleware(request, handler):
        tool_name = request.tool_call["name"]
        tool_args = request.tool_call["args"]

        AgentLog.objects.create(
            conversation=conv,
            event_type="tool_call",
            message=f"Calling tool {tool_name} with {tool_args}",
        )

        result = handler(request)

        AgentLog.objects.create(
            conversation=conv,
            event_type="tool_result",
            message=(
                f"Tool {tool_name} returned: "
                f"{str(result.content)[:200]}"
            ),
        )

        return result

    config = {
        "configurable": {
            "thread_id": str(conversation_id),
        }
    }

    contextual_message = (
        f"[Context: Order #{order_id}, User ID: {user_id}]\n"
        f"Customer message: {user_message}"
    )

    support_agent = create_agent(
        model=llm,
        tools=SUPPORT_TOOLS + [escalate_to_manager],
        system_prompt=SUPPORT_SYSTEM_PROMPT,
        checkpointer=checkpointer,
        middleware=[log_tools_call_middleware],
    )

    result = support_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": contextual_message,
                }
            ]
        },
        config=config,
    )

    final_reply = result["messages"][-1].content

    AgentLog.objects.create(
        conversation=conv,
        event_type="final",
        message=final_reply,
    )

    publish(conversation_id, DONE)
    return final_reply


# Manager Agent 
def run_manager_agent(case_summary, conversation_id):
    conv = Conversation.objects.get(id=conversation_id)
    
    @tool
    def assess_fraud_risk(user_id: int) -> dict:
        """Consult the risk agent to assess fraud risk for a customer. Use this when refund request looks suspicious or customer has multiple refund requests. Pass the user_id to get a risk verdict."""
        return run_risk_agent(user_id, conversation_id)


    event = {"type": "manager", "message": f"Case received for review: {case_summary[:200]}"}
    publish(conversation_id, event)
    
    AgentLog.objects.create(conversation=conv, event_type="manager", message=f"Case received for review: {case_summary[:200]}")
    
    #middleware 
    @wrap_tool_call
    def log_manager_tools_call_middleware(request, handler):
        #before executing the tool 
        event = {"type": "manager", "message": f"Consulting risk agent for fraud assesment ..."}
        publish(conversation_id, event)

        AgentLog.objects.create(conversation=conv, event_type="manager", message=f"Consulting risk agent for fraud assesment ...")
    
        result = handler(request)
        # after execution 
        return result

    manager_agent = create_agent(
        model=llm,
        tools=[assess_fraud_risk],
        system_prompt=MANAGER_SYSTEM_PROMPT,
        middleware=[log_manager_tools_call_middleware]
    )

    result = manager_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": case_summary,
                }
            ]
        }
    )
    
    decision = result["messages"][-1].content
    event = {"type": "manager", "message": f"Decision: {decision[:200]}"}
    publish(conversation_id, event)

    AgentLog.objects.create(conversation=conv, event_type="manager", message=f"Decision: {decision[:200]}")

    return decision


# Risk Agent 
def run_risk_agent(user_id, conversation_id):
    conv = Conversation.objects.get(id=conversation_id)

    event = {"type": "risk", "message": f"Starting fraud assessment: {user_id}"}
    publish(conversation_id, event)

    
    AgentLog.objects.create(conversation=conv, event_type="risk", message=f"Starting fraud assesment for user: {user_id}")
    
    @wrap_tool_call
    def log_risk_tool_middleware(request, handler):
        tool_name = request.tool_call["name"]
        event = {"type": "risk", "message": f"Calling {tool_name} to get customer risk profile..."}
        publish(conversation_id, event)
            
        AgentLog.objects.create(conversation=conv, event_type="risk", message=f"Calling {tool_name} to get customer risk profile...")
        result = handler(request)
        return result 

    risk_agent = create_agent(
        model=llm,
        system_prompt=RISK_SYSTEM_PROMPT,
        tools=[get_customer_risk_profile],  
        middleware=[log_risk_tool_middleware]
    )

    result = risk_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": f"Please assess the fraud risk for user ID {user_id}. User your tool to get their profile and return a verdict.",
                }
            ]
        },
    )

    # verdict = response.content[-1].content
    verdict = result["messages"][-1].content

    event = {"type": "risk", "message": f"Verdict: {verdict[:200]}"}
    publish(conversation_id, event)
    
    AgentLog.objects.create(conversation=conv, event_type="risk", message=f"Verdict: {verdict[:200]}")
    print("verdict==>:", verdict)
    return verdict
    





