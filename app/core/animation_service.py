from app.core.state_machine import PetState


class AnimationService:
    def pose_for_state(self, state: PetState) -> str:
        mapping = {
            PetState.IDLE: "idle",
            PetState.REMINDING: "prayer",
            PetState.BREATHING: "breathing",
            PetState.MANUAL_BELL: "bell",
            PetState.MENU_OPEN: "idle",
        }
        return mapping.get(state, "idle")
