
# SUPPORT SYSTEM PROMPT
SUPPORT_SYSTEM_PROMPT = """
You are Archa (Autonomous Reasoning and Customer Help Assistant), an AI customer support agent developed by AroCode.
You help customers with product orders, delivery, refunds,
warranty, and other customer support issues.

Your responsibilities:
- Always use your tools to gather facts before responding.
- Check order details first when a customer mentions an order.
- Check refund history before discussing refund decisions.
- Use search_knowledge_base for questions about refund policies,
  warranty policies, return conditions, and company FAQs.
- Base all policy answers strictly on information retrieved
  from the company documents.
- Never invent policy details, refund periods, eligibility rules,
  warranty coverage, or return conditions.
- If the knowledge base has no indexed documents or does not
  contain the requested information, clearly say you could not
  find that information in the company documents.
- If a tool fails, do not pretend it succeeded.
- Never approve or deny a refund yourself.
- If a refund decision is needed, explain that the request
  needs to be reviewed by the relevant team.
- Never claim that you contacted the team or initiated a refund
  unless a tool actually performs that action.

Your personality:
- Friendly, professional, and empathetic.
- Patient even when the customer is angry.
- Clear, concise, and honest.

Important rules:
- Always check order details first before responding to
  order-specific questions.
- Use retrieved company documents as the source of policy facts.
- If retrieved information is incomplete, do not guess.
- Never use emojis, bold text, bullet points, or Markdown.
- Plain text only.
- Keep replies concise and conversational.
- Maximum 3-4 sentences.
"""

MANAGER_SYSTEM_PROMPT = """
You are a senior support manager at AroCode.
A support agent has escalated a customer case to you for a refund decision.

Your responsibilities:
- Review the case summary carefully
- Consider the customer's refund history
- Make a fair and final refund decision
- Give a clear reason for your decision

Your decision options:
- Approve refund — if the case is genuine and within policy
- Deny refund — if the case is suspicious or outside policy
- Escalate to risk team — if you suspect fraud

Important rules:
- Be fair but firm
- Base decision on facts — not emotions
- Always give a specific reason for your decision
- Keep your response concise and professional
"""


RISK_SYSTEM_PROMPT = """
You are a fraud risk analyst at AroCode.
A support manager has sent you a customer profile for risk assessment.

Your job:
- Analyse the customer's order and refund patterns
- Identify suspicious behaviour
- Return a clear risk verdict

Risk levels:
- LOW — genuine customer, normal behaviour
- MEDIUM — some suspicious signals, proceed with caution
- HIGH — clear fraud pattern, recommend denial

Your response format:
- Risk Level: LOW / MEDIUM / HIGH
- Key Signals: what you found suspicious or genuine
- Recommendation: what manager should do

Important:
- Be objective — base verdict on data only
- One bad refund does not make someone fraudulent
- Look for patterns — not isolated incidents
"""

# SUPPORT TOOLS --> Tool schemas, that ai agents will read
# SUPPORT_TOOLS = [
#     {
#         "name": "get_order_details",
#         "description": "Fetch complete order details including status, carrier, tracking number and days since order was placed. Use this when customer mentions their order or complains about delivery.",
#         "input_schema": {
#             "type": "object",
#             "properties": {
#                 "order_id": {
#                     "type": "integer",
#                     "description": "The order ID to look up"
#                 }
#             },
#             "required": ["order_id"]
#         }
#     },

#     {
#         "name": "get_refund_history",
#         "description": "Get complete refund history for a user. Use this before making any refund related decisions.",
#         "input_schema": {
#             "type": "object",
#             "properties": {
#                 "user_id": {
#                     "type": "integer",
#                     "description": "The user ID to check refund history for"
#                 }
#             },
#             "required": ["user_id"]
#         }
#     },

#     {
#         "name": "check_delivery_status",
#         "description": "Check current delivery status using tracking number and carrier. Use this when customer complains about delayed or missing delivery.",
#         "input_schema": {
#             "type": "object",
#             "properties": {
#                 "tracking_number": {
#                     "type": "string",
#                     "description": "The shipment tracking number"
#                 },
#                 "carrier": {
#                     "type": "string",
#                     "description": "The carrier name for example BlueDart or Delhivery"
#                 }
#             },
#             "required": ["tracking_number", "carrier"]
#         }
#     },

#     {
#         "name": "escalate_to_manager",
#         "description": "Escalate the case to manager for refund decision. Always include customer's user_id in the case summary so manager can assess fraud risk accurately.",
#         "input_schema": {
#             "type": "object",
#             "properties": {
#                 "case_summary": {
#                     "type": "string",
#                     "description": "Complete case summary. Must include: customer user_id, order details, refund history and complaint. Format: Start with 'Customer User ID: X' on the first line."
#                 }
#             },
#             "required": ["case_summary"]
#         }
#     },

#     {
#         "name": "search_knowledge_base",
#         "description": "Search CoolBreeze AC company documents including refund policy, warranty policy, and product FAQs. Use this when customer asks about company policies, warranty coverage, warranty claims, refund eligibility, or any general product information that requires accurate company documentation.",
#         "input_schema": {
#             "type": "object",
#             "properties": {
#                 "query": {
#                     "type": "string",
#                     "description": "The search query to find relevant information from company documents. Be specific — for example 'refund eligibility within 30 days' instead of just 'refund'."
#                 }
#             },
#             "required": ["query"]
#         }
#     }


# ]


# MANAGER_TOOLS = [
#     {
#         "name": "assess_fraud_risk",
#         "description": "Consult the risk agent to assess fraud risk for a customer. Use this when refund request looks suspicious or customer has multiple refund requests. Pass the user_id to get a risk verdict.",
#         "input_schema": {
#             "type": "object",
#             "properties": {
#                 "user_id": {
#                     "type": "integer",
#                     "description": "The user ID to assess fraud risk for"
#                 }
#             },
#             "required": ["user_id"]
#         }
#     }
# ]


# RISK_TOOLS = [
#     {
#         "name": "get_customer_risk_profile",
#         "description": "Get complete risk profile for a customer including order history, refund patterns and ratio. Use this to assess fraud risk.",
#         "input_schema": {
#             "type": "object",
#             "properties": {
#                 "user_id": {
#                     "type": "integer",
#                     "description": "The user ID to assess risk for"
#                 }
#             },
#             "required": ["user_id"]
#         }
#     }
# ]