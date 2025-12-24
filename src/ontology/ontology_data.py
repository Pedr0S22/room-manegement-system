from ontology.dei_department import *

def populate_system():
    print("=== Initializing DEI Data Population ===\n")

    # 1. Add Courses (Name, Year, Student Capacity)
    print("Adding Courses...")
    add_course("CRP", 3, 60)
    add_course("IA", 3, 100)
    add_course("PDS", 2, 80)
    # TODO: Add more courses for years 1, 2, and 3
    
    # 2. Add Academic Classes (Name, Year)
    print("Adding Academic Classes...")
    add_academic_class("LEI", 3)
    add_academic_class("LEI", 2)
    add_academic_class("LEI", 1)

    add_academic_class("LIACD", 3)
    add_academic_class("LIACD", 2)
    add_academic_class("LIACD", 1)

    add_academic_class("LDM", 3)
    add_academic_class("LDM", 2)
    add_academic_class("LDM", 1)

    
    # 3. Add Rooms (Name, Capacity, Has Projector)
    print("Adding Rooms...")
    add_room("G.5.1", 60, True)
    add_room("G.5.2", 40, True)
    add_room("B.1", 120, True)
    add_room("Amfiteatro_A", 250, True)
    add_room("Lab_1", 20, False)
    # TODO: Add more rooms (e.g., small meeting rooms, large auditoriums)

    # 4. Add Teachers (Name, ID > 99, List of Course Names)
    print("Adding Teachers...")
    add_teacher("Pedro Martins", 101, ["CRP", "IA"])
    add_teacher("Ricardo Pereira", 102, ["CRP"])
    # TODO: Add more teachers and assign them to existing courses

    # 5. Add Students (Name, ID, Class Name, Year, List of Course Names)
    print("Adding Students...")
    add_student("Joao Silva", 2021001, "LEI-A", 3, ["CRP", "IA"])
    add_student("Maria Santos", 2021002, "LEI-A", 3, ["CRP"])
    add_student("Tiago Ferreira", 2022001, "LDCT-A", 2, ["PDS"])
    # TODO: Add more students

    # 6. Finalize
    print("\nData population complete.")
    print("Running reasoner to verify inferred classes...")
    run_reasoner()
    
    # Check for anomalies immediately
    attention_rooms = onto.search(type=RoomNeedsAttention)
    if attention_rooms:
        print(f"Warning: The following rooms already need attention: {attention_rooms}")

if __name__ == "__main__":
    # Ensure the ontology is loaded
    if not onto:
        print("Error: Could not load ontology.")
    else:
        populate_system()
        print("\nAll data has been saved to dei_room_management.owl")