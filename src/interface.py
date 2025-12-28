import sys
import random
from agents.agent_room_booking import BookingAgent
from agents.agent_room_maintenance import MaintenanceAgent
from ontology.dei_department import *
from datetime import datetime, timedelta, date, time

# Initialization of Agent 1 (room booking manager)
agent = BookingAgent(onto)

# Initialization of Agent 2 (room maintenance booking manager)
agent2 = MaintenanceAgent(onto)

def main_menu():
    """Displays the primary navigation menu."""
    while True:
        print("\n====== | DEI Room Management System | ======\n")
        print("1. Administrative Management")
        print("2. Maintenance Management")
        print("3. Room Bookings")
        print("4. Semester Planning")
        print("0. Exit")
        
        choice = input("\nSelect an option: ")
        
        if choice == '1':
            management_menu()
        elif choice == '2':
            maintenance_menu()
        elif choice == '3':
            booking_menu()
        elif choice == '4':
            planning_menu()
        elif choice == '0':
            print("Exiting system. Goodbye!")
            sys.exit(0)
        else:
            print("Invalid option. Please try again.")

def management_menu():
    while True:
        print("\n[Administrative Management]\n")
        print("1. Rooms Management")
        print("2. Teacher Management")
        print("3. Student Management")
        print("4. Course Management")
        print("5. Class Management\n")
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
        else:
            print("Invalid option. Please try again.")

def room_mgmt():
    while True:
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
        elif c == '0':
            return
        else:
            print("Invalid option. Please try again.")

def teacher_mgmt():
    while True:
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
        elif c == '0':
            return
        else:
            print("Invalid option. Please try again.")

def student_mgmt():
    while True:
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
        elif c == '0':
            return
        else:
            print("Invalid option. Please try again.")

def course_mgmt():
    while True:
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
        elif c == '2':
            courses = list(onto.Course.instances())
            if not courses:
                print("\nNo courses registered in the system.")
            else:
                print("\n--- List of Courses ---")
                for crs in courses:
                    print(f"- {crs.has_name} (Year: {crs.has_year}, Sem: {crs.has_semester}, Cap: {crs.required_capacity})")
        elif c == '0':
            return
        else:
            print("Invalid option. Please try again.")

def class_mgmt():
    while True:
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
        elif c == '0':
            return
        else:
            print("Invalid option. Please try again.")

# ===============================================
# TODO Verify if this is necessary
# ===============================================
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
        #elif choice == '2':
        #    rooms = onto.search(type=RoomNeedsAttention)
        #    print(f"Rooms needing cleaning: {[r.has_name for r in rooms]}")
        elif choice == '3':
            bookings = onto.search(type=UnsuitableRoomBooking)
            print(f"Conflicting/Unsuitable Bookings: {bookings}")
        elif choice == '4':
            break
        else:
            print("Invalid option. Please try again.")

