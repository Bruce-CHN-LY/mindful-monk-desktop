from app.core.quote_service import QuoteService


class DummyQuoteStore:
    def load_quotes(self):
        return [
            {"id": "a", "text": "A", "category": "mind", "weight": 1, "enabled": True},
            {"id": "b", "text": "B", "category": "breath", "weight": 1, "enabled": True},
        ]


def test_quote_service_returns_enabled_quote():
    service = QuoteService(DummyQuoteStore())
    quote = service.next_quote(["mind"])
    assert quote["category"] == "mind"


def test_quote_service_tolerates_invalid_weight():
    class InvalidWeightStore:
        def load_quotes(self):
            return [{"id": "a", "text": "A", "weight": "unknown", "enabled": True}]

    assert QuoteService(InvalidWeightStore()).next_quote()["text"] == "A"
