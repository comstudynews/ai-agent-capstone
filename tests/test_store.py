from app.store import create_ticket, search_tickets, remember, history

def test_idempotent_ticket():
    x = create_ticket("API error 500", "Repeated 500 response", "request-123")
    y = create_ticket("API error 500", "Repeated 500 response", "request-123")
    assert x["created"] and not y["created"]
    assert x["ticket_id"] == y["ticket_id"]
    assert len(search_tickets("API")) == 1

def test_thread_isolation():
    remember("thread-a", "user", "secret a")
    remember("thread-b", "user", "secret b")
    assert history("thread-a") == [{"role": "user", "content": "secret a"}]
