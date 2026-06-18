from app.core.presence_service import PresenceService


def test_presence_service_quiet_hours_returns_bool():
    service = PresenceService()
    result = service.is_quiet_hours(
        {
            "quiet_hours_enabled": True,
            "quiet_start": "22:30",
            "quiet_end": "07:00",
        }
    )
    assert isinstance(result, bool)