def booking_menu():
    while True:
        print("\n[Room Bookings]\n")
        
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
        print("\n1. New Booking\n2. View Room Schedule\n3. Delete Booking\n0. Back\n")
        choice = input("Choice: ")

        if choice == '1':
            # 1. Course/Capacity Logic
            while True:
                is_course = input("Is this for a Course? (y/n): ").lower().strip()
                if is_course in ['y', 'n']:
                    is_course = (is_course == 'y')
                    break

            if is_course:
                c_name = input("Enter Course Code: ").upper()
                course_obj = onto.search_one(type=Course, has_name=c_name)
                if not course_obj:
                    return print("Course not found.")
                cap_needed = course_obj.required_capacity
                print(f"Automatic Capacity required: {cap_needed}")
            else:
                while True:
                    try:
                        cap_needed = int(input("Required Capacity: "))
                        if 1 <= cap_needed <= 500:
                            break
                        print("Error: Capacity must be between 1 and 500.")
                    except ValueError:
                        print("Error: Capacity must be a valid number.")
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
                    if start_hour == 13:
                        print("13:00-14:00 is reserved for Maintenance/Lunch.")
                        continue
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
            if is_course:
                needs_proj = True # Automatic mandatory projector for courses
                print("Projector Required for Lectures (mandatory): y")
            else:
                while True:
                    needs_proj = input("Require Projector? (y/n): ").lower().strip()
                    if needs_proj in ['y', 'n']:
                        needs_proj = (needs_proj == 'y')
                        break
                    print("Error: Please enter only 'y' for yes or 'n' for no.")

            # Get available specific slots
            slots = agent.get_available_slots_in_interval(cap_needed, start_date, end_date, start_hour, num_hours, needs_proj)

            if not slots:
                print("\n[Room Management]: No available slots found in that interval and period of time.")
            else:
                if not slots[0]["suggestion"]:
                    print(f"\n[Room Management] Found {len(slots)} available slots:")
                    sugestion = False
                else:
                    print(f"\n[Room Management] No available slots found in that interval and period of time.\nFound {len(slots)} suggested slots:")
                    sugestion = True
                print("-" * 50)
                if sugestion:
                    samples = 10
                    if len(slots) > 10:
                        slots = random.sample(slots, samples)
                for i, s in enumerate(slots, start=1):
                    print(f" {i}. {s['date']} | {s['duration'][0]} - {s['duration'][1]} | Room: {s['room'].has_name} (Cap: {s['room'].has_capacity})")
                print("-" * 50)
                
                while True:
                    sel = input(f"Select a slot (1-{len(slots)}) or '0' to cancel: ")
                    if sel == '0':
                        print("Booking cancelled.")
                        break
                    
                    if sel.isdigit():
                        idx = int(sel)
                        if 1 <= idx <= len(slots):
                            chosen = slots[idx-1]
                            agent.create_booking(prof, chosen['room'], chosen['start'], chosen['end'],
                                                "Course" if is_course else "Meeting", course_obj)
                            print(f"\nSuccess: {chosen['room'].has_name} booked for {chosen['date']} at {chosen['duration'][0]} - {chosen['duration'][1]}.")
                            break
                    print(f"Invalid choice. Pick a number between 1 and {len(slots)}.")

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

            if not room:
                print(f"Error: Room '{room_name}' does not exist.")
            else:
                # Fetch and sort bookings
                bookings = [b for b in onto.search(type=RoomBooking, booked_in_room=room) if b.has_start_time.date() == target_date]
                sorted_bookings = sorted(bookings, key=lambda x: x.has_start_time)

                print(f"\n" + "="*50)
                print(f"DEI SCHEDULE [{target_date}]: {room.has_name}")
                print(f"Capacity: {room.has_capacity} | Projector: {'Yes' if onto.Projector in room.has_equipment else 'No'}")
                print("="*50)

                if not sorted_bookings:
                    print("No bookings found for this room.")
                else:
                    # 2. Display with Numbers (1, 2, 3...)
                    for idx, b in enumerate(sorted_bookings, start=1):
                        start = b.has_start_time.strftime('%H:%M')
                        end = b.has_end_time.strftime('%H:%M')
                        print(f" {idx}. {start} - {end} | {b.has_name} (by {b.booked_by.has_name})")

                    print("-" * 50)
                print("="*50)

        elif choice == '3':
            # 1. Validate Room
            while True:
                room_name = input("Enter Room Name: ")
                room_name = get_room(room_name)
                if not room_name:
                    print(f"Error: Room '{room_name}' does not exist.")
                else: break

            # 2. Validate day
            while True:
                try:
                    day = input("Cancelling Date (YYYY-MM-DD): ")
                    day_d = datetime.strptime(day, "%Y-%m-%d").date() if day and day is not None else day_d
                    if day_d <= date.today():
                        print("Error: Cancelling Bookings must be made at least one day in advance.")
                        continue
                    break
                except ValueError:
                    print("Invalid format. Use YYYY-MM-DD.")

            # 3. Validate start hour
            while True:
                try:
                    start_d = int(input("Start Hour (9-19): "))
                    if start_d > 8 and start_d < 20:
                        break
                    print("Error: Booking hour invalid.")
                except ValueError:
                    print("Error: Please enter a valid hour number (9-19)")

            # 4. Validate end hour
            while True:
                try:
                    end_d = int(input("End Hour (10-20): "))
                    if end_d > 9 and end_d < 21:
                        break
                    print("Error: Booking hour invalid.")
                except ValueError:
                    print("Error: Please enter a valid hour number (10-20)\n")

            # 5. Converting dates (day + hour)
            dt_start = datetime.combine(day_d, time.min).replace(hour=start_d)
            dt_end = datetime.combine(day_d, time.min).replace(hour=end_d)

            # 6. Formatting to your desired string format
            dt_start_iso = dt_start.isoformat(timespec='milliseconds')
            dt_end_iso = dt_end.isoformat(timespec='milliseconds')

            _ , msg = delete_booking(room_name, dt_start_iso, dt_end_iso, prof_id)
            print(msg)
        elif choice == '0':
            return
        else:
            print("Invalid option. Please try again.")

def maintenance_menu():
    while True:
        print("\n[System Maintenance]\n")
        print("1. Report Broken Equipment in Room")
        print("2. View Changes/Rebooked Classes (Query)")
        print("0. Back")
        
        choice = input("\nSelect: ")
        if choice == '1':
            r_name = input("Enter Room Name: ")
            room = get_room(r_name)
            if room and room.has_equipment:
                # 1. Report the problem
                for eq in room.has_equipment:
                    eq.is_broken = True
                print(f"Status: {r_name} projector reported as broken.")
                
                # 2. Schedule Maintenance (1.1 & 1.2)
                slots = agent2.get_maintenance_slots(room)
                print("\nPossible Maintenance Slots (Randomly generated):")
                for i, s in enumerate(slots, 1):
                    print(f"{i}. {s['start'].strftime('%Y-%m-%d %H:%M')}")
                
                sel = int(input("Choose a slot (Mandatory): ")) - 1
                chosen = slots[sel]
                
                # 3. Book Maintenance (1.3)
                agent2.add_maintenance_booking(room, chosen["start"], chosen['end'])
                
                # 4. Trigger Auto-Relocation (2.1)
                count = agent2.auto_relocate_affected(room)
                print(f"Success! Maintenance scheduled and {count} affected classes rebooked.")
                save()

        elif choice == '2':
            print("\n--- Rebooked Classes Audit ---")
            relocated = [b for b in onto.RoomBooking.instances() if b.is_relocated]
            
            if not relocated:
                print("No rebooked classes found.")
            else:
                for b in relocated:
                    changed_time = b.has_start_time != b.original_start_time
                    status = " [TIME/DAY CHANGED]" if changed_time else " [ROOM ONLY]"
                    print(f"- {b.has_name}: Now in {b.booked_in_room.has_name} at {b.has_start_time} {status}")

            # Validation and manual re-adjustment (2.2 part 2)
            p_id = int(input("\nEnter Prof ID to manually adjust one of your rebooked classes (or 0): "))
            if p_id != 0:
                # Use Agent 1's flow to re-schedule a specific booking if the user isn't happy
                pass
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

if __name__ == "__main__":
    main_menu()