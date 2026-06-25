from orders.models import *
from django.utils import timezone

def get_order(order_id):
    try:
        order = Order.objects.get(id=order_id)
        return {
            'product_name':order.product_name,
            'amount':order.amount,
            'status':order.status,
            'carrier':order.carrier,
            'delivery':order.delivery,
            'tracking_number':order.tracking_number,
            'ordered_on':order.created_at.strftime("%d %b %Y"),
            'days_since_order': (timezone.now() - order.created_at).days,
        }
    
    except Order.DoesNotExist:
        return {'error':f'Order #{order_id} not found.'}
    
def get_refund_history(user_id):
    refunds = RefundReQuest.objects.filter(user=user_id).order_by('-created_at')
    history = []

    for refund in refunds:
        history.append(refund)

    context = {
        ''
    }