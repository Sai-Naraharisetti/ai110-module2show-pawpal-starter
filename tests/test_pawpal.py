"""
tests/test_pawpal.py - Unit tests for PawPal+ core classes.

Tests verify key behaviors:
- Task completion status changes
- Task addition to pets
"""

import pytest
from pawpal_system import Task, Pet, Owner, Scheduler, DailyPlan


class TestTask:
    """Tests for Task class."""
    
    def test_mark_complete(self):
        """Verify that mark_complete() changes task status to 'complete'."""
        # Arrange
        task = Task(
            title="Morning walk",
            duration_minutes=20,
            priority="high",
            category="exercise"
        )
        
        # Assert initial state
        assert task.completion_status == "incomplete"
        
        # Act
        task.mark_complete()
        
        # Assert final state
        assert task.completion_status == "complete"
    
    def test_is_urgent(self):
        """Verify that is_urgent() returns True only for high priority tasks."""
        # Arrange
        high_priority = Task(
            title="Medication",
            duration_minutes=5,
            priority="high",
            category="medication"
        )
        low_priority = Task(
            title="Play time",
            duration_minutes=30,
            priority="low",
            category="enrichment"
        )
        
        # Act & Assert
        assert high_priority.is_urgent() is True
        assert low_priority.is_urgent() is False
    
    def test_matches_window(self):
        """Verify that matches_window() correctly identifies window matches."""
        # Arrange
        morning_task = Task(
            title="Breakfast",
            duration_minutes=10,
            priority="high",
            category="feeding",
            preferred_window="morning"
        )
        any_window_task = Task(
            title="Grooming",
            duration_minutes=15,
            priority="medium",
            category="grooming",
            preferred_window="any"
        )
        
        # Act & Assert
        assert morning_task.matches_window("morning") is True
        assert morning_task.matches_window("afternoon") is False
        assert any_window_task.matches_window("morning") is True
        assert any_window_task.matches_window("afternoon") is True


class TestPet:
    """Tests for Pet class."""
    
    def test_add_task_increases_count(self):
        """Verify that adding a task to a Pet increases task count."""
        # Arrange
        pet = Pet(name="Fluffy", species="dog", energy_level="high")
        initial_count = len(pet.tasks)
        
        # Act
        task = Task(
            title="Morning walk",
            duration_minutes=20,
            priority="high",
            category="exercise"
        )
        pet.add_task(task)
        
        # Assert
        assert len(pet.tasks) == initial_count + 1
        assert pet.tasks[0] == task
    
    def test_add_multiple_tasks(self):
        """Verify that multiple tasks can be added correctly."""
        # Arrange
        pet = Pet(name="Whiskers", species="cat", energy_level="low")
        
        task1 = Task(
            title="Breakfast",
            duration_minutes=5,
            priority="high",
            category="feeding"
        )
        task2 = Task(
            title="Litter box",
            duration_minutes=10,
            priority="high",
            category="grooming"
        )
        
        # Act
        pet.add_task(task1)
        pet.add_task(task2)
        
        # Assert
        assert len(pet.tasks) == 2
        assert pet.tasks[0].title == "Breakfast"
        assert pet.tasks[1].title == "Litter box"
    
    def test_remove_task(self):
        """Verify that remove_task() correctly removes tasks."""
        # Arrange
        pet = Pet(name="Max", species="dog", energy_level="medium")
        task = Task(
            title="Training",
            duration_minutes=15,
            priority="medium",
            category="enrichment"
        )
        pet.add_task(task)
        
        # Act
        removed = pet.remove_task("Training")
        
        # Assert
        assert removed is True
        assert len(pet.tasks) == 0
    
    def test_get_incomplete_tasks(self):
        """Verify that get_incomplete_tasks() returns only incomplete tasks."""
        # Arrange
        pet = Pet(name="Buddy", species="dog")
        
        task1 = Task(
            title="Walk",
            duration_minutes=20,
            priority="high",
            category="exercise"
        )
        task2 = Task(
            title="Play",
            duration_minutes=15,
            priority="medium",
            category="enrichment"
        )
        
        pet.add_task(task1)
        pet.add_task(task2)
        task1.mark_complete()
        
        # Act
        incomplete = pet.get_incomplete_tasks()
        
        # Assert
        assert len(incomplete) == 1
        assert incomplete[0].title == "Play"


