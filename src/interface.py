import sys
from ontology.dei_department import *

def main_menu():
    """Displays the primary navigation menu."""
    while True:
        print("\n===== DEI Room Management System =====\n")
        print("1. Administrative Management\n")
        print("2. Live Status & Queries (Ontology Reasoning)")
        print("3. Room Bookings & Ad-hoc Requests (Agent 1)")
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
            sys.exit()
        else:
            print("Invalid option. Please try again.")

def management_menu():
    while True:
        print("\n[Administrative Management]")
        print("1. Rooms Management")
        print("2. Teacher Management")
        print("3. Student Management")
        print("4. Course Management")
        print("5. Clear All Data")
        print("0. Back to Main Menu")
        
        choice = input("\nSelect: ")
        if choice == '1': room_mgmt()
        elif choice == '2': teacher_mgmt()
        elif choice == '3': student_mgmt()
        elif choice == '4': course_mgmt()
        elif choice == '5': clean_onto()
        elif choice == '0': main_menu()

def room_mgmt():
    print("\n[Room Management]\n")
    print("1. Add Room\n2. List Rooms\n0. Exit\n")
    c = input("Choice: ")
    if c == '1':
        name = input("Name: ")
        cap = int(input("Capacity: "))
        proj = input("Has Projector? (y/n): ").lower() == 'y'
        _ , msg = add_room(name, cap, proj)
        print(msg)
    elif c == '2':
        for r in onto.Room.instances():
            eq = "Projector" if onto.Projector in r.has_equipment else "None"
            print(f"- {r.has_name} (Cap: {r.has_capacity}, Equipment: {eq})")
    elif c == '0':
        management_menu()
    else:
        print("Invalid choice. Choose option 1, 2 or 0 to exit")
        room_mgmt()

def teacher_mgmt():
    print("\n[Teacher Management]\n")
    print("1. Add Teacher\n2. List Teachers\n0. Exit\n")
    c = input("Choice: ")
    if c == '1':
        name = input("Name: ")
        id_num = int(input("ID: "))
        courses = input("Courses (comma separated names): ").split(",")
        _ , msg = add_teacher(name, id_num, [x.strip() for x in courses])
        print(msg)
    elif c == '2':
        for t in onto.Teacher.instances():
            c_list = [c.has_name for c in t.teaches]
            print(f"ID {t.has_id}: {t.has_name} | Teaches: {c_list}")
    elif c == '0':
        management_menu()
    else:
        print("Invalid choice. Choose option 1 or 2")
        teacher_mgmt()

def student_mgmt():
    print("\n[Student Management]\n")
    print("1. Add Student\n2. List Students\n0. Exit\n")
    c = input("Choice: ")
    if c == '1':
        name = input("Name: ")
        id_num = int(input("ID: "))
        cls = input("Class Code: ")
        yr = int(input("Year: "))
        courses = input("Enrolled Courses (comma separated): ").split(",")
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
        
        management_menu()
    elif c == '0':
        management_menu()
    else:
        print("Invalid choice. Choose option 1 or 2")
        student_mgmt()
    

def course_mgmt():
    print("\n[Course Management]\n")
    print("1. Add Course\n2. List\n0. Exit\n")
    c = input("Choice: ")
    if c == '1':
        name = input("Course Name: ")
        _ , msg = add_course(name)
        print(msg)
    elif c == '2':
        print([c.has_name for c in onto.Course.instances()])
    elif c == '0':
        management_menu()
    else:
        print("Invalid choice. Choose option 1, 2 or 0 to exit")
        course_mgmt()

def queries_menu():
    
    while True:
        print("Nothing yet...")
        choice = input("\nExit pressing 0: ")
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
    """Interface for Agent 1 to handle new requests."""
    print("\n--- Room Bookings (Agent 1) ---")
    print("1. New Lecture Booking Request")
    print("2. Emergency Room Change (Equipment Failure)")
    print("3. Back to Main Menu")
    # This will trigger Agent 1's logic to search and assign rooms
    input("\n[Placeholder] Press Enter to return...")

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