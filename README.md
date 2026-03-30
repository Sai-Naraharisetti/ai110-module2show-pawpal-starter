# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Features

### Core Scheduling Capabilities

**Intelligent Task Scheduling**
- Generates daily care plans that respect time, priority, and pet energy constraints
- Uses weighted multi-factor scoring to rank tasks by importance and suitability
- Allocates tasks to available time slots with automatic 15-minute break management
- Explains reasoning for every scheduling decision (why each task was chosen or skipped)

### Algorithm Details

#### 1. **Weighted Priority Scoring**
Each task receives a composite score based on:
- **Priority Weight** (1-10 points): Urgent tasks (priority ≥ 7) ranked higher
- **Time Window Bonus** (+5 bonus): Tasks matched to their preferred time slot (morning/afternoon)
- **Pet Energy Fit** (1-3 points): Aligns with pet's current energy level
- **Duration Penalty** (-0.05 per minute): Longer tasks penalized slightly to balance schedule

**Formula:** `score = priority + (window_match ? +5 : 0) + energy_level - (duration_minutes × 0.05)`

Example: A high-priority (9) morning walk for an energetic pet:
```
score = 9 + 5 (morning bonus) + 3 (high energy) - (40 min × 0.05) = 15.0
```

#### 2. **Chronological Task Sorting** ⏰
- Tasks are automatically sorted by start time for easy visualization
- Uses HH:MM parsing to correctly order times (e.g., 9:30 before 14:00)
- Helps users quickly scan the daily schedule at a glance

**Usage:** `scheduler.sort_tasks_by_time(tasks)` → Returns tasks in time order

#### 3. **Flexible Task Filtering** 🔍
Query tasks by multiple dimensions:
- **By Status**: Filter complete vs. incomplete tasks
- **By Category**: Group by task type (feeding, play, grooming, medical, enrichment)
- **By Pet**: View tasks for specific pets across all owned pets

**Usage:**
```python
incomplete = scheduler.filter_tasks_by_status(tasks, "incomplete")
feeding_tasks = scheduler.filter_tasks_by_category(tasks, "feeding")
```

#### 4. **Conflict Detection & Warnings** ⚠️
- Automatically detects when multiple tasks are scheduled at the same start time
- Flags conflicts in the UI with clear warnings and actionable advice
- Helps prevent double-booking and scheduling errors

**Detection Strategy:** Exact start-time matching (e.g., both tasks at 10:00 AM)

**Usage:** `conflicts = scheduler.detect_conflicts(scheduled_tasks)` → Returns warning list

#### 5. **Time-Constrained Scheduling** ⏱️
The scheduler respects real-world time constraints:
- **Available Minutes**: Schedules only tasks that fit in remaining daily time
- **Break Intervals**: Enforces 15-minute breaks between tasks for owner rest
- **Time Boundary**: Keeps all tasks within owner's defined working hours (default 6 AM start)

Example: With 120 minutes available and a 30-minute task, only ~90 minutes remain for additional tasks.

#### 6. **Pet Energy Level Adaptation** ⚡
- Task selection adapts to pet's current energy state (1-3 scale)
- High-energy tasks matched to energetic pets
- Low-energy recovery tasks scheduled when pet is tired
- Prevents overexertion or understimulation

Example: A high-energy dog gets a 40-minute fetch before a 20-minute nap recovery.

#### 7. **Smart Task Skipping** 📋
When tasks can't fit:
- Scheduler explains why each task was skipped (time constraints, priority, etc.)
- Displays skipped tasks in UI with reasoning
- Allows users to explore incomplete tasks via filtering

## System Architecture

### Project Structure

```
app.py                      # Streamlit UI layer with session state persistence
pawpal_system.py            # Core business logic (8 classes, ~570 lines)
main.py                     # Terminal demo and testing ground
tests/
  └── test_pawpal.py        # 13 unit tests with full coverage
UML_DIAGRAM.md              # Complete class diagrams and specifications
requirements.txt            # Dependencies (streamlit, pytest, etc.)
```

### Architecture Pattern: Model-View-Controller (MVC)

**Model Layer** (`pawpal_system.py`)
- Data classes: `Task`, `Pet`, `Owner`
- Logic classes: `Scheduler` (scheduling algorithm), `PlanExplainer` (human-readable output)
- Support classes: `TaskFactory` (object creation), `PawPalService` (workflow orchestration)
- All methods have type hints and comprehensive docstrings

**View Layer** (`app.py`)
- Streamlit interface with session state persistence
- Session state acts as persistent "vault" across page reruns
- Wires UI actions (buttons, forms) to model methods
- Displays scheduled/skipped tasks with professional Streamlit components

