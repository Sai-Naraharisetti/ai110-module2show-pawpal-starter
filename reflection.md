# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

I started with five main classes: Task (holds task info like name, time, priority), Pet and Owner (store owner/pet details), Scheduler (figures out which tasks fit in the available time and sorts them by priority), and DailyPlan (the final output with scheduled tasks and skipped ones). The Scheduler does the heavy lifting—it scores each task, tries to fit them into the day, and explains why each one was picked or skipped. Everything else is just data containers.


**b. Design changes**

Yes. I originally planned separate PlanExplainer and TaskFactory classes, but when I built the app, I realized those were not needed. The Streamlit UI already handles input validation and formatting, and explanations fit naturally into the ScheduledTask.reason field, so I merged that logic directly into the Scheduler. Also, I added `ScheduledTask` during implementation—it wasn't in my initial sketch—because I needed a clean output model to display scheduled vs. skipped tasks with their reasoning. This made the plan output much clearer and easier to render in the UI.


---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

My scheduler considers: (1) available time in minutes, (2) task priority (high/medium/low), (3) owner's preferred planning window (morning/afternoon/evening), (4) pet's energy level (high-energy pets fit better with exercise tasks), and (5) task duration. I decided priority and time constraints mattered most because they're most relevant to a pet owner—they need to fit the day and handle urgent care needs first. Energy level and window preference are secondary but improve the schedule's usability.

**b. Tradeoffs**

**Conflict Detection Tradeoff:** My scheduler only detects exact start-time conflicts (two tasks scheduled to begin at the same minute), not overlapping durations. For example, a task from 8:00–8:20 and another from 8:15–8:30 wouldn't be flagged as conflicting. This is reasonable for a pet care app because: (1) tasks are small-granule (most are 5–30 minutes), (2) exact simultaneous starts are the main collision risk for a single pet, and (3) full overlap detection would add complexity and slow scheduling. If the app scaled to multiple simultaneous pets, I'd upgrade to duration-based overlap checks.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
