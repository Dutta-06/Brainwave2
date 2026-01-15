import requests
import json
import os
from datetime import datetime

class WeatherGuard:
    def __init__(self, cache_file="weather_cache.json"):
        self.cache_file = cache_file
        self.base_url = "https://api.open-meteo.com/v1/forecast"

    def get_forecast(self, lat=28.61, lon=77.20): # Default: New Delhi
        """
        Try Online -> Fail -> Fallback to Local Cache
        """
        try:
            # 1. Try Online Fetch
            print("[Weather] Connecting to satellite...")
            response = requests.get(
                self.base_url,
                params={"latitude": lat, "longitude": lon, "current_weather": "true"},
                timeout=5 # Short timeout for bad networks
            )
            response.raise_for_status()
            
            data = response.json()
            data['fetched_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Save to Cache
            with open(self.cache_file, 'w') as f:
                json.dump(data, f)
            
            return self._format_output(data, source="ONLINE")

        except (requests.ConnectionError, requests.Timeout):
            # 2. Offline Fallback
            print("[Weather] Connection failed. Checking cache...")
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                return self._format_output(data, source="OFFLINE (Cached)")
            else:
                return "Error: No internet and no cached weather data."

    def _format_output(self, data, source):
        curr = data.get('current_weather', {})
        temp = curr.get('temperature', 'N/A')
        wind = curr.get('windspeed', 'N/A')
        timestamp = data.get('fetched_at', 'Unknown')
        
        output = (
            f"--- WEATHER REPORT [{source}] ---\n"
            f"Temp: {temp}°C\n"
            f"Wind: {wind} km/h\n"
            f"Last Updated: {timestamp}\n"
        )
        
        if source.startswith("OFFLINE"):
            output += "WARNING: Data might be old. Look at the sky!"
            
        return output

# --- Test Block ---
if __name__ == "__main__":
    guard = WeatherGuard()
    # To test offline mode: Turn off WiFi and run this script.
    print(guard.get_forecast())