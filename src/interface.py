import sys
from agents.agent_room_booking import BookingAgent
from ontology.dei_department import *
from datetime import datetime, timedelta, date

# Initialization of Agent 1 (room booking manager)
agent = BookingAgent(onto)

def main_menu():
    """Displays the primary navigation menu."""
    while True:
        print("\n====== | DEI Room Management System | ======\n")
        print("1. Administrative Management")
        print("2. Live Status & Queries (????)")
        print("3. Room Bookings\n")
        print("4. Semester Planning (PDDL)")
        print("5. System Maintenance (Agent 2)")
        print("0. Exit")
        
        choice = input("\nSelect an option: ")
        
        if choice == '1':
            management_menu()
        elif choice == '2':
            queries_menu()
        elif choice == '3':
            booking_menu()
        elif choice == '4':
            planning_menu()
        elif choice == '5':
            maintenance_menu()
        elif choice == '0':
            print("Exiting system. Goodbye!")
            sys.exit(0)
        else:
            print("Invalid option. Please try again.")

def management_menu():
    while True:
        print("\n[Administrative Management]")
        print("1. Rooms Management")
        print("2. Teacher Management")
        print("3. Student Management")
        print("4. Course Management")
        print("5. Class Management")
        print("6. Clear All Data")
        print("0. Back to Main Menu")
        
        choice = input("\nSelect: ")
        if choice == '1': room_mgmt()
        elif choice == '2': teacher_mgmt()
        elif choice == '3': student_mgmt()
        elif choice == '4': course_mgmt()
        elif choice == '5': class_mgmt()
        elif choice == '6': clean_onto()
        elif choice == '0': main_menu()

def room_mgmt():
    print("\n[Room Management]\n")
    print("1. Add Room\n2. List Rooms\n0. Back\n")
    c = input("Choice: ")
    if c == '1':
        # 1. Validate Name (must not be empty)
        while True:
            name = input("Name: ").strip()
            if name:
                break
            print("Error: Name cannot be empty.")

        # 2. Validate Capacity (must be an integer > 0)
        while True:
            try:
                cap = int(input("Capacity: "))
                if cap > 0:
                    break
                print("Error: Capacity must be greater than 0.")
            except ValueError:
                print("Error: Please enter a valid whole number.")

        # 3. Validate Projector (must be y or n)
        while True:
            proj_input = input("Has Projector? (y/n): ").lower().strip()
            if proj_input in ['y', 'n']:
                proj = (proj_input == 'y')
                break
            print("Error: Please enter only 'y' for yes or 'n' for no.")
        _ , msg = add_room(name, cap, proj)
        print(msg)
        room_mgmt()
    elif c == '2':
        rooms = list(onto.Room.instances())
        
        if not rooms:
            print("\nNo rooms found in the department.")
        else:
            print("\n--- List of Registered Rooms ---")
            for r in rooms:
                # Check for equipment
                eq_list = [e.has_name for e in r.has_equipment]
                equipment_str = ", ".join(eq_list) if eq_list else "None"
                
                print(f"Room: {r.has_name}")
                print(f" - Capacity: {r.has_capacity}")
                print(f" - Equipment: {equipment_str}")
                print(f" - Accumulated Usage: {r.accumulated_usage} hours")
                
                # Intelligence Hint: Highlight if it needs attention
                if r in onto.RoomNeedsAttention.instances():
                    print("STATUS: Requires Maintenance/Cleaning")
                
                print("-" * 20)
        
        room_mgmt()
    elif c == '0':
        management_menu()
    else:
        print("Invalid choice. Choose option 1, 2 or 0 to Back")
        room_mgmt()

