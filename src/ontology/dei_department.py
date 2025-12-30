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