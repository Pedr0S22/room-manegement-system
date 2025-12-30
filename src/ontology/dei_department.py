import os
import sys
import datetime
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

    class AcademicClass(Thing):
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
    class Meeting(Activity):
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

    class BelongsToClass(Student >> AcademicClass, FunctionalProperty):
        python_name = "belongs_to_class"

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
        domain = [Activity | Course]
        range = [int]
        python_name = "required_capacity"

    class IsBroken(DataProperty, FunctionalProperty):
        domain = [Equipment]
        range = [bool]
        python_name = "is_broken"

    class StartHour(DataProperty, FunctionalProperty):
        domain = [RoomBooking]
        range = [int]
        python_name = "start_hour"

    class HasYear(DataProperty, FunctionalProperty):
        domain = [Student | Course | AcademicClass]
        range = [int]
        python_name = "has_year"

    class HasClassCode(DataProperty, FunctionalProperty):
        domain = [Student]
        range = [str]
        python_name = "has_class_code"
    class HasSemester(DataProperty, FunctionalProperty):
        domain = [Course]
        range = [int]
        python_name = "has_semester"

    class HasStartTime(DataProperty, FunctionalProperty):
        domain = [RoomBooking]
        range = [datetime.datetime]
        python_name = "has_start_time"

    class HasEndTime(DataProperty, FunctionalProperty):
        domain = [RoomBooking]
        range = [datetime.datetime]
        python_name = "has_end_time"

    class BookedBy(ObjectProperty, FunctionalProperty):
        domain = [RoomBooking]
        range = [Teacher]
        python_name = "booked_by"

    class OriginalStartTime(DataProperty, FunctionalProperty):
        domain = [RoomBooking]
        range = [datetime.datetime]
        python_name = "original_start_time"

    class OriginalEndTime(DataProperty, FunctionalProperty):
        domain = [RoomBooking]
        range = [datetime.datetime]
        python_name = "original_end_time"

    class IsRelocated(DataProperty, FunctionalProperty):
        domain = [RoomBooking]
        range = [bool]
        python_name = "is_relocated"

    # INFERRED CLASSES (First-Order Logic)

    class OverBookedRoom(Room):
        equivalent_to = [Room & Inverse(BookedInRoom).some(RoomBooking)]
    
    class UnsuitableProjectorRoomBooking(RoomBooking):
        equivalent_to = [RoomBooking & ForActivity.some(Activity & RequiresEquipment.some(Equipment & IsBroken.value(True)))]


    class AvailableRoom(Room):
        equivalent_to = [Room & Not(Inverse(BookedInRoom).some(RoomBooking))]

    class RelocatedBooking(RoomBooking):
        equivalent_to = [RoomBooking & IsRelocated.value(True)]

    class BrokenRoom(Room):
        equivalent_to = [Room & HasEquipment.some(Equipment & IsBroken.value(True))]


# Helper Functions to interact with ontology


def save():
    with onto:
        try:
            sync_reasoner(onto, infer_property_values=True, debug=False)
            onto.save(file=ONTOLOGY_FILE, format="rdfxml")
            print("[System] Data reasoned and saved successfully.")
        except Exception as e:
            print(f"[Warning] Reasoner found an inconsistency: {e}")
            onto.save(file=ONTOLOGY_FILE, format="rdfxml")

def get_room(name):
    return onto.search_one(type=Room, has_name=name)

def get_person_by_id(id_num):
    return onto.search_one(has_id=id_num)

def get_maintenance_books():
    return onto.search(type=RoomBooking, has_name="Maintenance")

def get_class_by_name(class_name, ac_year):
    return onto.search_one(type=AcademicClass, has_name=class_name, has_year=ac_year)

def add_room(name, capacity, has_proj):
    if get_room(name):
        return False, f"Error: Room '{name}' already exists."
    with onto:
        r = Room(name.replace(" ", "_"))
        r.has_name = name
        r.has_capacity = capacity
        if has_proj:
            # Create a unique projector instance for this specific room
            proj = Equipment(f"Projector_{r.name}")
            proj.has_name = f"Projector {name}"
            proj.is_broken = False
            r.has_equipment = [proj]
    save()
    return True, f"Room {name} added successfully."

def add_teacher(name, id_num, course_names):
    prof = get_person_by_id(id_num)
    if prof:
        return False, f"Error: ID {id_num} already assigned to {prof.has_name}."
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

        ac = onto.search_one(type=AcademicClass, has_name=class_code, has_year=year)
        if ac:
            s.belongs_to_class = ac
        else:
            print(f"[Warning] Academic Class '{class_code}' for year {year} not found. Link not created.")

        for c_name in course_names:
            course = onto.search_one(type=Course, has_name=c_name)
            if course: s.enrolled_in.append(course)
    save()
    return True, f"Student {name} added."

def add_course(name, year, semester, capacity):
    # Updated conjunction check: Name AND Year AND Semester
    if onto.search_one(type=Course, has_name=name, has_year=year, has_semester=semester):
        return False, f"Error: Course '{name}' (Year {year}, Sem {semester}) already exists."
    
    with onto:
        # Create a unique IRI including the semester
        c = Course(f"{name.replace(' ', '_')}_Y{year}_S{semester}")
        c.has_name = name
        c.has_year = year
        c.has_semester = semester
        c.required_capacity = capacity
    save()
    return True, f"Course {name} (Y{year}/S{semester}) added successfully."

def add_academic_class(name, year):
    # Conjunction check: verify if this class name and year already exist
    if onto.search_one(type=AcademicClass, has_name=name, has_year=year):
        return False, f"Error: Academic Class '{name}' for year {year} already exists."
    
    with onto:
        # Create unique IRI
        ac = AcademicClass(f"Class_{name.replace(' ', '_')}_{year}")
        ac.has_name = name
        ac.has_year = year
    save() # Ensure persistence
    return True, f"Academic Class {name} ({year}) added successfully."

def delete_booking(room, start, end, prof_id):
    """Deletes a booking with Prof ID validation."""

    prof = onto.search_one(type=Teacher, has_id=prof_id)

    if prof:
        booking = onto.search_one(
            type=RoomBooking,
            booked_in_room=room,
            booked_by=prof,
            has_start_time=start,
            has_end_time=end
        )
    else:
        return False, "Professor not found"
        
    if not booking:
        return False, "Booking not found."
    
    # Validation: Only the prof that made the book can delete it
    if booking.booked_by.has_id != prof_id:
        return False, "Permission Denied: You are not the owner of this booking."
    
    # Remove the activity and the booking
    destroy_entity(booking)

    save()
    return True, "Booking successfully deleted."

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