def teacher_mgmt():
    print("\n[Teacher Management]\n")
    print("1. Add Teacher\n2. List Teachers\n0. Back\n")
    c = input("Choice: ")

    if c == '1':
        # 1. Validate Name (must not be empty)
        while True:
            name = input("Name: ").strip()
            if name:
                break
            print("Error: Name cannot be empty.")

        # 2. Validate ID
        while True:
            try:
                id_num = int(input("ID: "))
                if id_num > 99:
                    break
                print("Error: ID must have more than 2 digits.")
            except ValueError:
                print("Error: ID must be a valid number.")

        # 3. Validate Courses
        while True:
            courses_raw = input("Courses (comma separated): ").split(",")
            processed_courses = [c.strip().upper() for c in courses_raw if c.strip()]
            
            if not processed_courses:
                print("Error: Please enter at least one course.")
                continue
            
            existing_courses = [course.has_name for course in onto.Course.instances()]
            
            # Identify which entered courses are missing from the ontology
            missing_courses = [c for c in processed_courses if c not in existing_courses]
            
            if missing_courses:
                print(f"Error: The following courses do not exist: {', '.join(missing_courses)}")
                print("Note: Courses must be added via 'Course Management' first.")
                valid_format = False
                teacher_mgmt()
            else:
                valid_format = True

            if valid_format:
                courses = processed_courses
                break
        _ , msg = add_teacher(name, id_num, courses)
        print(msg)
        teacher_mgmt()
    elif c == '2':
        teachers = list(onto.Teacher.instances())
        
        if not teachers:
            print("\nNo teachers found in the department.")
        else:
            print("\n--- List of Registered Teachers ---")
            for t in teachers:
                # Extract course details (Name and Year/Semester)
                course_details = [f"{c.has_name} (Y{c.has_year}S{c.has_semester})" for c in t.teaches]
                
                print(f"ID: {t.has_id}")
                print(f" - Name: {t.has_name}")
                print(f" - Courses Taught: {', '.join(course_details) if course_details else 'None Assigned'}")
                
                # Intelligence Hint: Check for Overloaded status (Inferred Class)
                if t in onto.OverloadedTeacher.instances():
                    print(" ! STATUS: Overloaded (Teaches > 3 Courses)")
                
                print("-" * 20)
        teacher_mgmt()
    elif c == '0':
        management_menu()
    else:
        print("Invalid choice. Choose option 1 or 2")
        teacher_mgmt()

def student_mgmt():
    print("\n[Student Management]\n")
    print("1. Add Student\n2. List Students\n0. Back\n")
    c = input("Choice: ")
    if c == '1':
        # 1. Validate Name (must not be empty)
        while True:
            name = input("Name: ").strip()
            if name:
                break
            print("Error: Name cannot be empty.")
        
        # 2. Validate ID
        while True:
            try:
                id_num = int(input("ID: "))
                if id_num > 99:
                    break
                print("Error: ID must have more than 2 digits.")
            except ValueError:
                print("Error: ID must be a valid number.")

        # 3. Validate Class
        cls = input("Class Code: ")
        
        # 4. Validate Year
        while True:
            try:
                yr = int(input("Year: "))
                if yr < 4 or yr > 0:
                    break
                print("Error: Year must be 1, 2 or 3.")
            except ValueError:
                print("Error: Year must be a valid number.")

        # 5. Validate Courses
        while True:
            courses_raw = input("Courses (comma separated): ").split(",")
            processed_courses = [c.strip().upper() for c in courses_raw if c.strip()]
            
            if not processed_courses:
                print("Error: Please enter at least one course.")
                continue
            
            existing_courses = [course.has_name for course in onto.Course.instances()]
            
            # Identify which entered courses are missing from the ontology
            missing_courses = [c for c in processed_courses if c not in existing_courses]
            
            if missing_courses:
                print(f"Error: The following courses do not exist: {', '.join(missing_courses)}")
                print("Note: Courses must be added via 'Course Management' first.")
                valid_format = False
            else:
                valid_format = True

            if valid_format:
                courses = processed_courses
                break
        _ , msg = add_student(name, id_num, cls, yr, [x.strip() for x in courses])
        print(msg)
        student_mgmt()
    elif c == '2':
        students = list(onto.Student.instances())
        
        if not students:
            print("\nNo students found in the department.")
        else:
            print("\nList of Registered Students")
            for s in students:
                course_names = [course.has_name for course in s.enrolled_in]
                
                print(f"ID: {s.has_id}")
                print(f" - Name: {s.has_name}")
                print(f" - Class: {s.has_class_code} (Year {s.has_year})")
                print(f" - Enrolled In: {', '.join(course_names) if course_names else 'None'}")
                print("-" * 20)
        
        student_mgmt()
    elif c == '0':
        management_menu()
    else:
        print("Invalid choice. Choose option 1 or 2")
        student_mgmt()

