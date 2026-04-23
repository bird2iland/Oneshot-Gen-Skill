from typing import Optional


class PresetCombinationValidator:
    CONFLICTS = [
        ("slow_motion", "timelapse", "Time effect conflict: slow_motion and timelapse are incompatible"),
        ("timelapse", "slow_motion", "Time effect conflict: timelapse and slow_motion are incompatible"),
        ("handheld", "gimbal", "Camera style conflict: handheld and gimbal are incompatible"),
        ("gimbal", "handheld", "Camera style conflict: gimbal and handheld are incompatible"),
    ]

    def __init__(self, visual: Optional[str], time: Optional[str], camera: Optional[str]):
        self._visual = visual
        self._time = time
        self._camera = camera

    async def validate(self) -> list[str]:
        warnings: list[str] = []
        presets = [p for p in [self._visual, self._time, self._camera] if p]

        for preset1 in presets:
            for preset2 in presets:
                if preset1 != preset2:
                    for conflict in self.CONFLICTS:
                        if preset1 == conflict[0] and preset2 == conflict[1]:
                            if conflict[2] not in warnings:
                                warnings.append(conflict[2])

        return warnings