import json
import os

class RentalAgent:
    def __init__(self, db_file="tractor_schedule.json"):
        self.db_file = db_file
        if os.path.exists(db_file):
            with open(db_file, 'r') as f:
                self.schedule = json.load(f)
        else:
            self.schedule = {} # Format: {"YYYY-MM-DD": {"09:00": "Ravi"}}

    def check_availability(self, date, time_slot):
        if date in self.schedule and time_slot in self.schedule[date]:
            return False, self.schedule[date][time_slot]
        return True, None

    def book_slot(self, date, time_slot, farmer_name):
        """
        Smart Booking: Checks conflicts before confirming.
        """
        is_free, holder = self.check_availability(date, time_slot)
        
        if not is_free:
            return f"CONFLICT: Slot {time_slot} on {date} is already booked by {holder}."
        
        if date not in self.schedule:
            self.schedule[date] = {}
        
        self.schedule[date][time_slot] = farmer_name
        self._save_db()
        return f"SUCCESS: Tractor booked for {farmer_name} on {date} at {time_slot}."

    def _save_db(self):
        with open(self.db_file, 'w') as f:
            json.dump(self.schedule, f, indent=4)

# --- Test Block ---
if __name__ == "__main__":
    manager = RentalAgent()
    print(manager.book_slot("2026-02-14", "Morning", "Ramesh"))
    print(manager.book_slot("2026-02-14", "Morning", "Suresh")) # Should fail
    print(manager.book_slot("2026-02-14", "Evening", "Suresh")) # Should pass