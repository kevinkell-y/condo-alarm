class Siren:
    def __init__(self, state):
        self.state = state

    def on(self):
        if self.state.siren_muted:
            print("[SIREN] muted (no sound)")
            return

        self.state.siren_active = True
        print(f"[SIREN] ON (volume={self.state.siren_volume})")

    def off(self):
        self.state.siren_active = False
        print("[SIREN] OFF")