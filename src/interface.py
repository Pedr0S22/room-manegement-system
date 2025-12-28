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
        print("5. Class Management")
        print("6. Check Overbooked Rooms\n")
        print("7. Clear All Data")
        print("0. Back to Main Menu")
        
        choice = input("\nSelect: ")
        if choice == '1': room_mgmt()
        elif choice == '2': teacher_mgmt()
        elif choice == '3': student_mgmt()
        elif choice == '4': course_mgmt()
        elif choice == '5': class_mgmt()
        elif choice == '6': check_overbooked()
        elif choice == '7': clean_onto()
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

            # 3. Validate Class and year
            while True:
                cls = input("Academic Class: ")
                while True:
                    try:
                        yr = int(input("Academic Year: "))
                        if yr < 4 or yr > 0:
                            break
                        print("Error: Year must be 1, 2 or 3.")
                    except ValueError:
                        print("Error: Academic Year must be a valid number.")
                
                academic_class = get_class_by_name(cls, yr)
                if academic_class:
                    break

            # 4. Validate Courses
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
                else:
                    break
            if not valid_format:
                break
            _ , msg = add_student(name, id_num, cls, yr, [x.strip() for x in courses])
            print(msg)
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
                print("\n[List of Academic Classes]\n")
                for ac in classes:
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