def course_mgmt():
    print("\n[Course Management]\n")
    print("1. Add Course\n2. Course List\n0. Back\n")
    c = input("Choice: ")
    if c == '1':
        # 1. Validate Name (must not be empty)
        while True:
            name = input("Course Name: ").strip()
            if not name:
                print("Error: Name cannot be empty.")
            elif len(name) <= 1:
                print("Error: Name is too short (minimum 2 characters).")
            elif len(name) > 10:
                print("Error: Name is too long (maximum 10 characters).")
            else:
                break

        # 2. Validate Year
        while True:
            try:
                year = int(input("Year: "))
                if year < 4 or year > 0:
                    break
                print("Error: Year must be 1, 2 or 3.")
            except ValueError:
                print("Error: Year must be a valid number.")

        # 3. Validate Semester (1 or 2)
        while True:
            try:
                semester = int(input("Semester (1 or 2): "))
                if semester in [1, 2]:
                    break
                print("Error: Semester must be 1 or 2.")
            except ValueError:
                print("Error: Semester must be a valid number.")

        # 4. Validate Student Course Number
        while True:
            try:
                capacity = int(input("Number of Students (e.g., 10-300): "))
                if 10 <= capacity <= 500:
                    break
                print("Error: Number of Students must be between 10 and 500.")
            except ValueError:
                print("Error: Number of Students must be a valid number.")

        _ , msg = add_course(name, year, semester, capacity)
        print(msg)
        course_mgmt()
    elif c == '2':
        courses = list(onto.Course.instances())
        if not courses:
            print("\nNo courses registered in the system.")
        else:
            print("\n--- List of Courses ---")
            for crs in courses:
                print(f"- {crs.has_name} (Year: {crs.has_year}, Sem: {crs.has_semester}, Cap: {crs.required_capacity})")
        course_mgmt()
    elif c == '0':
        management_menu()
    else:
        print("Invalid choice. Choose option 1, 2 or 0 to Back")
        course_mgmt()

def class_mgmt():
    print("\n[Class Management]\n")
    print("1. Add Class\n2. Class List\n0. Back\n")
    c = input("Choice: ")
    
    if c == '1':
        # 1. Validate Name
        while True:
            name = input("Class Name: ").strip().upper()
            if name: break
            print("Error: Class name cannot be empty.")

        # 2. Validate Year
        while True:
            try:
                year = int(input("Year (1-3): "))
                if 1 <= year <= 5: break
                print("Error: Year must be between 1 and 5.")
            except ValueError:
                print("Error: Year must be a number.")

        _ , msg = add_academic_class(name, year)
        print(msg)
        class_mgmt()

    elif c == '2':
        classes = list(onto.AcademicClass.instances())
        if not classes:
            print("\nNo academic classes registered.")
        else:
            print("\n--- List of Academic Classes ---")
            for ac in classes:
                # Find students belonging to this class using inverse search
                # FOL: {s | Student(s) ^ belongs_to_class(s, ac)}
                students = onto.search(type=Student, belongs_to_class=ac)
                student_names = [s.has_name for s in students]
                
                print(f"Class: {ac.has_name} | Year: {ac.has_year}")
                print(f" - Registered Students: {', '.join(student_names) if student_names else 'None'}")
                print("-" * 30)
        
        class_mgmt()
    elif c == '0':
        management_menu()

def queries_menu():
    
    while True:
        print("Nothing yet...")
        choice = input("\nBack pressing 0: ")
        if choice == '0':
            break

        print("\n--- Live Status & Queries ---")
        print("1. List Available Rooms (Inferred)")
        print("2. List Rooms Needing Attention (Agent 2 Trigger)")
        print("3. Identify Unsuitable Bookings")
        print("4. Back to Main Menu")
        
        choice = input("\nSelect an option: ")
        if choice == '1':
            rooms = onto.search(type=AvailableRoom)
            print(f"Available Rooms: {[r.has_name for r in rooms]}")
        elif choice == '2':
            rooms = onto.search(type=RoomNeedsAttention)
            print(f"Rooms needing cleaning: {[r.has_name for r in rooms]}")
        elif choice == '3':
            bookings = onto.search(type=UnsuitableRoomBooking)
            print(f"Conflicting/Unsuitable Bookings: {bookings}")
        elif choice == '4':
            break

