import os
import sys
import time

# --- IMPORTING MODULES ---
# We wrap imports in try-except blocks to prevent crashing if a module is missing
try:
    # Module 1: IO & Diagnostics
    from diagnostic import mod_voice_local, mod_airgap_courier, mod_machinery_hear
    
    # Module 2: Intelligence
    from intelligence import mod_llama_brain, mod_rag_store
    
    # Module 3: Vision
    from agri import mod_crop_doctor, mod_inventory_cam, mod_quality_grader
    
    # Module 4: Business
    from business import mod_contract_maker, mod_khata_ledger, mod_rental_scheduler, mod_barter_match
    
    # Module 5: Utility
    from utility import mod_offline_maps, mod_gov_schemes, mod_weather_cache

except ImportError as e:
    print(f"CRITICAL ERROR: Missing module. {e}")
    print("Ensure all mod_*.py files are in this directory.")
    sys.exit(1)

# --- HELPER FUNCTIONS ---

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_file_input(extensions):
    """
    Robust file requester. 
    Args:
        extensions (list): Valid file types e.g. ['.wav', '.mp3']
    """
    while True:
        path = input(f"\n[INPUT] Enter path to file ({'/'.join(extensions)}): ").strip().strip('"')
        if path.lower() == 'back':
            return None
            
        if not os.path.exists(path):
            print("❌ File not found. Please try again or type 'back'.")
            continue
            
        _, ext = os.path.splitext(path)
        if ext.lower() not in extensions:
            print(f"❌ Invalid format. Supported: {extensions}")
            continue
            
        return path

def print_header(title):
    clear_screen()
    print("="*60)
    print(f"   GRAM-OS v1.0  |  {title}")
    print("="*60)
    print(" [OFFLINE MODE ACTIVE] ")
    print("-" * 60)

# --- SUB-MENUS ---

def menu_diagnostics():
    while True:
        print_header("MODULE 1: DIAGNOSTICS & I/O")
        print("1. Voice Interface (Transcribe Audio File)")
        print("2. Air-Gap Courier (Scan/Generate QR)")
        print("3. Tractor Doctor (Diagnose Engine Audio)")
        print("0. Back to Main Menu")
        
        choice = input("\nSelect Option: ")
        
        if choice == '1':
            print("\n--- VOICE TRANSCRIBER ---")
            f = get_file_input(['.wav', '.mp3', '.m4a'])
            if f:
                bot = mod_voice_local.VoiceBot()
                # We assume we modified the class to accept a file, or we mock it here:
                # For strict adherence to the previous script, we might need to access the internal model directly
                print("Processing...")
                result = bot.stt_model.transcribe(f)
                print(f"\n💬 Transcription: {result['text']}")
                input("\nPress Enter to continue...")

        elif choice == '2':
            print("\n--- AIR-GAP COURIER ---")
            print("A. Generate QR (Send Data)")
            print("B. Scan QR (Read Image File)")
            sub = input("Select A or B: ").upper()
            courier = mod_airgap_courier.AirGapCourier()
            
            if sub == 'A':
                data = {"type": "demo_order", "content": "50kg Rice"}
                courier.generate_qr(data)
            elif sub == 'B':
                f = get_file_input(['.png', '.jpg', '.jpeg'])
                if f:
                    # We need to mock the camera capture by reading the file
                    # Modifying the previous script logic slightly to just read the image:
                    import cv2
                    from pyzbar.pyzbar import decode
                    img = cv2.imread(f)
                    decoded = decode(img)
                    if decoded:
                        print(f"📦 Data Found: {decoded[0].data.decode('utf-8')}")
                    else:
                        print("❌ No QR Code detected in image.")
            input("\nPress Enter to continue...")

        elif choice == '3':
            print("\n--- TRACTOR DOCTOR ---")
            f = get_file_input(['.wav'])
            if f:
                import librosa
                # Load the audio file and process
                doc = mod_machinery_hear.TractorDoctor()
                audio, _ = librosa.load(f, sr=22050, duration=3) # Load 3s
                
                # Mocking the live record function by passing loaded audio directly
                # Note: You might need to adjust the class to accept raw array if not already
                diagnosis, conf = doc.diagnose(audio)
                print(f"\n🚜 Diagnosis: {diagnosis} (Confidence: {conf:.2f})")
            input("\nPress Enter to continue...")

        elif choice == '0':
            break

def menu_intelligence():
    # Initialize Brain once to save loading time
    print("Loading AI Brain... (Please wait)")
    brain = mod_llama_brain.LlamaEngine()
    rag = mod_rag_store.RAGStore()
    
    while True:
        print_header("MODULE 2: INTELLIGENCE")
        print("1. Chat with Gram-Assistant (TinyLlama)")
        print("2. Search Offline Manuals (RAG)")
        print("0. Back to Main Menu")
        
        choice = input("\nSelect Option: ")
        
        if choice == '1':
            q = input("\nUser Query: ")
            resp = brain.generate_response(q)
            print(f"\n🤖 AI: {resp}")
            input("\nPress Enter...")
            
        elif choice == '2':
            q = input("\nSearch Manuals: ")
            res = rag.retrieve(q)
            print(f"\n📖 Found: {res}")
            input("\nPress Enter...")
            
        elif choice == '0':
            break

