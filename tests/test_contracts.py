from app.contracts import SearchHit, Ticket
from app.knowledge import search_manual
from app.store import create_ticket

def test_contract_matches_search():
    assert [SearchHit.model_validate(d) for d in search_manual("500")]

def test_contract_matches_create():
    Ticket.model_validate(create_ticket("API error 500", "Repeated 500 response", "request-123"))