**Service Layer** (`PawPalService`)
- High-level orchestrator combining `Scheduler` and `PlanExplainer`
- Simplifies complex workflows (plan generation, explanations)
- Single entry point for UI to access scheduling logic

### Data Persistence with Streamlit Session State

```python
# Session state persists across page reruns (Streamlit page refreshes)
if "owner" not in st.session_state:
    st.session_state.owner = None  # Persist owner object

if "current_pet" not in st.session_state:
    st.session_state.current_pet = None  # Persist current pet

if "tasks" not in st.session_state:
    st.session_state.tasks = []  # Persist task list
```

This enables interactive workflows where user actions (add task, create pet) immediately update state without data loss.

## Testing

### Test Suite

The project includes 13 unit tests covering critical scheduling behaviors:

```bash
pytest tests/test_pawpal.py -v
```

**Test Coverage:**
- ✅ Task completion marking (`test_mark_complete`)
- ✅ Urgency detection (`test_is_urgent`)
- ✅ Time window matching (`test_matches_window`)
- ✅ Pet task management (`test_add_task_*`, `test_remove_task`)
- ✅ Owner multi-pet queries (`test_get_all_tasks_across_pets`)
- ✅ Scheduler initialization and scoring (`test_scheduler_initialization`, `test_score_task_high_priority`)
- ✅ Time formatting (`test_format_time`)
- ✅ Empty task edge case (`test_build_daily_plan_empty_tasks`)

**Result:** 13/13 tests passing ✓

### Demo Script

Run `main.py` to see algorithm features in action:

```bash
python main.py
```

Demonstrates:
- Creating owner and pets
- Adding tasks with various priorities and constraints
- Generating daily schedules
- Sorting tasks chronologically
- Filtering by status and category
- Detecting scheduling conflicts

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the Web App

```bash
streamlit run app.py
```

### Run Tests

```bash
pytest tests/test_pawpal.py -v
```

### Run Demo

```bash
python main.py
```

## Usage Examples

### Programmatic Usage

```python
from pawpal_system import Owner, Pet, Task, Scheduler, PawPalService, PlanExplainer

# Create owner and pet
owner = Owner("Alice")
dog = Pet("Buddy", "dog", energy_level=3)

# Create tasks
task1 = Task("Morning walk", 40, priority=9, category="exercise", time_window="morning", energy_level=3)
task2 = Task("Feeding", 15, priority=8, category="feeding", time_window="morning", energy_level=1)

dog.add_task(task1)
dog.add_task(task2)
owner.add_pet(dog)

# Generate schedule
scheduler = Scheduler(owner, start_hour=6)
plan = scheduler.build_daily_plan(dog.get_incomplete_tasks())

# Display results
for task in scheduler.sort_tasks_by_time(plan.scheduled):
    print(f"{task.start_label}-{task.end_label}: {task.title} ({task.reason})")

# Check for conflicts
conflicts = scheduler.detect_conflicts(plan.scheduled)
if conflicts:
    for conflict in conflicts:
        print(f"⚠️ {conflict['warning']}")
else:
    print("✓ No conflicts detected")
```

## Design Philosophy

### Principles Applied

1. **Separation of Concerns** — Logic layer (`pawpal_system.py`) independent from UI (`app.py`)
2. **Single Responsibility** — Each class has one reason to change
3. **Composition Over Inheritance** — No deep inheritance hierarchies
4. **Type Safety** — Full type hints enable IDE support and catch errors early
5. **Testability** — Logic layer has zero Streamlit dependencies, easy to test

### Trade-offs Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Conflict Detection | Exact start-time matching | MVP scope; can upgrade to full overlap detection later |
| Break Intervals | Fixed 15 minutes | Simplifies algorithm while providing reasonable rest |
| Energy Levels | 1-3 discrete scale | Easier to reason about than continuous; covers MVP needs |
| Data Persistence | Session state | Built-in to Streamlit; adequate for single-user app |
| Scheduling Strategy | Greedy weighted scoring | Fast computation; acceptable quality for most scenarios |

## Suggested Development Workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Future Enhancements

- **Conflict Resolution** — Automatically suggest rescheduling options when conflicts detected
- **Multi-Day Planning** — Extend algorithm to weekly schedules
- **Pet Profiles** — Save/load pet configurations from database
- **Smart Notifications** — Alert owner about upcoming tasks
- **Advanced Filtering** — Filter by duration, energy level, or combinations
- **Analytics** — Show task completion trends over time

## Documentation

- **UML_DIAGRAM.md** — Complete class diagrams, specifications, and architecture details
- **reflection.md** — Design decisions, constraints, and AI collaboration notes
