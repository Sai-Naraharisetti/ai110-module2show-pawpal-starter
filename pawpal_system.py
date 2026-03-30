from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional


Priority = Literal["low", "medium", "high"]
TimeWindow = Literal["any", "morning", "afternoon", "evening"]


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: Priority
    category: str
    preferred_window: TimeWindow = "any"


@dataclass
class Pet:
    name: str
    species: str
    energy_level: Literal["low", "medium", "high"] = "medium"


@dataclass
class Owner:
    name: str
    available_minutes: int
    focus_window: Literal["morning", "afternoon", "evening"] = "morning"
    break_minutes: int = 5


@dataclass
class ScheduledTask:
    title: str
    start_label: str
    end_label: str
    duration_minutes: int
    priority: Priority
    category: str
    reason: str


@dataclass
class DailyPlan:
    scheduled: List[ScheduledTask] = field(default_factory=list)
    skipped: List[Dict[str, str]] = field(default_factory=list)
    total_minutes: int = 0


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet, start_hour: int = 8) -> None:
        self.owner = owner
        self.pet = pet
        self.start_hour = start_hour

    def validate_task(self, task: Task) -> None:
        raise NotImplementedError

    def rank_tasks(self, tasks: List[Task]) -> List[Task]:
        raise NotImplementedError

    def score_task(self, task: Task) -> int:
        raise NotImplementedError

    def format_time(self, minute_of_day: int) -> str:
        raise NotImplementedError

    def build_daily_plan(self, tasks: List[Task]) -> DailyPlan:
        raise NotImplementedError


class PlanExplainer:
    def explain_scheduled_task(self, task: ScheduledTask) -> str:
        raise NotImplementedError

    def explain_skipped_task(self, skipped_item: Dict[str, str]) -> str:
        raise NotImplementedError


class TaskFactory:
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> Task:
        raise NotImplementedError

    @staticmethod
    def list_from_dicts(items: List[Dict[str, Any]]) -> List[Task]:
        raise NotImplementedError


class PawPalService:
    def __init__(self, scheduler: Scheduler, explainer: Optional[PlanExplainer] = None) -> None:
        self.scheduler = scheduler
        self.explainer = explainer

    def generate_plan(self, tasks: List[Task]) -> DailyPlan:
        raise NotImplementedError

    def summarize_plan(self, plan: DailyPlan) -> Dict[str, Any]:
        raise NotImplementedError
