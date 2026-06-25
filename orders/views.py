from django.shortcuts import render, get_object_or_404
from .models import Order, RefundReQuest
from django.contrib.auth.decorators import login_required


@login_required(login_url='login_view')
def orders_list(request):
    orders = Order.objects.filter(user=request.user)
    context = {
        'orders': orders,
    }
    return render(request, 'orders_list.html', context)


def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # get refund history for this order
    refunds = RefundReQuest.objects.filter(order=order)

    context = {
        'order': order,
        'refunds': refunds,
    }
    return render(request, "order_detail.html", context)