
import queue
from collections import defaultdict
from threading import Lock

subscribers = defaultdict(list)
subscribers_lock = Lock()

DONE = {"type": "done"}


def subscribe(conversation_id):
    q = queue.Queue()

    with subscribers_lock:
        subscribers[conversation_id].append(q)

    return q


def unsubscribe(conversation_id, q):
    with subscribers_lock:
        queues = subscribers.get(conversation_id, [])

        if q in queues:
            queues.remove(q)

        if not queues:
            subscribers.pop(conversation_id, None)


def publish(conversation_id, event):
    with subscribers_lock:
        queues = list(subscribers.get(conversation_id, []))

    for q in queues:
        q.put(event)