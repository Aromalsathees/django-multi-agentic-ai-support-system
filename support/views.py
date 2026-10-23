from django.shortcuts import render, get_object_or_404
import json
from django.http import JsonResponse, StreamingHttpResponse
import time

from .langchain_agents import run_support_agent
from .event_queue import publish, subscribe, unsubscribe
from .models import Conversation, Message

from orders.models import Order
from django.contrib.admin.views.decorators import staff_member_required

from queue import Empty


def chat(request, order_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get("message")

        if not user_message:
            return JsonResponse({"error": "Empty message"}, status=400)
        print(user_message)
        order = get_object_or_404(Order, id=order_id, user=request.user)

        conversation, created = Conversation.objects.get_or_create(user=request.user, order=order)
        
        Message.objects.create(conversation=conversation, role="user", content=user_message)

        event = {"type": "user_message", "message": user_message, "name": request.user.first_name}
        publish(conversation.id, event)
        print(event)
        # send user message and conversation to LLM
        reply = run_support_agent(user_message, conversation.id, order.id, request.user.id)
        print(reply)
        # store the LLM reply
        Message.objects.create(conversation=conversation, role="assistant", content=reply)
        
        # time.sleep(5)
        return JsonResponse({"reply": reply})
    

@staff_member_required
def dashboard(request):
    conversations = Conversation.objects.all().order_by("-created_at")
    print('conversations===>', conversations)
    context = {
        'conversations': conversations,
    }
    return render(request, "dashboard/dashboard.html", context)


@staff_member_required
def conversation_detail(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    messages = conversation.messages.order_by("created_at")
    agentlogs = conversation.agentlogs.order_by("created_at")

    context = {
        "conversation": conversation,
        "messages": messages,
        "agentlogs": agentlogs
    }
    return render(request, "dashboard/conversation_detail.html", context)



def conversation_stream(request, conversation_id):

    # Verify that the user is allowed to access this conversation
    conversation = get_object_or_404(
        Conversation,
        id=conversation_id,
        user=request.user,
    )

    def event_stream():
        q = subscribe(conversation.id)

        try:
            # Notify the client that the connection is established
            yield 'data: {"type": "connected"}\n\n'

            while True:
                try:
                    # Wait for the next event
                    event = q.get(timeout=15)

                except Empty:
                    # Send heartbeat to keep the connection alive
                    yield ": keep-alive\n\n"
                    continue

                # Send the event immediately to the client
                yield f"data: {json.dumps(event)}\n\n"

                # Stop streaming when the agent finishes
                if event.get("type") == "done":
                    break

        finally:
            # Clean up the subscription when the stream closes
            unsubscribe(conversation.id, q)

    response = StreamingHttpResponse(
        event_stream(),
        content_type="text/event-stream",
    )

    # Prevent caching and discourage proxy buffering
    response["Cache-Control"] = "no-cache, no-transform"
    response["X-Accel-Buffering"] = "no"

    return response