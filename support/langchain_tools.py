from langchain.tools import tool 
from .rag import search_knowledge_base as rag_search
from datetime import timedelta
from django.utils import timezone
from .tracking_data import DELIVERY_DATA
from orders.models import Order, RefundReQuest


@tool 
def get_order_details(order_id: int) -> dict:
    """Fetch complete order details including status, carrier, tracking numer and days since """

    try:
        order = Order.objects.get(id=order_id)
        return {
            "order_id": order.id,
            "product_name": order.product_name,
            "amount": str(order.amount),
            "status": order.status,
            "carrier": order.carrier,
            "tracking_number": order.tracking_number,
            "delivery_address": order.delivery,
            "ordered_on": order.created_at.strftime("%d %b %Y"),
            "days_since_order": (timezone.now() - order.created_at).days,
        }
    except Order.DoesNotExist:
        return {"error": f"Order #{order_id} not found"}
    

@tool 
def get_refund_history(user_id: int) -> dict: 
    """Get complete refund history for a user. Use this before making any refund related decisions."""

    refunds = RefundReQuest.objects.filter(user_id=user_id).order_by("-created_at")
    history = []

    for refund in refunds:
        history.append({
                    "order_id": refund.order.id,
                    "product": refund.order.product_name,
                    "reason": refund.reason,
                    "status": refund.status,
                    "requested_on": refund.created_at.strftime("%d %b %Y"),
                })
    return {
        "total_refund_requests": len(history),
        "history": history
    }


@tool
def check_delivery_status(tracking_number: int, carrier=None) -> dict:
    """Check current delivery status using tracking number and carrier. Use this when customer complains about delayed or missing delivery."""
        
    default_response = {
        "status": "Unknown",
        "last_location": "Tracking info unavailable",
        "last_update": "N/A",
        "estimated_delivery": "Contact carrier directly",
        "delay_reason": "No updates from carrier",
    }
    result = dict(DELIVERY_DATA.get(tracking_number, default_response))
    result["tracking_number"] = tracking_number
    if carrier is not None:
        result["carrier"] = carrier
    return result


@tool
def get_customer_risk_profile(user_id: int) -> dict:
    """Get complete risk profile for a customer including order history, refund patterns and ratio. Use this to assess fraud risk."""

    refunds = RefundReQuest.objects.filter(user_id=user_id)
    orders = Order.objects.filter(user_id=user_id)
    recent_refunds = refunds.filter(
        created_at__gte=timezone.now() - timedelta(days=90)
    ).count()

    denied = refunds.filter(status="denied").count()
    approved = refunds.filter(status="approved").count()
    pending = refunds.filter(status="pending").count()
    total_orders = orders.count()
    total_refunds = refunds.count()
    refund_to_order_ratio = round(total_refunds / total_orders, 2) if total_orders else 0

    return {
        "user_id": user_id,
        "total_orders": total_orders,
        "total_refund_requests": total_refunds,
        "refunds_last_90_days": recent_refunds,
        "denied_refunds": denied,
        "approved_refunds": approved,
        "pending_refunds": pending,
        "refund_to_order_ratio": refund_to_order_ratio,
    }


@tool
def search_knowledge_base(query: str) -> dict:
    """Search the support knowledge base for information relevant to a customer query."""
    return {"result": rag_search(query)}