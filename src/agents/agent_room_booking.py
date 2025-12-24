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
            projector_obj = self.onto.search_one(has_name="Standard Projector")
            suitable = [r for r in suitable if projector_obj in r.has_equipment]

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
        
        # Iterate through every day in the requested range
        for i in range(delta + 1):
            day = start_date + timedelta(days=i)
            
            # Skip Weekends
            if day.weekday() >= 5:
                continue
                
            check_start = datetime.combine(day, time.min).replace(hour=start_hour)
            check_end = check_start + timedelta(hours=num_hours)
            
            # Validation for DEI Operating Hours and Lunch
            is_valid, _ = self.validate_time_slots(check_start, check_end)
            if not is_valid:
                continue

            # Find all rooms for this specific day/time
            # We use the existing logic to find suitable rooms
            rooms = self.get_available_rooms(capacity, check_start, check_end, needs_proj)
            
            for r in rooms:
                available_slots.append({
                    "date": day,
                    "room": r,
                    "start": check_start,
                    "end": check_end
                })
                
        # Sort slots: earliest date first, then smallest room capacity
        available_slots.sort(key=lambda x: (x['date'], x['room'].has_capacity))
        return available_slots

    def _is_room_busy(self, room, start_t, end_t):
        """Conflict check against existing RoomBookings."""
        bookings = self.onto.search(type=self.onto.RoomBooking, booked_in_room=room)
        for b in bookings:
            # Check for any temporal overlap
            if (start_t < b.has_end_time) and (end_t > b.has_start_time):
                return True
        return False

    def create_booking(self, prof, room, start_t, end_t, b_type, course=None):
        with self.onto:
            b_id = f"Booking_{int(start_t.timestamp())}_{room.name}"
            new_b = self.onto.RoomBooking(b_id)
            new_b.booked_in_room = room
            new_b.booked_by = prof
            new_b.has_start_time = start_t
            new_b.has_end_time = end_t
            new_b.has_name = f"{b_type}: {course.has_name if course else 'Meeting'}"
            
            if course:
                new_b.for_activity = self.onto.Lecture() # Mapping to DEI Activity types
        return new_b
    
    def emergency_relocate(self, booking):
        """Automatically moves a booking to a new room if the current one is unsuitable."""
        print(f"[Agent 1] Initiating emergency relocation for {booking.has_name}...")
        
        # Calculate requirements
        capacity = 0
        if hasattr(booking, "for_course") and booking.for_course:
            capacity = booking.for_course.required_capacity
        
        # Search for a new room for the same time slot
        # Assuming the relocation is triggered because a projector is needed but broken
        options = self.get_available_rooms(
            capacity,
            booking.has_start_time,
            booking.has_end_time,
            needs_projector=True
        )

        # Filter out the current broken room
        options = [r for r in options if r != booking.booked_in_room]

        if options:
            new_room = options[0] # Smallest fit first
            old_room_name = booking.booked_in_room.has_name
            booking.booked_in_room = new_room
            return True, f"Booking moved from {old_room_name} to {new_room.has_name}."
        
        return False, "No suitable alternative rooms available for this slot."