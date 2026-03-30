# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

I started with five main classes: Task (holds task info like name, time, priority), Pet and Owner (store owner/pet details), Scheduler (figures out which tasks fit in the available time and sorts them by priority), and DailyPlan (the final output with scheduled tasks and skipped ones). The Scheduler does the heavy lifting—it scores each task, tries to fit them into the day, and explains why each one was picked or skipped. Everything else is just data containers.


**b. Design changes**

Yes. I originally planned separate `PlanExplainer` and `TaskFactory` classes, but when I built the app, I realized those were overkill. The Streamlit UI already handles input validation and formatting, and explanations fit naturally into the `ScheduledTask.reason` field, so I merged that logic directly into the Scheduler. Also, I added `ScheduledTask` during implementation—it wasn't in my initial sketch—because I needed a clean output model to display scheduled vs. skipped tasks with their reasoning. This made the plan output much clearer and easier to render in the UI.


---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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