def check_overbooked():
    """Queries the ontology for rooms that have at least one booking."""
    print("\n[Overbooked Rooms Report]")
    
    # Get rooms that the ontology identifies as having bookings
    potential_conflict_rooms = onto.OverBookedRoom.instances()
    
    conflict_found = False

    for room in potential_conflict_rooms:
        # Get all bookings for this specific room
        bookings = [b for b in onto.RoomBooking.instances() if b.booked_in_room == room]
        
        # Sort bookings by start time for easier comparison
        bookings.sort(key=lambda x: x.has_start_time)
        
        room_conflicts = []
        
        # Compare every pair of bookings in the room to find overlaps
        for i in range(len(bookings)):
            for j in range(i + 1, len(bookings)):
                b1 = bookings[i]
                b2 = bookings[j]
                
                # Overlap logic: (Start1 < End2) AND (Start2 < End1)
                # Since these are datetime objects, this handles both same-day and time overlaps
                if (b1.has_start_time < b2.has_end_time) and (b2.has_start_time < b1.has_end_time):
                    room_conflicts.append((b1, b2))
        
        if room_conflicts:
            conflict_found = True
            print(f"\n[!] CONFLICT DETECTED in Room: {room.has_name}")
            for b1, b2 in room_conflicts:
                print(f"  Overlap found between:")
                print(f"    - {b1.has_name} ({b1.has_start_time.strftime('%Y-%m-%d %H:%M')} to {b1.has_end_time.strftime('%H:%M')})")
                print(f"    - {b2.has_name} ({b2.has_start_time.strftime('%Y-%m-%d %H:%M')} to {b2.has_end_time.strftime('%H:%M')})")

    if not conflict_found:
        print("No time-slot conflicts found. All room schedules are valid.")
    
    print("\n" + "-"*40)

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
                    suggestion = False
                else:
                    print(f"\n[Room Management] No available slots found in that interval and period of time.\nFound {len(slots)} suggested slots:")
                    suggestion = True
                print("-" * 50)
                if suggestion:
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
                    # Display with Numbers
                    for idx, b in enumerate(sorted_bookings, start=1):
                        start = b.has_start_time.strftime('%H:%M')
                        end = b.has_end_time.strftime('%H:%M')
                        print(f" {idx}. {start} - {end} | {b.has_name} (by {b.booked_by.has_name})")
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
        print("2. Rebooked Bookings (Maintenance)")
        print("3. Check Maintenance Bookings")
        print("4. Report Fixed Equipment in a Room")
        print("0. Back")
        
        choice = input("\nSelect: ")
        if choice == '1':
            r_name = input("Enter Room Name: ")
            room = get_room(r_name)
            if room and room.has_equipment:
                # Report the problem~
                eq_projector = room.has_equipment[0]
                if eq_projector.is_broken:
                    while True:
                        rebook = input("There exists a Maintenance Booking for this Room. Do you want to rebook? (y/n): ").lower().strip()
                        if rebook in ['y', 'n']:
                            if rebook == 'y':
                                maintenance_bookings = [
                                    b for b in onto.search(type=RoomBooking, booked_in_room=room)
                                    if isinstance(b.for_activity, MaintenanceActivity)
                                ]
                                for b in maintenance_bookings:
                                    print(f"Removing maintenance booking from schedule: {b.has_start_time.strftime('%Y-%m-%d %H:%M')}")
                                    destroy_entity(b)
                                break
                            else:
                                return
                        print("Please enter only 'y' for yes or 'n' for no.")

                for eq in room.has_equipment:
                    eq.is_broken = True
                print(f"Status: {r_name} projector reported as broken.")
                
                # Schedule Maintenance
                maintenance_slots = agent2.get_maintenance_slots(room)
                print("\nPossible Maintenance Slots:")
                for idx, m in enumerate(maintenance_slots, start=1):
                    start = m['start'].strftime('%H:%M')
                    end = m['end'].strftime('%H:%M')
                    slot_date = m['date']
                    print(f" {idx}. {slot_date} | {start} - {end}")
                
                while True:
                    sel = input(f"Select a slot (1-{len(maintenance_slots)} - Mandatory): ")
                    
                    if sel.isdigit():
                        idx = int(sel)
                        if 1 <= idx <= len(maintenance_slots):
                            chosen = maintenance_slots[idx-1]
                            # Book Maintenance
                            agent2.create_maintenance_booking(room, chosen["start"], chosen['end'])
                            print(f"\nSuccess: {chosen['room'].has_name} Maintenance booked for {chosen['date']} at {chosen['duration'][0]} - {chosen['duration'][1]}.")
                            break
                    print(f"Invalid choice. Pick a number between 1 and {len(maintenance_slots)}.")

                # Trigger Auto-Relocation
                affected = agent2.auto_relocate_affected(room)
                print(f"Success! Maintenance scheduled and {len(affected)} affected classes rebooked.\n These books where affected: {affected}")
            else:
                if not room:
                    print("Room not found.")
                else:
                    print("This Room has no Equipment.")

        elif choice == '2':
            print("\nRebooked Bookings (Maintenance)\n")
            relocated = onto.RelocatedBooking.instances()
            
            if not relocated:
                print("No rebooked classes found.")
            else:
                for b in relocated:
                    changed_time = b.has_start_time != b.original_start_time
                    status = " [TIME/DAY CHANGED]" if changed_time else " [ROOM ONLY]"
                    print(f"- {b.has_name}: Now in {b.booked_in_room.has_name} at {b.has_start_time} {status}")

            # Validation and manual re-adjustment (2.2 part 2)
            p_id = int(input("\nEnter Prof ID to manually adjust one of your rebooked classes or '0' to return): "))
            if p_id != 0:
                # Use Agent 1's flow to re-schedule a specific booking if the user isn't happy
                # TODO
                pass
        elif choice == '3':
            maintenance_slots = get_maintenance_books()
            if maintenance_slots:
                print(f"DEI MAINTENANCE SCHEDULE")
                print('='*50)
                for idx, book in enumerate(maintenance_slots, start=1):
                    start = book.has_start_time.strftime('%H:%M')
                    end = book.has_end_time.strftime('%H:%M')
                    slot_date = book.has_start_time.strftime("%Y-%m-%d")
                    room_m = book.booked_in_room.has_name
                    print(f" Room {room_m} | {slot_date} | {start} - {end}")
                    if idx < len(maintenance_slots):
                        print(" " + "-"*48)
                print('='*50)
            else:
                print("There is no Maintenance Bookings.")
        elif choice == '4':
            r_name = input("Enter the Room Name: ").strip()
            room = get_room(r_name)
            
            if not room:
                print(f"Error: Room '{r_name}' not found.")
                return

            # 1. Validate that equipment is broken
            broken_eq = [eq for eq in room.has_equipment if eq.is_broken]
            if not broken_eq:
                print(f"Error: Room '{r_name}' has no reported broken equipment.")
                return

            # 2. Validate that a maintenance booking exists for this room
            # We look for bookings where the activity is a MaintenanceActivity
            maintenance_bookings = [
                b for b in onto.search(type=RoomBooking, booked_in_room=room)
                if isinstance(b.for_activity, MaintenanceActivity)
            ]
            
            if not maintenance_bookings:
                print(f"Error: No maintenance booking found for Room '{r_name}'. Repair cannot be finalized without a record.")
                return

            # 3. Perform the fix: Switch is_broken to False
            for eq in broken_eq:
                eq.is_broken = False
                print(f"[System] - {eq.has_name} is now functional.")

            # 4. Delete the maintenance bookings associated with the room
            for b in maintenance_bookings:
                print(f"[System] - Removing maintenance booking from schedule: {b.has_start_time.strftime('%Y-%m-%d %H:%M')}")
                destroy_entity(b)
            
            # Save the changes to the .owl file
            save()
            print("\nRoom status updated and schedule cleared successfully.")
        elif choice == '0':
            return
        else:
            print("Invalid option. Please try again.")
        
def planning_menu():
    """Triggers the PDDL Automated Planners."""
    print("\n [Semester Planning]\n")
    print("1. Generate Weekly Class Template")
    print("2. Generate Exam Epoch Schedule")
    print("3. Back to Main Menu")
    # This will call the unified-planning solver as seen in planner.py
    input("\n[Placeholder] Press Enter to return...")

if __name__ == "__main__":
    main_menu()