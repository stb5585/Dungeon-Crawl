"""Focused core coverage for concealment and Detect."""

from types import SimpleNamespace

from src.core.combat.visibility import conceal, detect, detect_chance, is_revealed_to


class _Rng:
    def __init__(self, value: float) -> None:
        self.value = value

    def random(self) -> float:
        return self.value


def test_detect_uses_wisdom_bounds_and_records_observation():
    observer = SimpleNamespace(stats=SimpleNamespace(wisdom=14), sight=False)
    target = SimpleNamespace()
    conceal(target)

    assert detect_chance(observer, target) == 0.60
    assert detect(observer, target, rng=_Rng(0.59)) is True
    assert is_revealed_to(observer, target) is True


def test_sight_reveals_concealed_opponents_without_mutating_them():
    observer = SimpleNamespace(stats=SimpleNamespace(wisdom=10), sight=True)
    target = SimpleNamespace()
    conceal(target)

    assert is_revealed_to(observer, target) is True
