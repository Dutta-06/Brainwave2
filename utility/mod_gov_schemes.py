import json
import os

class SchemeFinder:
    def __init__(self, db_path="schemes_db.json"):
        self.db_path = db_path
        # Create dummy DB if not exists
        if not os.path.exists(db_path):
            self._create_dummy_db()
        
        with open(db_path, 'r') as f:
            self.schemes = json.load(f)
        print(f"[Gov] Loaded {len(self.schemes)} schemes.")

    def _create_dummy_db(self):
        data = [
            {
                "name": "PM-Kisan Samman Nidhi",
                "benefit": "Rs 6000/year",
                "criteria": {"occupation": "farmer", "max_land_hectares": 2.0}
            },
            {
                "name": "Solar Pump Subsidy",
                "benefit": "60% cost subsidy",
                "criteria": {"occupation": "farmer", "state": "Rajasthan", "has_pump": False}
            },
            {
                "name": "Ladli Behna Yojana",
                "benefit": "Rs 1000/month",
                "criteria": {"gender": "female", "max_income": 250000}
            }
        ]
        with open(self.db_path, 'w') as f:
            json.dump(data, f, indent=4)

    def find_eligible_schemes(self, user_profile):
        """
        Matches user profile dict against scheme criteria logic.
        """
        eligible = []
        
        for scheme in self.schemes:
            criteria = scheme['criteria']
            is_match = True
            
            # Check every condition
            for key, required_val in criteria.items():
                user_val = user_profile.get(key)
                
                # Logic: Numeric Comparison (Max limits)
                if key.startswith("max_"):
                    real_key = key.replace("max_", "") # e.g. "land_hectares"
                    if user_profile.get(real_key, 999) > required_val:
                        is_match = False
                        break
                
                # Logic: Exact Match (Gender/State)
                elif user_val != required_val:
                    is_match = False
                    break
            
            if is_match:
                eligible.append(f"✓ {scheme['name']} ({scheme['benefit']})")
                
        return eligible if eligible else ["No eligible schemes found."]

# --- Test Block ---
if __name__ == "__main__":
    agent = SchemeFinder()
    
    # Test Profile: Small farmer, Female
    profile = {
        "occupation": "farmer",
        "gender": "female",
        "land_hectares": 1.5,
        "income": 100000,
        "has_pump": False,
        "state": "MP"
    }
    
    matches = agent.find_eligible_schemes(profile)
    print("Eligible Schemes:")
    for m in matches: print(m)