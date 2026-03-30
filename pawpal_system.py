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
    completion_status: Literal["incomplete", "complete"] = "incomplete"
    
    def mark_complete(self) -> None:
        """Mark this task as complete."""
        self.completion_status = "complete"
    
    def is_urgent(self) -> bool:
        """Return True if task has high priority."""
        return self.priority == "high"
    
    def matches_window(self, window: TimeWindow) -> bool:
        """Return True if task's preferred window matches the given window."""
        if self.preferred_window == "any":
            return True
        return self.preferred_window == window
    
    def duration_hours(self) -> float:
        """Return task duration in hours."""
        return self.duration_minutes / 60.0


@dataclass
class Pet:
    name: str
    species: str
    energy_level: Literal["low", "medium", "high"] = "medium"
    tasks: List[Task] = field(default_factory=list)
    
    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        if not isinstance(task, Task):
            raise TypeError(f"Expected Task object, got {type(task).__name__}")
        self.tasks.append(task)
    
    def remove_task(self, title: str) -> bool:
        """Remove task by title. Return True if removed, False if not found."""
        original_length = len(self.tasks)
        self.tasks = [task for task in self.tasks if task.title != title]
        return len(self.tasks) < original_length
    
    def get_tasks_by_priority(self, priority: Priority) -> List[Task]:
        """Get all tasks with specified priority level."""
        return [task for task in self.tasks if task.priority == priority]
    
    def get_incomplete_tasks(self) -> List[Task]:
        """Get all incomplete tasks."""
        return [task for task in self.tasks if task.completion_status == "incomplete"]


