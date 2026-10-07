from datetime import timedelta

from orders.models import Order, RefundRequest
from django.utils import timezone
from .tracking_data import DELIVERY_DATA
from .rag import search_knowledge_base as rag_search



def get_order_details(order_id):
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
            "ordered_on": order.created_at.strftime("%d %b %Y"), # 25 May 2026
            "days_since_order": (timezone.now() - order.created_at).days, # 20
        }
    except Order.DoesNotExist:
        return {"error": f"Order #{order_id} not found."}
    

def get_refund_history(user_id):
    refunds = RefundRequest.objects.filter(user_id=user_id).order_by("-created_at")

    history = []
    for refund in refunds:
        history.append({
            "order_id": refund.order.id,
            "product": refund.order.product_name,
            "reason": refund.reason,
            "status": refund.status,
            "requested_on": refund.created_at.strftime("%d %b %Y"), # 25 May 2026
        })
    return {
        "total_refund_requests": len(history),
        "history": history,
    }


def check_delivery_status(tracking_number, carrier):
    default_response = {
        "status": "Unknown",
        "last_location": "Tracking info unavailable",
        "last_update": "N/A",
        "estimated_delivery": "Contact carrier directly",
        "delay_reason": "No updates from carrier",
    }
    result = DELIVERY_DATA.get(tracking_number, default_response)
    result["tracking_number"] = tracking_number
    result["carrier"] = carrier
    return result


def get_customer_risk_profile(user_id):
    print('user_id==>', user_id)
    refunds = RefundRequest.objects.filter(user_id=user_id)
    orders = Order.objects.filter(user_id=user_id)

    # recent 90 days refund requests
    recent_refunds = refunds.filter(created_at__gte=timezone.now() - timedelta(days=90)).count()

    denied = refunds.filter(status="denied").count()
    approved = refunds.filter(status="approved").count()
    pending = refunds.filter(status="pending").count()

    total_orders = orders.count()
    total_refunds = refunds.count()

    if total_orders > 0:
        refund_to_order_ratio = round(total_refunds / total_orders, 2) # order = 8, refund = 12
    else:
        refund_to_order_ratio = 0
    
    return {
        "user_id": user_id,
        "total_orders": total_orders,
        "total_refund_requests": total_refunds,
        "refunds_last_90_days": recent_refunds,
        "denied_refunds": denied,
        "approved_refunds": approved,
        "pending_refunds": pending,
        "refund_to_order_ratio": refund_to_order_ratio
    }


# wrapper function
def search_knowledge_base(query):
    result = rag_search(query)
    return {"result": result}