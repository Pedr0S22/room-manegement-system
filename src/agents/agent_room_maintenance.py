from datetime import datetime, timedelta, time
from ontology.dei_department import RoomBooking, save, sync_reasoner, MaintenanceActivity
from agents.agent_room_booking import BookingAgent

class MaintenanceAgent:
    def __init__(self, ontology):
        self.onto = ontology
        self.booking_agent = BookingAgent(ontology)

    def get_maintenance_slots(self, room, num_days=3):
        """Returns slots specifically during the 13:00-14:00 Lunch/Maintenance window."""
        slots = []
        for i in range(1, num_days + 1):
            day = datetime.now().date() + timedelta(days=i)
            if day.weekday() >= 5: continue # Skip weekends
            
            dt_start = datetime.combine(day, time(13, 0))
            dt_end = dt_start + timedelta(hours=1)
            
            # Ensure the slot is available in the ontology
            if not self.booking_agent._is_room_busy(room, dt_start, dt_end):
                slots.append(dt_start)
        return slots

    def auto_relocate_affected(self, room):
        """Uses 'UnsuitableRoomBooking' and the new data properties."""
        sync_reasoner(self.onto)
        # Find bookings flagged by the reasoner as Unsuitable for this specific room
        affected = [b for b in self.onto.UnsuitableRoomBooking.instances()
                    if b.booked_in_room == room]
        
        relocated_list = []
        for b in affected:
            # 1. Store history using new properties before moving
            if not b.original_start_time:
                b.original_start_time = b.has_start_time
                b.original_end_time = b.has_end_time

            # 2. Attempt relocation using Agent 1's logic
            success, msg = self.booking_agent.emergency_relocate(b)
            if success:
                b.is_relocated = True
                relocated_list.append(b)
        save()
        return relocated_list
    
    def add_maintenance_booking(self, room, start_t, end_t):
        """Business logic for maintenance bookings moved to Ontology."""
        with self.onto:
            m_id = f"Maint_{int(start_t.timestamp())}_{room.name}"
            m_book = RoomBooking(m_id)
            m_book.booked_in_room = room
            m_book.has_start_time = start_t
            m_book.has_end_time = end_t
            m_book.for_activity = MaintenanceActivity()
            m_book.has_name = "System Maintenance"
        save()
        return m_book