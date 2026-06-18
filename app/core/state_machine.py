from enum import Enum


class PetState(str, Enum):
    IDLE = "idle"
    REMINDING = "reminding"
    BREATHING = "breathing"
    MANUAL_BELL = "manual_bell"
    MENU_OPEN = "menu_open"
