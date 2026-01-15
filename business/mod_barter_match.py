class BarterBrain:
    def __init__(self):
        # In a real app, this data comes from the AirGap Courier updates
        self.village_inventory = [
            {"name": "User (Self)", "has": "Rice Seeds", "needs": "Manure"},
            {"name": "Farmer A", "has": "Manure", "needs": "Rice Seeds"},
            {"name": "Farmer B", "has": "Tractor Service", "needs": "Diesel"},
            {"name": "Farmer C", "has": "Manure", "needs": "Cash"}
        ]

    def find_matches(self):
        """
        Algorithm: Finds 'Double Coincidence of Wants'
        """
        my_profile = self.village_inventory[0]
        matches = []

        print(f"[Barter] Looking for trade: I have {my_profile['has']}, I need {my_profile['needs']}...")

        for neighbor in self.village_inventory[1:]:
            # Perfect Match: They have what I need, AND I have what they need
            if (neighbor['has'] == my_profile['needs'] and 
                neighbor['needs'] == my_profile['has']):
                matches.append(f"PERFECT MATCH: Trade {my_profile['has']} with {neighbor['name']} for {neighbor['has']}.")
            
            # Partial Match: They just have what I need
            elif neighbor['has'] == my_profile['needs']:
                matches.append(f"PARTIAL MATCH: {neighbor['name']} has {neighbor['has']}, but wants {neighbor['needs']}.")

        if not matches:
            return ["No trades found today."]
        return matches

# --- Test Block ---
if __name__ == "__main__":
    matcher = BarterBrain()
    suggestions = matcher.find_matches()
    for s in suggestions:
        print(s)