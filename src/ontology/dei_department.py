import os
import time
import pathlib
from owlready2 import *

BASE_PATH = pathlib.Path(__file__).parent.resolve()
ONTOLOGY_FILE = str(BASE_PATH / "dei_room_management.owl")

owlready2.JAVA_EXE = "java"

if os.path.exists(ONTOLOGY_FILE):
    onto = get_ontology(ONTOLOGY_FILE).load()
else:
    onto = get_ontology(ONTOLOGY_FILE)

with onto:
    # ONTOLOGY CLASSES (Categories)

    # Room related classes
    class Room(Thing):
        pass

    class RoomBooking(Thing):
        pass

    class Equipment(Thing):
        pass

    class Course(Thing):
        pass
    
    # Person related classes
    class Person(Thing):
        pass
    class Teacher(Person):
        pass
    class Student(Person):
        pass
    
    # Activity related classes
    class Activity(Thing):
        pass
    class Lecture(Activity):
        pass
    class Exam(Activity):
        pass
    class MaintenanceActivity(Activity):
        pass
    
    # Other classes
    class DayOfWeek(Thing):
        pass

    # OBJECT PROPERTIES (Relations)

    class BookedInRoom(RoomBooking >> Room, FunctionalProperty):
        python_name = "booked_in_room"

    class ForActivity(RoomBooking >> Activity, FunctionalProperty):
        python_name = "for_activity"

    class HasEquipment(Room >> Equipment):
        python_name = "has_equipment"

    class RequiresEquipment(Activity >> Equipment):
        python_name = "requires_equipment"

    class OccursOnDay(RoomBooking >> DayOfWeek, FunctionalProperty):
        python_name = "occurs_on_day"

    class Teaches(Teacher >> Course):
        python_name = "teaches"

    class EnrolledIn(Student >> Course):
        python_name = "enrolled_in"

    # DATA PROPERTIES

    class HasId(DataProperty, FunctionalProperty):
        domain = [Person]
        range = [int]
        python_name = "has_id"

    class HasName(DataProperty, FunctionalProperty):
        domain = [Thing]
        range = [str]
        python_name = "has_name"

    class HasCapacity(DataProperty, FunctionalProperty):
        domain = [Room]
        range = [int]
        python_name = "has_capacity"

    class RequiredCapacity(DataProperty, FunctionalProperty):
        domain = [Activity]
        range = [int]
        python_name = "required_capacity"

    class IsBroken(DataProperty, FunctionalProperty):
        domain = [Equipment]
        range = [bool]
        python_name = "is_broken"

    class AccumulatedUsage(DataProperty, FunctionalProperty):
        domain = [Room]
        range = [int]
        python_name = "accumulated_usage"

    class StartHour(DataProperty, FunctionalProperty):
        domain = [RoomBooking]
        range = [int]
        python_name = "start_hour"

    class HasYear(DataProperty, FunctionalProperty):
        domain = [Student]
        range = [int]
        python_name = "has_year"

    class HasClassCode(DataProperty, FunctionalProperty):
        domain = [Student]
        range = [str]
        python_name = "has_class_code"

    # INFERRED CLASSES (First-Order Logic)

    class OverBookedRoom(Room):
        equivalent_to = [Room & Inverse(BookedInRoom).some(RoomBooking)] # Simplified
    
    class UnsuitableRoomBooking(RoomBooking):
        equivalent_to = [RoomBooking & ForActivity.some(Activity & RequiresEquipment.some(Equipment & IsBroken.value(True)))]

    class RoomNeedsAttention(Room):
        equivalent_to = [Room & AccumulatedUsage.some(ConstrainedDatatype(int, min_inclusive=21))]

    class AvailableRoom(Room):
        equivalent_to = [Room & Not(Inverse(BookedInRoom).some(RoomBooking))]

    class OverloadedTeacher(Teacher): # Creative: Teachers with more than 3 courses
        equivalent_to = [Teacher & Teaches.min(4, Course)]

    class LargeExamRoom(Room): # Creative: High capacity rooms for exams
        equivalent_to = [Room & HasCapacity.some(ConstrainedDatatype(int, min_inclusive=100))]

    # --- INITIAL INDIVIDUALS ---
    projector = Equipment("Projector")
    projector.has_name = "Standard Projector"
    projector.is_broken = False

# --- VALIDATION & PERSISTENCE HELPER FUNCTIONS ---

def save():
    onto.save(file=ONTOLOGY_FILE, format="rdfxml")

def get_room(name):
    return onto.search_one(type=Room, has_name=name)

def get_person_by_id(id_num):
    return onto.search_one(has_id=id_num)

def add_room(name, capacity, has_proj):
    if get_room(name):
        return False, f"Error: Room '{name}' already exists."
    with onto:
        r = Room(name.replace(" ", "_"))
        r.has_name = name
        r.has_capacity = capacity
        r.accumulated_usage = 0
        if has_proj: r.has_equipment = [onto.Projector]
    save()
    return True, f"Room {name} added successfully."

def add_teacher(name, id_num, course_names):
    if get_person_by_id(id_num):
        return False, f"Error: ID {id_num} already assigned to {get_person_by_id(id_num).has_name}."
    with onto:
        t = Teacher(f"T_{id_num}")
        t.has_name = name
        t.has_id = id_num
        for c_name in course_names:
            course = onto.search_one(type=Course, has_name=c_name)
            if course: t.teaches.append(course)
    save()
    return True, f"Teacher {name} added."

def add_student(name, id_num, class_code, year, course_names):
    if get_person_by_id(id_num):
        return False, f"Error: ID {id_num} already exists."
    with onto:
        s = Student(f"S_{id_num}")
        s.has_name = name
        s.has_id = id_num
        s.has_class_code = class_code
        s.has_year = year
        for c_name in course_names:
            course = onto.search_one(type=Course, has_name=c_name)
            if course: s.enrolled_in.append(course)
    save()
    return True, f"Student {name} added."

def add_course(name):
    if onto.search_one(type=Course, has_name=name):
        return False, f"Error: Course '{name}' already exists."
    with onto:
        c = Course(name.replace(" ", "_"))
        c.has_name = name
    save()
    return True, f"Course {name} added."

def clean_onto():

    default_world.close()

    if os.path.exists(ONTOLOGY_FILE):
        try:
            os.remove(ONTOLOGY_FILE)
            print(f"Successfully deleted Ontology!\n")
            print("!! NOTICE !!\nThe program must be restart the to clear Python class definitions.")
            
            time.sleep(2)
            
            sys.exit(0)
        except Exception as e:
            print(f"Error deleting Ontology: {e}")
            return
    else:
        print("No Ontology initialized!")