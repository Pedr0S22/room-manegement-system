import random
from datetime import datetime, timedelta, time
from ontology.dei_department import RoomBooking, save, sync_reasoner, MaintenanceActivity
from agents.agent_room_booking import BookingAgent

class MaintenanceAgent:
    def __init__(self, ontology):
        self.onto = ontology
        self.booking_agent = BookingAgent(ontology)

    def get_maintenance_slots(self, room, num_days=5):
        """
        Simulates a phone call from maintenance providing 3-6 random valid slots.
        Returns a list of dictionaries formatted like Agent 1's output.
        """
        lunch_candidates = []
        other_candidates = []

        # Collect all valid 1-hour slots across the requested range
        for i in range(1, num_days + 1):
            target_date = datetime.now().date() + timedelta(days=i)
            
            # Respect DEI weekend rules
            if target_date.weekday() >= 5:
                continue
            
            # Check operating hours (9:00 to 20:00)
            for hour in range(9, 20):
                dt_start = datetime.combine(target_date, time(hour, 0))
                dt_end = dt_start + timedelta(hours=1)
                
                # Check for conflicts (Agent 1 logic)
                if not self.booking_agent._is_room_busy(room, dt_start, dt_end):
                    slot_data = {
                        "date": target_date,
                        "duration": (dt_start.strftime('%H:%M'), dt_end.strftime('%H:%M')),
                        "room": room,
                        "start": dt_start,
                        "end": dt_end
                    }
                    if hour == 13:
                        lunch_candidates.append(slot_data)
                    else:
                        other_candidates.append(slot_data)

        # Determine number of slots to offer (3-6)
        num_to_offer = random.randint(3, 6)
        offered_slots = []

        # At least one lunch slot (if available)
        if lunch_candidates:
            first_choice = random.choice(lunch_candidates)
            offered_slots.append(first_choice)
            lunch_candidates.remove(first_choice)

        # High probability for remaining lunch slots
        # Create a weighted pool where lunch slots appear 2 times more often
        weighted_pool = other_candidates + (lunch_candidates * 2)
        
        # We need unique slots, so we keep track of selected datetimes
        selected_starts = {offered_slots[0]['start']} if offered_slots else set()

        while len(offered_slots) < num_to_offer and weighted_pool:
            candidate = random.choice(weighted_pool)
            
            if candidate['start'] not in selected_starts:
                offered_slots.append(candidate)
                selected_starts.add(candidate['start'])
            
            # Clean up the pool if we've exhausted options
            weighted_pool = [c for c in weighted_pool if c['start'] not in selected_starts]

        # Sort by most recent (chronological ascending)
        offered_slots.sort(key=lambda x: x['start'])
        
        return offered_slots
    
    def create_maintenance_booking(self, room, start_t, end_t):
        """Business logic for maintenance bookings moved to Ontology."""
        with self.onto:
            m_id = f"Maint_{int(start_t.timestamp())}_{room.name}"
            m_book = RoomBooking(m_id)
            m_book.booked_in_room = room
            m_book.has_start_time = start_t
            m_book.has_end_time = end_t
            m_book.for_activity = MaintenanceActivity()
            m_book.has_name = "Maintenance"
        save()
        return m_book

    def auto_relocate_affected(self, room):
        
        # Find bookings flagged by the reasoner as Unsuitable for this specific room
        affected = [b for b in self.onto.PendingRelocationBooking.instances()
                if b.booked_in_room == room]
        
        relocated_list = []
        for b in affected:
            # 1. Store history using new properties before moving
            if not b.original_start_time:
                b.original_start_time = b.has_start_time
                b.original_end_time = b.has_end_time

            # 2. Attempt relocation using Agent 1's logic
            success, msg = self.emergency_relocate(b)
            if success:
                b.is_relocated = True
                relocated_list.append(b)
        save()
        return relocated_list
    
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
            save()
            return True, f"Booking moved from {old_room_name} to {new_room.has_name}."
        
        return False, "No suitable alternative rooms available for this slot."