@dataclass
class Owner:
    name: str
    available_minutes: int
    focus_window: Literal["morning", "afternoon", "evening"] = "morning"
    break_minutes: int = 5
    pets: List[Pet] = field(default_factory=list)
    
    def add_pet(self, pet: Pet) -> None:
        """Add a pet to owner's pet list."""
        if not isinstance(pet, Pet):
            raise TypeError(f"Expected Pet object, got {type(pet).__name__}")
        self.pets.append(pet)
    
    def get_all_tasks(self) -> List[Task]:
        """Get all tasks from all pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks
    
    def get_tasks_for_pet(self, pet_name: str) -> List[Task]:
        """Get all tasks for a specific pet by name."""
        for pet in self.pets:
            if pet.name == pet_name:
                return pet.tasks
        return []
    
    def total_pet_count(self) -> int:
        """Return total number of pets."""
        return len(self.pets)


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
    # Scoring constants
    PRIORITY_WEIGHTS = {"low": 1, "medium": 5, "high": 10}
    WINDOW_MATCH_WEIGHT = 5
    ENERGY_LEVEL_WEIGHTS = {"low": 1, "medium": 2, "high": 3}
    DURATION_PENALTY_FACTOR = 0.05
    
    def __init__(self, owner: Owner, start_hour: int = 8) -> None:
        """Initialize scheduler with owner and start time.
        
        Args:
            owner: Owner instance managing the pets
            start_hour: Hour of day when scheduling starts (0-23)
        """
        if not isinstance(owner, Owner):
            raise TypeError(f"Expected Owner object, got {type(owner).__name__}")
        if not 0 <= start_hour <= 23:
            raise ValueError(f"start_hour must be between 0 and 23, got {start_hour}")
        
        self.owner = owner
        self.start_hour = start_hour
    
    def validate_task(self, task: Task) -> None:
        """Validate task has required fields.
        
        Args:
            task: Task to validate
            
        Raises:
            TypeError: If task is not a Task instance
            ValueError: If task has invalid fields
        """
        if not isinstance(task, Task):
            raise TypeError(f"Expected Task object, got {type(task).__name__}")
        if task.duration_minutes <= 0:
            raise ValueError(f"duration_minutes must be positive, got {task.duration_minutes}")
        if not task.title.strip():
            raise ValueError("Task title cannot be empty")
    
    def score_task(self, task: Task, pet: Pet) -> int:
        """Score a task based on multiple factors.
        
        Scoring algorithm:
        - Priority: 1-10 points based on priority level
        - Window match: +5 points if preferred_window matches owner's focus_window
        - Energy level: 1-3 points based on pet's energy level fit
        - Duration penalty: -0.05 per minute
        
        Args:
            task: Task to score
            pet: Pet associated with the task
            
        Returns:
            Numeric score (higher is better)
        """
        self.validate_task(task)
        
        score = 0
        
        # Priority component
        score += self.PRIORITY_WEIGHTS.get(task.priority, 0)
        
        # Window matching component
        if task.matches_window(self.owner.focus_window):
            score += self.WINDOW_MATCH_WEIGHT
        
        # Energy level component - higher energy pet is better for longer tasks
        score += self.ENERGY_LEVEL_WEIGHTS.get(pet.energy_level, 0)
        
        # Duration penalty - longer tasks get lower scores
        score -= task.duration_minutes * self.DURATION_PENALTY_FACTOR
        
        return max(0, int(score))
    
    def rank_tasks(self, tasks: List[Task]) -> List[Task]:
        """Rank tasks by score in descending order.
        
        Args:
            tasks: List of tasks to rank
            
        Returns:
            List of tasks sorted by score (highest first)
        """
        if not self.owner.pets:
            raise ValueError("Owner has no pets to rank tasks for")
        
        # Use first pet for scoring if multiple tasks
        pet = self.owner.pets[0]
        
        ranked = sorted(
            tasks,
            key=lambda t: self.score_task(t, pet),
            reverse=True
        )
        return ranked
    
    def format_time(self, minute_of_day: int) -> str:
        """Format minutes since midnight into HH:MM format.
        
        Args:
            minute_of_day: Minutes since midnight (0-1439)
            
        Returns:
            Formatted time string (e.g., "08:30")
        """
        if not 0 <= minute_of_day < 1440:
            raise ValueError(f"minute_of_day must be 0-1439, got {minute_of_day}")
        
        hours = minute_of_day // 60
        minutes = minute_of_day % 60
        return f"{hours:02d}:{minutes:02d}"
    
    def allocate_time(self, tasks: List[Task]) -> Dict[str, Any]:
        """Allocate available time among tasks respecting breaks.
        
        Args:
            tasks: List of tasks to allocate time for
            
        Returns:
            Dictionary with 'allocated' (list of scheduled tasks) and 
            'remaining_minutes' (unused time)
        """
        allocated = []
        remaining_minutes = self.owner.available_minutes
        current_minute = self.start_hour * 60
        
        for task in tasks:
            # Check if task fits with breaks
            total_needed = task.duration_minutes + self.owner.break_minutes
            
            if remaining_minutes >= total_needed:
                allocated.append({
                    "task": task,
                    "start_minute": current_minute,
                    "end_minute": current_minute + task.duration_minutes
                })
                current_minute += total_needed
                remaining_minutes -= total_needed
            # Also allocate if we can fit without break (last task)
            elif remaining_minutes >= task.duration_minutes:
                allocated.append({
                    "task": task,
                    "start_minute": current_minute,
                    "end_minute": current_minute + task.duration_minutes
                })
                remaining_minutes -= task.duration_minutes
        
        return {
            "allocated": allocated,
            "remaining_minutes": max(0, remaining_minutes)
        }
    
    def build_daily_plan(self, tasks: List[Task]) -> DailyPlan:
        """Build a daily plan with scheduled tasks and skip reasons.
        
        Args:
            tasks: List of tasks to schedule
            
        Returns:
            DailyPlan object with scheduled tasks and skipped items
        """
        plan = DailyPlan()
        
        if not tasks:
            return plan
        
        # Rank tasks by priority and fit
        ranked_tasks = self.rank_tasks(tasks)
        
        # Allocate time
        allocation = self.allocate_time(ranked_tasks)
        scheduled_items = allocation["allocated"]
        
        # Build scheduled tasks
        total_minutes = 0
        for item in scheduled_items:
            task = item["task"]
            start_time = self.format_time(item["start_minute"])
            end_time = self.format_time(item["end_minute"])
            
            scheduled_task = ScheduledTask(
                title=task.title,
                start_label=start_time,
                end_label=end_time,
                duration_minutes=task.duration_minutes,
                priority=task.priority,
                category=task.category,
                reason=f"Scheduled in {self.owner.focus_window} window"
            )
            plan.scheduled.append(scheduled_task)
            total_minutes += task.duration_minutes
        
        # Determine skipped tasks
        scheduled_titles = {item["task"].title for item in scheduled_items}
        for task in ranked_tasks:
            if task.title not in scheduled_titles:
                skip_reason = "Insufficient time available"
                if not task.matches_window(self.owner.focus_window):
                    skip_reason = f"Not scheduled for {self.owner.focus_window}"
                
                plan.skipped.append({
                    "title": task.title,
                    "priority": task.priority,
                    "reason": skip_reason
                })
        
        plan.total_minutes = total_minutes
        return plan
    
    def sort_tasks_by_time(self, scheduled_tasks: List[ScheduledTask]) -> List[ScheduledTask]:
        """Sort scheduled tasks chronologically by start time.
        
        Uses lambda function to parse HH:MM format and sort by minutes since midnight.
        
        Args:
            scheduled_tasks: List of ScheduledTask objects to sort
            
        Returns:
            List of tasks sorted by start time (earliest first)
        """
        def time_to_minutes(time_str: str) -> int:
            """Convert HH:MM format to minutes since midnight."""
            hours, minutes = map(int, time_str.split(":"))
            return hours * 60 + minutes
        
        return sorted(
            scheduled_tasks,
            key=lambda task: time_to_minutes(task.start_label)
        )
    
    def filter_tasks_by_status(self, tasks: List[Task], status: Literal["complete", "incomplete"]) -> List[Task]:
        """Filter tasks by completion status.
        
        Args:
            tasks: List of tasks to filter
            status: Status to filter by ('complete' or 'incomplete')
            
        Returns:
            Filtered list of tasks matching the status
        """
        return [task for task in tasks if task.completion_status == status]
    
    def filter_tasks_by_category(self, tasks: List[Task], category: str) -> List[Task]:
        """Filter tasks by category.
        
        Args:
            tasks: List of tasks to filter
            category: Category to filter by
            
        Returns:
            Filtered list of tasks matching the category
        """
        return [task for task in tasks if task.category.lower() == category.lower()]
    
    def detect_conflicts(self, scheduled_tasks: List[ScheduledTask]) -> List[Dict[str, Any]]:
        """Detect if any tasks are scheduled at the same time.
        
        Lightweight conflict detection: checks for exact start time matches.
        Returns warnings rather than blocking the schedule.
        
        Args:
            scheduled_tasks: List of scheduled tasks to check
            
        Returns:
            List of conflict warnings (empty if no conflicts)
        """
        conflicts = []
        
        # Create a mapping of start times to tasks
        time_map: Dict[str, List[ScheduledTask]] = {}
        
        for task in scheduled_tasks:
            start = task.start_label
            if start not in time_map:
                time_map[start] = []
            time_map[start].append(task)
        
        # Find conflicts (multiple tasks at same start time)
        for start_time, tasks_at_time in time_map.items():
            if len(tasks_at_time) > 1:
                task_names = [t.title for t in tasks_at_time]
                conflicts.append({
                    "time": start_time,
                    "task_count": len(tasks_at_time),
                    "tasks": task_names,
                    "warning": f"⚠️  {len(tasks_at_time)} tasks scheduled at {start_time}: {', '.join(task_names)}"
                })
        
        return conflicts
    
    def get_task_summary(self) -> Dict[str, Any]:
        """Get summary of all tasks across all pets.
        
        Returns:
            Dictionary with task counts by priority and status
        """
        all_tasks = self.owner.get_all_tasks()
        
        summary = {
            "total_tasks": len(all_tasks),
            "high_priority": len([t for t in all_tasks if t.priority == "high"]),
            "medium_priority": len([t for t in all_tasks if t.priority == "medium"]),
            "low_priority": len([t for t in all_tasks if t.priority == "low"]),
            "completed": len([t for t in all_tasks if t.completion_status == "complete"]),
            "incomplete": len([t for t in all_tasks if t.completion_status == "incomplete"])
        }
        return summary


class PlanExplainer:
    """Provides human-readable explanations for plan components."""
    
    def explain_scheduled_task(self, task: ScheduledTask) -> str:
        """Generate explanation for a scheduled task.
        
        Args:
            task: ScheduledTask to explain
            
        Returns:
            Human-readable explanation string
        """
        return (
            f"{task.title} ({task.category}) scheduled from {task.start_label} to "
            f"{task.end_label} ({task.duration_minutes} min, {task.priority} priority). "
            f"Reason: {task.reason}"
        )
    
    def explain_skipped_task(self, skipped_item: Dict[str, str]) -> str:
        """Generate explanation for a skipped task.
        
        Args:
            skipped_item: Dictionary with task skip information
            
        Returns:
            Human-readable explanation string
        """
        return (
            f"{skipped_item['title']} ({skipped_item['priority']} priority) was skipped. "
            f"Reason: {skipped_item['reason']}"
        )


class TaskFactory:
    """Factory for creating Task objects from dictionaries."""
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> Task:
        """Create a Task from a dictionary.
        
        Args:
            data: Dictionary with task fields (title, duration_minutes, priority, 
                  category, preferred_window, completion_status)
        
        Returns:
            Task object
            
        Raises:
            ValueError: If required fields are missing
            TypeError: If field types are invalid
        """
        required_fields = ["title", "duration_minutes", "priority", "category"]
        missing = [f for f in required_fields if f not in data]
        if missing:
            raise ValueError(f"Missing required fields: {missing}")
        
        try:
            task = Task(
                title=str(data["title"]),
                duration_minutes=int(data["duration_minutes"]),
                priority=data.get("priority", "low"),
                category=str(data.get("category", "general")),
                preferred_window=data.get("preferred_window", "any"),
                completion_status=data.get("completion_status", "incomplete")
            )
            return task
        except (ValueError, TypeError) as e:
            raise TypeError(f"Invalid task data: {e}")
    
    @staticmethod
    def list_from_dicts(items: List[Dict[str, Any]]) -> List[Task]:
        """Create multiple Tasks from a list of dictionaries.
        
        Args:
            items: List of dictionaries with task fields
            
        Returns:
            List of Task objects
        """
        return [TaskFactory.from_dict(item) for item in items]


class PawPalService:
    """Main service orchestrating task scheduling and planning."""
    
    def __init__(self, scheduler: Scheduler, explainer: Optional[PlanExplainer] = None) -> None:
        """Initialize PawPal service.
        
        Args:
            scheduler: Scheduler instance to use for planning
            explainer: Optional PlanExplainer for human-readable outputs
        """
        if not isinstance(scheduler, Scheduler):
            raise TypeError(f"Expected Scheduler object, got {type(scheduler).__name__}")
        
        self.scheduler = scheduler
        self.explainer = explainer or PlanExplainer()
    
    def generate_plan(self, tasks: List[Task]) -> DailyPlan:
        """Generate a daily plan for given tasks.
        
        Args:
            tasks: List of tasks to schedule
            
        Returns:
            DailyPlan with scheduled and skipped tasks
        """
        if not tasks:
            return DailyPlan()
        
        # Validate all tasks
        for task in tasks:
            self.scheduler.validate_task(task)
        
        return self.scheduler.build_daily_plan(tasks)
    
    def summarize_plan(self, plan: DailyPlan) -> Dict[str, Any]:
        """Generate summary statistics for a plan.
        
        Args:
            plan: DailyPlan to summarize
            
        Returns:
            Dictionary with plan statistics and explanations
        """
        scheduled_explanations = [
            self.explainer.explain_scheduled_task(task)
            for task in plan.scheduled
        ]
        
        skipped_explanations = [
            self.explainer.explain_skipped_task(item)
            for item in plan.skipped
        ]
        
        return {
            "total_minutes_allocated": plan.total_minutes,
            "tasks_scheduled": len(plan.scheduled),
            "tasks_skipped": len(plan.skipped),
            "scheduled": scheduled_explanations,
            "skipped": skipped_explanations,
            "available_minutes": self.scheduler.owner.available_minutes,
            "remaining_minutes": self.scheduler.owner.available_minutes - plan.total_minutes
        }