class TestOwner:
    """Tests for Owner class."""
    
    def test_add_pet(self):
        """Verify that pets can be added to an owner."""
        # Arrange
        owner = Owner(
            name="Jordan",
            available_minutes=120,
            focus_window="morning"
        )
        pet = Pet(name="Fluffy", species="dog")
        
        # Act
        owner.add_pet(pet)
        
        # Assert
        assert owner.total_pet_count() == 1
        assert owner.pets[0] == pet
    
    def test_get_all_tasks_across_pets(self):
        """Verify that get_all_tasks() retrieves tasks from all pets."""
        # Arrange
        owner = Owner(name="Sarah", available_minutes=150)
        
        dog = Pet(name="Rex", species="dog")
        cat = Pet(name="Mittens", species="cat")
        
        dog_task = Task(
            title="Walk",
            duration_minutes=20,
            priority="high",
            category="exercise"
        )
        cat_task = Task(
            title="Feed",
            duration_minutes=5,
            priority="high",
            category="feeding"
        )
        
        dog.add_task(dog_task)
        cat.add_task(cat_task)
        
        owner.add_pet(dog)
        owner.add_pet(cat)
        
        # Act
        all_tasks = owner.get_all_tasks()
        
        # Assert
        assert len(all_tasks) == 2
        assert dog_task in all_tasks
        assert cat_task in all_tasks


class TestScheduler:
    """Tests for Scheduler class."""
    
    def test_scheduler_initialization(self):
        """Verify that Scheduler initializes correctly."""
        # Arrange & Act
        owner = Owner(
            name="Jordan",
            available_minutes=120,
            focus_window="morning"
        )
        scheduler = Scheduler(owner=owner, start_hour=8)
        
        # Assert
        assert scheduler.owner == owner
        assert scheduler.start_hour == 8
    
    def test_format_time(self):
        """Verify that format_time() produces correct HH:MM format."""
        # Arrange
        owner = Owner(name="Test", available_minutes=100)
        scheduler = Scheduler(owner=owner)
        
        # Act & Assert
        assert scheduler.format_time(0) == "00:00"
        assert scheduler.format_time(480) == "08:00"  # 8 AM
        assert scheduler.format_time(870) == "14:30"  # 2:30 PM
        assert scheduler.format_time(1439) == "23:59" # 11:59 PM
    
    def test_score_task_high_priority(self):
        """Verify that high priority tasks score higher."""
        # Arrange
        owner = Owner(
            name="Jordan",
            available_minutes=120,
            focus_window="morning"
        )
        pet = Pet(name="Fluffy", species="dog", energy_level="high")
        owner.add_pet(pet)
        
        high_task = Task(
            title="Medication",
            duration_minutes=5,
            priority="high",
            category="medication"
        )
        low_task = Task(
            title="Play",
            duration_minutes=20,
            priority="low",
            category="enrichment"
        )
        
        scheduler = Scheduler(owner=owner)
        
        # Act
        high_score = scheduler.score_task(high_task, pet)
        low_score = scheduler.score_task(low_task, pet)
        
        # Assert
        assert high_score > low_score
    
    def test_build_daily_plan_empty_tasks(self):
        """Verify that build_daily_plan handles empty task list."""
        # Arrange
        owner = Owner(name="Jordan", available_minutes=120)
        scheduler = Scheduler(owner=owner)
        
        # Act
        plan = scheduler.build_daily_plan([])
        
        # Assert
        assert isinstance(plan, DailyPlan)
        assert len(plan.scheduled) == 0
        assert len(plan.skipped) == 0
        assert plan.total_minutes == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