def booking_menu():
    while True:
        print("\n--- Room Bookings ---")
        
        # Identity Check
        raw_input = input("Verify Teacher ID to proceed or '0' Return: ")
        if raw_input == '0':
            return
        
        try:
            prof_id = int(raw_input)
        except ValueError:
            print("Invalid ID format.")
            continue

        prof = onto.search_one(type=Teacher, has_id=prof_id)
        
        if not prof:
            print("\nAccess Denied: Only registered Teachers/Professors can book.")
            return

        print(f"\nWelcome, {prof.has_name}")
        print("\n1. New Booking\n2. View Room Schedule\n3. Emergency Room Changes\n0. Back\n")
        choice = input("Choice: ")

        if choice == '1':
            # 1. Course/Capacity Logic
            is_course = input("Is this for a Course? (y/n): ").lower() == 'y'
            if is_course:
                c_name = input("Enter Course Code: ").upper()
                course_obj = onto.search_one(type=Course, has_name=c_name)
                if not course_obj:
                    return print("Course not found.")
                cap_needed = course_obj.required_capacity
                print(f"Automatic Capacity required: {cap_needed}")
            else:
                cap_needed = int(input("Required Capacity: "))
                course_obj = None

            # 2. Validate starting date
            while True:
                try:
                    start_date_str = input("Start Date (YYYY-MM-DD): ")
                    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                    
                    # Validation: Must be at least tomorrow
                    if start_date <= date.today():
                        print("Error: Bookings must be made at least one day in advance.")
                        continue
                    
                    # Validation: Not a weekend
                    if start_date.weekday() >= 5:
                        print("Error: Starting date cannot be a weekend.")
                        continue
                    break
                except ValueError:
                    print("Invalid format. Use YYYY-MM-DD.")

            # 3. Validate ending Date
            while True:
                try:
                    end_date_str = input("End Date (YYYY-MM-DD) [Press Enter if same as start]: ")
                    end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date() if end_date_str else start_date
                    if end_date < start_date:
                        print("Error: End date must be equal or greater then start date")
                        continue
                    break
                except ValueError:
                    print("Invalid format. Use YYYY-MM-DD.")

            # 4. Validate Hour
            while True:
                try:
                    start_hour = int(input("Start Hour (9-19): "))
                    if start_hour > 8 and start_hour < 20 and start_hour != 13:
                        break
                    print("Error: Booking start hour invalid.")
                except ValueError:
                    print("Error: Please enter a valid hour number (9-19)")
            
            # 5. Validate slot duration
            while True:
                try:
                    num_hours = int(input("Duration in Hours (max 4h): "))
                    if num_hours > 0 and num_hours < 5:
                        break
                    print("Error: Slots must have at least 1h duration and at most 4h duration")
                except ValueError:
                    print("Error: Please enter a valid hour number (9-19)")
            
            # 6. Validates projector
            while True:
                needs_proj = input("Require Projector? (y/n): ").lower().strip()
                if needs_proj in ['y', 'n']:
                    needs_proj = (needs_proj == 'y')
                    break
                print("Error: Please enter only 'y' for yes or 'n' for no.")

            # Get available specific slots
            slots = agent.get_available_slots_in_interval(cap_needed, start_date, end_date, start_hour, num_hours, needs_proj)

            if not slots:
                print("\n[Agent 1]: No available slots found in that interval.")
            else:
                print(f"\n[Agent 1] Found {len(slots)} available slots:")
                for i, s in enumerate(slots):
                    print(f"{i+1}. Date: {s['date']} | Room: {s['room'].has_name} (Cap: {s['room'].has_capacity})")
                
                sel = input("\nSelect one slot to book (number) or 'c' to cancel: ")
                if sel.isdigit() and int(sel) <= len(slots):
                    chosen = slots[int(sel)-1]
                    agent.create_booking(prof, chosen['room'], chosen['start'], chosen['end'],
                                        "Course" if is_course else "Meeting", course_obj)
                    save()
                    print(f"Success: {chosen['room'].has_name} booked for {chosen['date']}.")

        elif choice == '2':
            room_name = input("Enter Room Name to check: ")
            room = get_room(room_name)

            while True:
                day_str = input("Enter Date (YYYY-MM-DD): ")
                try:
                    target_date = datetime.strptime(day_str, "%Y-%m-%d").date()
                    break
                except ValueError:
                    print("Invalid format. Use YYYY-MM-DD.")
            ###

            if not room:
                print(f"Error: Room '{room_name}' does not exist.")
            else:
                # Fetch and sort bookings by start time
                bookings = [b for b in onto.search(type=RoomBooking, booked_in_room=room) if b.has_start_time.date() == target_date]
                sorted_bookings = sorted(bookings, key=lambda x: x.has_start_time)

                print(f"\n" + "="*40)
                print(f"DEI SCHEDULE [{target_date}]: {room.has_name}")
                print(f"Capacity: {room.has_capacity} | Projector: {'Yes' if onto.Projector in room.has_equipment else 'No'}")
                print("="*40)

                if not sorted_bookings:
                    print("No bookings found for this room.")
                else:
                    current_date = None
                    for b in sorted_bookings:
                        # Print a date header whenever the day changes
                        booking_date = b.has_start_time.strftime('%Y-%m-%d')
                        if booking_date != current_date:
                            print(f"\n--- {booking_date} ---")
                            current_date = booking_date
                        
                        # Formatting the hourly block display
                        start = b.has_start_time.strftime('%H:%M')
                        end = b.has_end_time.strftime('%H:%M')
                        print(f"  {start} - {end} | {b.has_name} (by {b.booked_by.has_name})")

                print("="*40)

            # ======================================================================
            # TODO Change logic: this service must only show what changed.
            # Agent 2 will activate the emergency relocation service automatically
            # ======================================================================

        elif choice == '3':
            print("\n--- Emergency Relocation Service ---")
            # List bookings made by this professor today or in the future
            my_bookings = onto.search(type=RoomBooking, booked_by=prof)
            if not my_bookings:
                print("You have no active bookings moved.")
            else:
                for i, b in enumerate(my_bookings):
                    print(f"{i+1}. {b.has_name} in {b.booked_in_room.has_name} ({b.has_start_time.strftime('%H:%M')})")
                
                idx = input("Select booking to relocate (or 'c'): ")
                if idx.isdigit() and int(idx) <= len(my_bookings):
                    target_booking = my_bookings[int(idx)-1]
                    
                    # Simulate reporting the projector as broken in the ontology
                    current_room = target_booking.booked_in_room
                    projector = onto.search_one(has_name="Standard Projector")
                    if projector in current_room.has_equipment:
                        projector.is_broken = True # Trigger for Agent 2 later
                    
                    # Agent 1 attempts relocation
                    success, msg = agent.emergency_relocate(target_booking)
                    if success:
                        save()
                        print(f"SUCCESS: {msg}")
                    else:
                        print(f"FAILED: {msg}")

        elif choice == '0':
            return

def planning_menu():
    """Triggers the PDDL Automated Planners."""
    print("\n--- Semester Planning (PDDL) ---")
    print("1. Generate Weekly Class Template")
    print("2. Generate Exam Epoch Schedule")
    print("3. Back to Main Menu")
    # This will call the unified-planning solver as seen in planner.py
    input("\n[Placeholder] Press Enter to return...")

def maintenance_menu():
    """Interface for Agent 2's maintenance operations."""
    print("\n--- System Maintenance (Agent 2) ---")
    print("1. Run Hygiene & Maintenance Audit")
    print("2. View Scheduled Repairs")
    print("3. Back to Main Menu")
    # This will trigger Agent 2 to claim slots for cleaning/repairs
    input("\n[Placeholder] Press Enter to return...")

if __name__ == "__main__":
    main_menu()