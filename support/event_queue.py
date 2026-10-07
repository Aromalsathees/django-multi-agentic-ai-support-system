import queue


subscribers = {} # {5: [queue_1, queue_2], 24: [queue_3]}


def subscribe(conversation_id):
    q = queue.Queue() # create an empty queue for this browser tab

    if conversation_id not in subscribers:
        subscribers[conversation_id] = []

    subscribers[conversation_id].append(q)
    return q


def unsubscribe(conversation_id, q):
    if conversation_id in subscribers:
        subscribers[conversation_id].remove(q)
        if not subscribers[conversation_id]:
            del subscribers[conversation_id]



def publish(conversation_id, event):
    if conversation_id in subscribers:
        for q in subscribers[conversation_id]:
            q.put(event)


# Sentinel value - it tells SSE stream to stop
DONE = {"type": "done"}