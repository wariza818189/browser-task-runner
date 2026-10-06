"""Shared ordered step recording and sanitized workflow errors."""
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


class WorkflowFailure(RuntimeError):
    def __init__(self, kind: str, message: str):
        super().__init__(message)
        self.kind = kind


def run_step(steps: list[dict[str, str]], name: str, action: Callable[[], T]) -> T:
    record = {"name": name, "status": "running"}
    steps.append(record)
    try:
        value = action()
    except Exception:
        record["status"] = "failed"
        raise
    record["status"] = "success"
    return value
