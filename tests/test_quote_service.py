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


def test_quote_service_keeps_category_filter_when_recent_pool_is_exhausted():
    service = QuoteService(DummyQuoteStore())

    assert service.next_quote(["mind"])["category"] == "mind"
    assert service.next_quote(["mind"])["category"] == "mind"


def test_quote_service_returns_fallback_when_category_has_no_quotes():
    quote = QuoteService(DummyQuoteStore()).next_quote(["missing"])

    assert quote == {"text": "轻轻看一眼这一念。", "category": "mind"}
