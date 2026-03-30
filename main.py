#!/usr/bin/env python3
"""
main.py - Testing ground for PawPal+ scheduling logic.

This script demonstrates the full workflow:
1. Create an owner with pets
2. Add tasks to pets
3. Generate a daily schedule
4. Display results in a readable format
"""

from pawpal_system import Owner, Pet, Task, Scheduler, PawPalService, PlanExplainer


def print_schedule_header(owner_name: str, pet_names: list, available_time: int) -> None:
    """Print a formatted header for the schedule."""
    print("\n" + "=" * 70)
    print(f"  🐾 PawPal+ Daily Schedule")
    print("=" * 70)
    print(f"  Owner: {owner_name}")
    print(f"  Pets: {', '.join(pet_names)}")
    print(f"  Available Time: {available_time} minutes ({available_time / 60:.1f} hours)")
    print("=" * 70 + "\n")


def print_scheduled_tasks(scheduled: list) -> None:
    """Print scheduled tasks in a readable format."""
    if not scheduled:
        print("  ⚠️  No tasks scheduled.\n")
        return
    
    print("  📅 SCHEDULED TASKS:")
    print("  " + "-" * 66)
    
    for i, task in enumerate(scheduled, 1):
        print(f"\n  {i}. {task.title}")
        print(f"     Category: {task.category} | Priority: {task.priority.upper()}")
        print(f"     Time: {task.start_label} – {task.end_label} ({task.duration_minutes} min)")
        print(f"     Why: {task.reason}")
    
    print("\n  " + "-" * 66 + "\n")


def print_skipped_tasks(skipped: list) -> None:
    """Print skipped tasks with reasons."""
    if not skipped:
        print("  ✓ All tasks scheduled!\n")
        return
    
    print("  ⏭️  SKIPPED TASKS:")
    print("  " + "-" * 66)
    
    for i, item in enumerate(skipped, 1):
        print(f"\n  {i}. {item['title']} ({item['priority'].upper()} priority)")
        print(f"     Reason: {item['reason']}")
    
    print("\n  " + "-" * 66 + "\n")


def print_summary(plan, available_time: int) -> None:
    """Print summary statistics."""
    remaining = available_time - plan.total_minutes
    
    print("  📊 SUMMARY:")
    print(f"     Total scheduled: {plan.total_minutes} minutes")
    print(f"     Tasks scheduled: {len(plan.scheduled)}")
    print(f"     Tasks skipped: {len(plan.skipped)}")
    print(f"     Time remaining: {remaining} minutes")
    print("\n" + "=" * 70 + "\n")


def main() -> None:
    """Main testing scenario."""
    
    # Create owner
    owner = Owner(
        name="Jordan",
        available_minutes=120,
        focus_window="morning",
        break_minutes=5
    )
    
    # Create pets
    fluffy = Pet(name="Fluffy", species="dog", energy_level="high")
    whiskers = Pet(name="Whiskers", species="cat", energy_level="low")
    
    owner.add_pet(fluffy)
    owner.add_pet(whiskers)
    
    # Add tasks to Fluffy (dog)
    fluffy.add_task(Task(
        title="Morning walk",
        duration_minutes=20,
        priority="high",
        category="exercise",
        preferred_window="morning"
    ))
    
    fluffy.add_task(Task(
        title="Breakfast feeding",
        duration_minutes=10,
        priority="high",
        category="feeding",
        preferred_window="morning"
    ))
    
    fluffy.add_task(Task(
        title="Play fetch",
        duration_minutes=25,
        priority="medium",
        category="exercise",
        preferred_window="morning"
    ))
    
    # Add tasks to Whiskers (cat)
    whiskers.add_task(Task(
        title="Breakfast feeding",
        duration_minutes=5,
        priority="high",
        category="feeding",
        preferred_window="morning"
    ))
    
    whiskers.add_task(Task(
        title="Litter box clean",
        duration_minutes=10,
        priority="high",
        category="grooming",
        preferred_window="any"
    ))
    
    whiskers.add_task(Task(
        title="Afternoon nap supervision",
        duration_minutes=30,
        priority="low",
        category="enrichment",
        preferred_window="afternoon"
    ))
    
    # Get all tasks
    all_tasks = owner.get_all_tasks()
    
    # Create scheduler and generate plan
    scheduler = Scheduler(owner=owner, start_hour=8)
    plan = scheduler.build_daily_plan(all_tasks)
    
    # Print schedule in readable format
    pet_names = [pet.name for pet in owner.pets]
    print_schedule_header(owner.name, pet_names, owner.available_minutes)
    print_scheduled_tasks(plan.scheduled)
    print_skipped_tasks(plan.skipped)
    print_summary(plan, owner.available_minutes)
    
    # Optional: Print task summary
    summary = scheduler.get_task_summary()
    print("  📈 TASK SUMMARY ACROSS ALL PETS:")
    print(f"     Total tasks: {summary['total_tasks']}")
    print(f"     High priority: {summary['high_priority']}")
    print(f"     Medium priority: {summary['medium_priority']}")
    print(f"     Low priority: {summary['low_priority']}")
    print(f"     Completed: {summary['completed']} | Incomplete: {summary['incomplete']}")
    print("\n")


if __name__ == "__main__":
    main()
