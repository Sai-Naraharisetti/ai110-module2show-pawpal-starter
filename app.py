import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler, PawPalService, PlanExplainer

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to **PawPal+** — your personal pet care scheduling assistant.

This app helps you plan daily care tasks for your pet(s) based on priorities, time constraints, and preferences.
"""
)

with st.expander("How it works", expanded=False):
    st.markdown(
        """
1. **Enter owner & pet info** — Set your available time and preferred planning window
2. **Add tasks** — Define care activities (feeding, walks, grooming, etc.)
3. **Generate schedule** — Our scheduler uses priority, time fit, and pet energy level to create an optimal plan
4. **Review & adjust** — See what fits today and why each task was chosen or skipped
"""
    )

# ===== SESSION STATE INITIALIZATION =====
# st.session_state acts like a persistent "vault" across page reruns
# Check if Owner object exists before creating a new one

if "owner" not in st.session_state:
    st.session_state.owner = None

if "current_pet" not in st.session_state:
    st.session_state.current_pet = None

if "tasks" not in st.session_state:
    st.session_state.tasks = []

# ===== OWNER & PET SETUP =====
st.divider()
st.subheader("Owner & Pet Information")

col_a, col_b = st.columns(2)
with col_a:
    owner_name = st.text_input("Owner name", value="Jordan")
    available_minutes = st.slider("Available time today (minutes)", 30, 480, 120, 15)
    focus_window = st.selectbox("Preferred planning window", ["morning", "afternoon", "evening"], index=0)
with col_b:
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"], index=0)
    energy_level = st.selectbox("Pet energy level", ["low", "medium", "high"], index=1)

break_minutes = st.slider("Break between tasks (minutes)", 0, 30, 5, 5)
start_hour = st.slider("Day starts at (hour)", 5, 12, 8)

# Button to create/update Owner & Pet (wires to Owner.add_pet() method)
if st.button("Create/Update Owner & Pet", type="primary"):
    # Call Owner class constructor to create instance
    st.session_state.owner = Owner(
        name=owner_name.strip() or "Owner",
        available_minutes=int(available_minutes),
        focus_window=focus_window,
        break_minutes=int(break_minutes),
    )
    
    # Create Pet instance
    pet = Pet(
        name=pet_name.strip() or "Pet",
        species=species,
        energy_level=energy_level
    )
    
    # Wire to Owner.add_pet() method - adds pet to owner's pet list
    st.session_state.owner.add_pet(pet)
    st.session_state.current_pet = pet
    
    # Reset tasks when owner/pet changes
    st.session_state.tasks = []
    
    st.success(f"✓ Created {owner_name} with pet {pet_name}!")

# Display current Owner & Pet info (read from session_state vault)
if st.session_state.owner:
    st.info(
        f"📌 Working with: **{st.session_state.owner.name}** "
        f"({st.session_state.owner.available_minutes} min available) | "
        f"Pet: **{st.session_state.current_pet.name}** ({st.session_state.current_pet.species}, {st.session_state.current_pet.energy_level} energy)"
    )
else:
    st.warning("⚠️ Create an owner and pet first!")

# ===== TASK MANAGEMENT =====
st.divider()
st.subheader("Task Management")

if st.session_state.owner is None:
    st.info("Create an owner and pet above to start adding tasks.")
else:
    st.caption("Add tasks to your pet's schedule below.")
    
    # Add task form
    add_col1, add_col2, add_col3 = st.columns(3)
    with add_col1:
        new_title = st.text_input("Task title", value="Evening enrichment")
        new_category = st.selectbox("Category", ["exercise", "feeding", "medication", "grooming", "enrichment", "other"])
    with add_col2:
        new_duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        new_priority = st.selectbox("Priority", ["low", "medium", "high"], index=1)
    with add_col3:
        new_window = st.selectbox("Preferred window", ["any", "morning", "afternoon", "evening"], index=0)
    
    # Add task button - wires to Pet.add_task() method
    if st.button("Add task"):
        normalized_title = new_title.strip()
        if not normalized_title:
            st.error("Task title cannot be empty.")
        else:
            # Create Task instance
            task = Task(
                title=normalized_title,
                duration_minutes=int(new_duration),
                priority=new_priority,
                category=new_category,
                preferred_window=new_window,
            )
            
            # Wire to Pet.add_task() method - adds task to pet's task list
            st.session_state.current_pet.add_task(task)
            st.session_state.tasks.append({
                "title": normalized_title,
                "duration_minutes": int(new_duration),
                "priority": new_priority,
                "category": new_category,
                "preferred_window": new_window,
            })
            st.success(f"✓ Added: {normalized_title}")
    
    # Display and edit tasks (read/modify session_state vault)
    if st.session_state.current_pet and st.session_state.current_pet.tasks:
        st.markdown("#### Current Tasks")
        
        edited_tasks = st.data_editor(
            st.session_state.tasks,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "title": st.column_config.TextColumn("Title", required=True),
                "duration_minutes": st.column_config.NumberColumn("Duration (min)", min_value=1, max_value=240, step=1),
                "priority": st.column_config.SelectboxColumn("Priority", options=["low", "medium", "high"], required=True),
                "category": st.column_config.SelectboxColumn(
                    "Category",
                    options=["exercise", "feeding", "medication", "grooming", "enrichment", "other"],
                    required=True,
                ),
                "preferred_window": st.column_config.SelectboxColumn(
                    "Preferred window",
                    options=["any", "morning", "afternoon", "evening"],
                    required=True,
                ),
            },
        )
        
        # Sync edited tasks back to Pet object
        st.session_state.tasks = [
            {
                "title": str(item["title"]).strip(),
                "duration_minutes": int(item["duration_minutes"]),
                "priority": str(item["priority"]),
                "category": str(item["category"]),
                "preferred_window": str(item["preferred_window"]),
            }
            for item in edited_tasks
            if str(item.get("title", "")).strip()
        ]
        
        # Sync back to Pet object
        st.session_state.current_pet.tasks = []
        for task_data in st.session_state.tasks:
            task = Task(
                title=task_data["title"],
                duration_minutes=int(task_data["duration_minutes"]),
                priority=task_data["priority"],
                category=task_data["category"],
                preferred_window=task_data["preferred_window"],
            )
            st.session_state.current_pet.add_task(task)
        
        # Remove task button - wires to Pet.remove_task() method
        remove_options = [task["title"] for task in st.session_state.tasks]
        remove_title = st.selectbox("Remove a task", ["-- none --"] + remove_options)
        if st.button("Remove selected task") and remove_title != "-- none --":
            # Wire to Pet.remove_task() method
            removed = st.session_state.current_pet.remove_task(remove_title)
            if removed:
                st.session_state.tasks = [task for task in st.session_state.tasks if task["title"] != remove_title]
                st.success(f"✓ Removed: {remove_title}")
            else:
                st.error(f"Could not remove: {remove_title}")
    else:
        st.info("No tasks yet. Add one above.")

# ===== SCHEDULE GENERATION =====
st.divider()
st.subheader("Daily Schedule")

if st.button("Generate schedule", type="primary"):
    if not st.session_state.owner:
        st.warning("Create an owner and pet first!")
    elif not st.session_state.current_pet.tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        try:
            # Generate schedule using Scheduler class
            scheduler = Scheduler(owner=st.session_state.owner, start_hour=int(start_hour))
            service = PawPalService(scheduler=scheduler, explainer=PlanExplainer())
            
            # Wire to Scheduler.build_daily_plan() method
            plan = service.generate_plan(st.session_state.current_pet.get_incomplete_tasks())
            
            # Display results
            st.markdown(f"### Plan for {st.session_state.owner.name} and {st.session_state.current_pet.name} ({st.session_state.current_pet.species})")
            
            col_metrics = st.columns(3)
            col_metrics[0].metric("Scheduled care minutes", plan.total_minutes)
            col_metrics[1].metric("Tasks scheduled", len(plan.scheduled))
            col_metrics[2].metric("Tasks skipped", len(plan.skipped))
            
            # ENHANCEMENT: Sort tasks chronologically using new method
            if plan.scheduled:
                sorted_tasks = scheduler.sort_tasks_by_time(plan.scheduled)
                
                st.markdown("#### 📅 Scheduled Tasks (Chronological Order)")
                st.table(
                    [
                        {
                            "Time": f"{item.start_label}–{item.end_label}",
                            "Task": item.title,
                            "Duration": f"{item.duration_minutes} min",
                            "Priority": item.priority.upper(),
                            "Category": item.category,
                            "Why chosen": item.reason,
                        }
                        for item in sorted_tasks
                    ]
                )
                
                # ENHANCEMENT: Detect and display conflicts using new method
                conflicts = scheduler.detect_conflicts(plan.scheduled)
                if conflicts:
                    st.warning("⚠️ **Scheduling Conflicts Detected**")
                    for conflict in conflicts:
                        st.error(
                            f"🚨 {conflict['warning']}\n\n"
                            f"**Action needed:** Please review the tasks scheduled at **{conflict['time']}** "
                            f"and consider adjusting task times or durations."
                        )
                else:
                    st.success("✓ No scheduling conflicts detected!")
            else:
                st.warning("No tasks could be scheduled with the current constraints.")
            
            # ENHANCEMENT: Display skipped tasks with filter option
            if plan.skipped:
                st.markdown("#### ⏭️ Skipped Tasks")
                
                with st.expander("View skipped tasks", expanded=True):
                    st.table(
                        [
                            {"Task": item["title"], "Priority": item["priority"].upper(), "Reason": item["reason"]}
                            for item in plan.skipped
                        ]
                    )
                
                # Suggest filtering by status
                if st.button("Show all incomplete tasks (unscheduled)"):
                    all_incomplete = scheduler.filter_tasks_by_status(
                        st.session_state.current_pet.tasks, 
                        "incomplete"
                    )
                    st.info(f"**Found {len(all_incomplete)} incomplete tasks:**")
                    st.table(
                        [
                            {
                                "Task": t.title,
                                "Duration": f"{t.duration_minutes} min",
                                "Priority": t.priority.upper(),
                                "Category": t.category,
                                "Status": t.completion_status.upper()
                            }
                            for t in all_incomplete
                        ]
                    )
        
        except Exception as e:
            st.error(f"Error generating schedule: {str(e)}")

