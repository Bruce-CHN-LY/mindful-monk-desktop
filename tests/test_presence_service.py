from datetime import time

import pytest

from app.core.presence_service import PresenceService


@pytest.mark.parametrize(
    ("value", "expected"),
    [("00:00", time(0, 0)), ("07:30", time(7, 30)), ("23:59", time(23, 59))],
)
def test_parse_time_accepts_valid_values(value, expected):
    assert PresenceService._parse_time(value) == expected


@pytest.mark.parametrize("value", ["24:00", "12:60", "bad", None])
def test_parse_time_rejects_invalid_values(value):
    with pytest.raises((TypeError, ValueError)):
        PresenceService._parse_time(value)


def test_invalid_quiet_hours_do_not_suppress_reminders():
    service = PresenceService()
    assert not service.is_quiet_hours(
        {"quiet_hours_enabled": True, "quiet_start": "bad", "quiet_end": "07:00"}
    )