def menu_vision():
    while True:
        print_header("MODULE 3: COMPUTER VISION")
        print("1. Crop Doctor (Disease Detect from Photo)")
        print("2. Inventory Cam (Count Items in Photo)")
        print("3. Quality Grader (Grade Fruit in Photo)")
        print("0. Back to Main Menu")
        
        choice = input("\nSelect Option: ")
        
        if choice == '1':
            doc = mod_crop_doctor.CropDoctor()
            f = get_file_input(['.jpg', '.jpeg', '.png'])
            if f:
                diag, conf = doc.diagnose(f)
                print(f"\n🌿 Result: {diag} ({conf*100:.1f}%)")
            input("Press Enter...")

        elif choice == '2':
            cam = mod_inventory_cam.InventoryCam()
            f = get_file_input(['.jpg', '.jpeg', '.png'])
            if f:
                target = input("Target object (e.g. 'apple', 'all'): ")
                count = cam.count_stock(f, target_class=target)
                print(f"\n🔢 Counted: {count}")
            input("Press Enter...")

        elif choice == '3':
            grader = mod_quality_grader.QualityGrader()
            f = get_file_input(['.jpg', '.jpeg', '.png'])
            if f:
                res = grader.grade_fruit(f)
                print(f"\n🍎 Grade: {res}")
            input("Press Enter...")
            
        elif choice == '0':
            break

def menu_business():
    ledger = mod_khata_ledger.KhataLedger()
    scheduler = mod_rental_scheduler.RentalAgent()
    contractor = mod_contract_maker.ContractBot()
    barter = mod_barter_match.BarterBrain()

    while True:
        print_header("MODULE 4: BUSINESS & LOGISTICS")
        print("1. Generate Contract (PDF)")
        print("2. Khata Ledger (View Collections)")
        print("3. Rental Scheduler (Book Tractor)")
        print("4. Barter Matcher (Find Trades)")
        print("0. Back to Main Menu")
        
        choice = input("\nSelect Option: ")
        
        if choice == '1':
            print("Generating Sample Contract...")
            contractor.generate_sales_agreement("Raju", "Self", "Seeds", "10kg", "500")
            input("Press Enter...")
            
        elif choice == '2':
            print("Daily Collection List:")
            for task in ledger.get_collection_list():
                print(task)
            input("Press Enter...")
            
        elif choice == '3':
            date = input("Date (YYYY-MM-DD): ")
            slot = input("Slot (Morning/Evening): ")
            res = scheduler.book_slot(date, slot, "Self")
            print(res)
            input("Press Enter...")
            
        elif choice == '4':
            print("Finding Trades...")
            for m in barter.find_matches():
                print(m)
            input("Press Enter...")
            
        elif choice == '0':
            break

def menu_utility():
    maps = mod_offline_maps.OfflineNav()
    gov = mod_gov_schemes.SchemeFinder()
    weather = mod_weather_cache.WeatherGuard()

    while True:
        print_header("MODULE 5: UTILITY & INFRASTRUCTURE")
        print("1. Offline Maps (Directions)")
        print("2. Check Gov Schemes")
        print("3. Check Weather (Cached)")
        print("0. Back to Main Menu")
        
        choice = input("\nSelect Option: ")
        
        if choice == '1':
            print("Available: Home, Village_Square, Mandi_Market, Hospital")
            start = input("Start: ")
            end = input("End: ")
            print(maps.get_directions(start, end))
            input("Press Enter...")
            
        elif choice == '2':
            print("Checking profile for schemes...")
            # Using a dummy profile for the demo
            profile = {"occupation": "farmer", "gender": "female", "land_hectares": 1.0}
            for s in gov.find_eligible_schemes(profile):
                print(s)
            input("Press Enter...")
            
        elif choice == '3':
            print(weather.get_forecast())
            input("Press Enter...")
            
        elif choice == '0':
            break

# --- MAIN LOOP ---

def main():
    while True:
        print_header("HOME MENU")
        print("1. [Diagnostics]  Voice, QR, Machinery Repair")
        print("2. [Intelligence] AI Assistant, Offline Manuals")
        print("3. [Vision]       Crop Doctor, Inventory, Quality")
        print("4. [Business]     Contracts, Ledger, Scheduler")
        print("5. [Utility]      Maps, Schemes, Weather")
        print("Q. Quit Gram-OS")
        
        choice = input("\nSelect Module (1-5): ").upper()
        
        if choice == '1':
            menu_diagnostics()
        elif choice == '2':
            menu_intelligence()
        elif choice == '3':
            menu_vision()
        elif choice == '4':
            menu_business()
        elif choice == '5':
            menu_utility()
        elif choice == 'Q':
            print("\nShutting down Gram-OS...")
            break
        else:
            print("Invalid selection.")
            time.sleep(1)

if __name__ == "__main__":
    main()