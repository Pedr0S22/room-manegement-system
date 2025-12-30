from owlready2 import *
from ontology.dei_department import *
from datetime import datetime, timedelta, time

class BookingAgent:
    def __init__(self, ontology):
        self.onto = ontology

    def validate_time_slots(self, start_t, end_t):
        """Checks if the requested time follows DEI rules."""
        # Rule 1: No weekends (Saturday=5, Sunday=6)
        if start_t.weekday() >= 5:
            return False, "DEI rooms are closed on Saturdays and Sundays."
        
        # Rule 2: Operating hours (09:00 - 20:00)
        if start_t.hour < 9 or end_t.hour > 20 or (end_t.hour == 20 and end_t.minute > 0):
            return False, "DEI rooms are only available from 09:00 to 20:00."
        
        # Rule 3: Lunch/Maintenance block (13:00 - 14:00)
        if start_t.hour < 14 and end_t.hour > 13:
            return False, "13:00-14:00 is reserved for Maintenance/Lunch."

        # Rule 4: Hourly blocks
        if start_t.minute != 0 or end_t.minute != 0:
            return False, "Bookings must be in exact hourly blocks."

        return True, "Success"

    def get_available_rooms(self, capacity_needed, start_t, end_t, needs_projector=False):
        """Searches for the smallest suitable room within DEI constraints."""
        all_rooms = list(self.onto.Room.instances())
        suitable = [r for r in all_rooms if r.has_capacity >= capacity_needed]
        
        if needs_projector:
        # Check if the room has any equipment (projector)
            suitable = [
                r for r in suitable
                if r.has_equipment and not any(eq.is_broken for eq in r.has_equipment)
            ]

        available = []
        for room in suitable:
            if not self._is_room_busy(room, start_t, end_t):
                available.append(room)
        
        # Sort by capacity to propose the 'minimum space possible' [DEI optimization]
        available.sort(key=lambda x: x.has_capacity)
        return available
    
    def get_available_slots_in_interval(self, capacity, start_date, end_date, start_hour, num_hours, needs_proj):
        """Returns a list of (date, room) tuples that are available."""
        available_slots = []
        delta = (end_date - start_date).days

        def check_slot(target_day, h_start, duration):
            dt_start = datetime.combine(target_day, time.min).replace(hour=h_start)
            dt_end = dt_start + timedelta(hours=duration)
            
            # This calls your Rule 3: if start < 14 and end > 13, it returns False
            is_valid, _ = self.validate_time_slots(dt_start, dt_end)
            if not is_valid:
                return None
                
            rooms = self.get_available_rooms(capacity, dt_start, dt_end, needs_proj)
            if rooms:
                return [{
                    "date": target_day,
                    "duration": (dt_start.strftime('%H:%M'), dt_end.strftime('%H:%M')),
                    "room": r,
                    "start": dt_start,
                    "end": dt_end,
                    "suggestion": False
                } for r in rooms]
            return None
        
        # Iterate through every day in the requested range
        # 1. Primary Search
        for i in range(delta + 1):
            day = start_date + timedelta(days=i)
            if day.weekday() >= 5: continue
            
            found = check_slot(day, start_hour, num_hours)
            if found:
                available_slots.extend(found)

        # 2. Hypothesis Search: Only triggers if the specific hour was fully booked
        if not available_slots:
            print("\n[Notice]: Requested time slot is full or invalid. Finding alternative hypotheses...")
            for i in range(delta + 1):
                day = start_date + timedelta(days=i)
                if day.weekday() >= 5: continue
                
                # Range 9 to 19 (Last possible start is 19:00 for a 1h booking)
                for alt_hour in range(9, 20):
                    # Optimization: Skip the 13:00 start immediately
                    # And skip the original start_hour we already checked
                    if alt_hour == 13 or alt_hour == start_hour:
                        continue
                    
                    found_alt = check_slot(day, alt_hour, num_hours)
                    if found_alt:
                        for item in found_alt:
                            item["suggestion"] = True
                        available_slots.extend(found_alt)

        # Sort: Date -> Time -> Smallest Room Capacity
        available_slots.sort(key=lambda x: (x['date'], x["start"], x['room'].has_capacity))
        return available_slots

    def _is_room_busy(self, room, start_t, end_t):
        """Conflict check against existing RoomBookings."""
        if room in self.onto.AvailableRoom.instances():
            return False # It is impossible for it to be busy
        bookings = self.onto.search(type=self.onto.RoomBooking, booked_in_room=room)
        for b in bookings:
            # Check for any temporal overlap
            if (start_t < b.has_end_time) and (end_t > b.has_start_time):
                return True
        return False

    def create_booking(self, prof, room, start_t, end_t, b_type, capacity, needs_proj=False, course=None):
        with self.onto:
            b_id = f"Booking_{int(start_t.timestamp())}_{room.name}"
            new_b = self.onto.RoomBooking(b_id)
            new_b.booked_in_room = room
            new_b.booked_by = prof
            new_b.has_start_time = start_t
            new_b.has_end_time = end_t
            new_b.has_name = f"{b_type}: {course.has_name if course else 'Meeting'}"
            
            # Initialize relocation properties as None/False
            new_b.is_relocated = False

            if b_type == "Course":
                act = self.onto.Lecture()
                # Courses always need the projector if the room has one
                if room.has_equipment:
                    act.requires_equipment = room.has_equipment
            else:
                act = self.onto.Meeting()
                # Meetings only link equipment if the teacher explicitly requested it
                if needs_proj and room.has_equipment:
                    act.requires_equipment = room.has_equipment
            
            # Universal capacity assignment
            act.required_capacity = capacity
            new_b.for_activity = act
        save()
        return new_b
    
    
    # Helper Functions to interact with ontology


    def get_room(self, name):
        return self.onto.search_one(type=Room, has_name=name)

    def get_person_by_id(self, id_num):
        return self.onto.search_one(has_id=id_num)

    def get_maintenance_books(self):
        return self.onto.search(type=RoomBooking, has_name="Maintenance")

    def get_class_by_name(self, class_name, ac_year):
        return self.onto.search_one(type=AcademicClass, has_name=class_name, has_year=ac_year)

    def add_room(self, name, capacity, has_proj):
        if self.get_room(name):
            return False, f"Error: Room '{name}' already exists."
        with self.onto:
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

    def add_teacher(self, name, id_num, course_names):
        prof = self.get_person_by_id(id_num)
        if prof:
            return False, f"Error: ID {id_num} already assigned to {prof.has_name}."
        with self.onto:
            t = Teacher(f"T_{id_num}")
            t.has_name = name
            t.has_id = id_num
            for c_name in course_names:
                course = self.onto.search_one(type=Course, has_name=c_name)
                if course: t.teaches.append(course)
        save()
        return True, f"Teacher {name} added."

    def add_student(self, name, id_num, class_code, year, course_names):
        if self.get_person_by_id(id_num):
            return False, f"Error: ID {id_num} already exists."
        with self.onto:
            s = Student(f"S_{id_num}")
            s.has_name = name
            s.has_id = id_num
            s.has_class_code = class_code
            s.has_year = year

            ac = self.onto.search_one(type=AcademicClass, has_name=class_code, has_year=year)
            if ac:
                s.belongs_to_class = ac
            else:
                print(f"[Warning] Academic Class '{class_code}' for year {year} not found. Link not created.")

            for c_name in course_names:
                course = self.onto.search_one(type=Course, has_name=c_name)
                if course: s.enrolled_in.append(course)
        save()
        return True, f"Student {name} added."

    def add_course(self, name, year, semester, capacity):
        # Updated conjunction check: Name AND Year AND Semester
        if self.onto.search_one(type=Course, has_name=name, has_year=year, has_semester=semester):
            return False, f"Error: Course '{name}' (Year {year}, Sem {semester}) already exists."
        
        with self.onto:
            # Create a unique IRI including the semester
            c = Course(f"{name.replace(' ', '_')}_Y{year}_S{semester}")
            c.has_name = name
            c.has_year = year
            c.has_semester = semester
            c.required_capacity = capacity
        save()
        return True, f"Course {name} (Y{year}/S{semester}) added successfully."

    def add_academic_class(self, name, year):
        # Conjunction check: verify if this class name and year already exist
        if self.onto.search_one(type=AcademicClass, has_name=name, has_year=year):
            return False, f"Error: Academic Class '{name}' for year {year} already exists."
        
        with self.onto:
            # Create unique IRI
            ac = AcademicClass(f"Class_{name.replace(' ', '_')}_{year}")
            ac.has_name = name
            ac.has_year = year
        save() # Ensure persistence
        return True, f"Academic Class {name} ({year}) added successfully."

    def delete_booking(self, room, start, end, prof_id):
        """Deletes a booking with Prof ID validation."""

        prof = self.onto.search_one(type=Teacher, has_id=prof_id)

        if prof:
            booking = self.onto.search_one(
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
