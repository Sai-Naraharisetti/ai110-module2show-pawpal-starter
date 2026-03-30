# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

I started with five main classes: Task (holds task info like name, time, priority), Pet and Owner (store owner/pet details), Scheduler (figures out which tasks fit in the available time and sorts them by priority), and DailyPlan (the final output with scheduled tasks and skipped ones). The Scheduler does the heavy lifting—it scores each task, tries to fit them into the day, and explains why each one was picked or skipped. Everything else is just data containers.


**b. Design changes**

Yes. I refined the original design during implementation. I kept `PlanExplainer` and `TaskFactory` as lightweight support classes rather than making them central, and I introduced `ScheduledTask` to represent output rows cleanly (start/end labels, reason, category, priority). I also added `PawPalService` to orchestrate schedule generation between the `Scheduler` and explainer layer. These changes made responsibilities clearer: entities store data, `Scheduler` computes plans, and the service layer coordinates app workflows.


---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

My scheduler considers: (1) available time in minutes, (2) task priority (high/medium/low), (3) owner's preferred planning window (morning/afternoon/evening), (4) pet's energy level (high-energy pets fit better with exercise tasks), and (5) task duration. I decided priority and time constraints mattered most because they're most relevant to a pet owner—they need to fit the day and handle urgent care needs first. Energy level and window preference are secondary but improve the schedule's usability.

**b. Tradeoffs**

**Conflict Detection Tradeoff:** My scheduler only detects exact start-time conflicts (two tasks scheduled to begin at the same minute), not overlapping durations. For example, a task from 8:00–8:20 and another from 8:15–8:30 wouldn't be flagged as conflicting. This is reasonable for a pet care app because: (1) tasks are small-granule (most are 5–30 minutes), (2) exact simultaneous starts are the main collision risk for a single pet, and (3) full overlap detection would add complexity and slow scheduling. If the app scaled to multiple simultaneous pets, I'd upgrade to duration-based overlap checks.

---

## 3. AI Collaboration

**a. How you used AI**

I used GitHub Copilot throughout the project for code scaffolding, debugging, refactoring, and documentation:
- Generated class skeletons from UML (`Task`, `Pet`, `Owner`, `Scheduler`, etc.)
- Helped implement weighted scheduling logic and helper methods
- Refactored architecture by moving logic from `app.py` into `pawpal_system.py`
- Generated and expanded test cases in `tests/test_pawpal.py`
- Suggested Streamlit UI improvements (`st.warning`, `st.success`, `st.expander`)
- Helped draft docstrings and README feature explanations

The most helpful prompts were specific and constraint-based, for example:
- "Implement a weighted task scoring method using priority, time window, and duration"
- "Generate pytest tests for Task, Pet, Owner, and Scheduler methods"
- "Update Streamlit UI to show sorted tasks and conflict warnings"

**b. Judgment and verification**

I did not accept one early suggestion to model task types with a deep inheritance tree (e.g., `UrgentTask`, `FeedingTask`). I kept a single flexible `Task` model instead because it was simpler, easier to test, and avoided duplicated scheduling logic.

I verified AI suggestions by:
1. Reviewing generated code for design fit and readability
2. Running `pytest` after each meaningful change
3. Manually testing the Streamlit app flow (owner/pet/task creation + schedule generation)
4. Running `main.py` to validate sorting/filtering/conflict behavior end-to-end

---

## 4. Testing and Verification

**a. What you tested**

I tested the core behaviors that protect scheduling correctness:
- Task behavior (`mark_complete`, urgency, time-window matching)
- Pet task operations (add/remove/retrieve incomplete tasks)
- Owner aggregation (tasks across multiple pets)
- Scheduler setup, time formatting, and weighted scoring
- Empty-input planning edge case

These tests were important because they validate the full data flow from entities to scheduling decisions. They also made refactoring safer by catching regressions quickly.

**b. Confidence**

I’m highly confident for MVP scope. The suite is stable at **13/13 passing tests**, and manual runs in both `main.py` and Streamlit confirm expected behavior.

If I had more time, I’d test:
- Overlapping-duration conflicts (not just same start time)
- Very large task lists (performance and ordering stability)
- Duplicate task titles and invalid field values
- Late-day boundary times and constrained schedules with many skipped tasks

---

## 5. Reflection

**a. What went well**

The strongest outcome was the architecture split: logic in `pawpal_system.py`, UI in `app.py`, and tests independent from Streamlit. That separation made iteration fast and made the code easier to reason about.

**b. What you would improve**

In a next iteration I’d add persistent storage (SQLite), richer filtering controls in the UI, and smarter conflict resolution suggestions (auto-shift or recommendation engine).

**c. Key takeaway**

My key takeaway is that simple domain models plus strong tests lead to better systems. AI accelerates implementation, but quality comes from clear constraints, deliberate design choices, and continuous verification.
