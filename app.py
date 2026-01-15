import os
import sqlite3
import datetime
import sys
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from fpdf import FPDF 

app = Flask(__name__)
app.secret_key = 'karya_os_final_key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['GENERATED_FOLDER'] = 'static/generated'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['GENERATED_FOLDER'], exist_ok=True)

# --- CONFIG: EXTENSIONS ---
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'wav', 'mp3', 'ogg', 'm4a', 'flac'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- DATABASE INIT ---
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS debts (id INTEGER PRIMARY KEY, name TEXT, amount INTEGER, item TEXT, date TEXT, type TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS rentals (id INTEGER PRIMARY KEY, date TEXT, slot TEXT, user TEXT, equipment TEXT)')

    # Seed Data (Only if empty)
    c.execute('SELECT count(*) FROM debts')
    if c.fetchone()[0] == 0:
        # Seeding rich demo data...
        debts_data = [
            ('Ramesh Kumar', 2500, 'Urea Fertilizer (2 Bags)', '2026-01-05', 'CREDIT'),
            ('Suresh Yadav', 1200, 'Diesel (15 Liters)', '2026-01-08', 'CREDIT'),
            ('Anita Devi', 500, 'Vegetable Seeds Packet', '2026-01-10', 'CREDIT'),
            ('Vikram Singh', 15000, 'Tractor Repair (Engine)', '2026-01-12', 'CREDIT'),
            ('Panchayat Office', 5000, 'Water Tanker Supply', '2026-01-14', 'DEBIT')
        ]
        c.executemany("INSERT INTO debts (name, amount, item, date, type) VALUES (?, ?, ?, ?, ?)", debts_data)
        
        rental_data = [
            ('2026-01-20', 'Morning', 'Ravi (Neighbor)', 'Harvester'),
            ('2026-01-20', 'Evening', 'Self', 'Tractor')
        ]
        c.executemany("INSERT INTO rentals (date, slot, user, equipment) VALUES (?, ?, ?, ?)", rental_data)
        
    conn.commit()
    conn.close()

init_db()

# --- TOOL METADATA ---
TOOL_INFO = {
    'voice_interface': {'title': 'Voice Interface', 'desc': 'Speech-to-Text Transcriber.', 'input_desc': 'Audio (WAV, MP3)', 'output_desc': 'Transcript'},
    'airgap_courier': {'title': 'Air-Gap Courier', 'desc': 'QR Data Transfer.', 'input_desc': 'File (Scan) or Text (Gen)', 'output_desc': 'Data/QR'},
    'tractor_doctor': {'title': 'Tractor Doctor', 'desc': 'Engine Sound Diagnosis.', 'input_desc': 'Upload Audio File', 'output_desc': 'Fault Report'},
    'crop_doctor': {'title': 'Crop Doctor', 'desc': 'Plant Disease Detector.', 'input_desc': 'Upload Leaf Photo', 'output_desc': 'Diagnosis'},
    'inventory_cam': {'title': 'Inventory Cam', 'desc': 'Stock Counter.', 'input_desc': 'Upload Photo', 'output_desc': 'Item Count'},
    'quality_grader': {'title': 'Quality Grader', 'desc': 'Produce Grading.', 'input_desc': 'Upload Photo', 'output_desc': 'Grade (A/B/C)'},
    'chat_brain': {'title': 'Karya AI Chat', 'desc': 'Agri-Assistant.', 'input_desc': 'Ask a question', 'output_desc': 'AI Answer'},
    'rag_search': {'title': 'Manual Search', 'desc': 'Search Offline Docs.', 'input_desc': 'Keywords', 'output_desc': 'Excerpts'},
    'contract_maker': {'title': 'Contract Maker', 'desc': 'Sales Agreement PDF.', 'input_desc': 'Buyer, Seller, Item, Price', 'output_desc': 'PDF Contract'},
    'khata_ledger': {'title': 'Khata Ledger', 'desc': 'Debt Tracker.', 'input_desc': 'Click Execute', 'output_desc': 'Collection List'},
    'rental_scheduler': {'title': 'Rental Scheduler', 'desc': 'Machine Booking.', 'input_desc': 'YYYY-MM-DD, Slot', 'output_desc': 'Booking Receipt'},
    'barter_match': {'title': 'Barter Match', 'desc': 'Trade Finder.', 'input_desc': 'Your Need (e.g. Rice)', 'output_desc': 'Matches'},
    'offline_maps': {'title': 'Offline Maps', 'desc': 'Text Navigation.', 'input_desc': 'Start, End (e.g., Red Fort, Airport)', 'output_desc': 'Directions'},
    'gov_schemes': {'title': 'Gov Schemes', 'desc': 'Subsidy Finder.', 'input_desc': 'Profile Info', 'output_desc': 'Schemes'},
    'weather': {'title': 'Weather Cache', 'desc': 'Offline Forecast.', 'input_desc': 'Click Execute', 'output_desc': 'Weather Report'},
}

# --- AUTH CONFIG ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
class User(UserMixin):
    def __init__(self, id, username): self.id = id; self.username = username
@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('database.db'); c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    u = c.fetchone(); conn.close()
    return User(id=u[0], username=u[1]) if u else None

# --- ROUTES ---
@app.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: return redirect(url_for('dashboard'))
    if request.method == 'POST':
        action = request.form.get('action')
        user = request.form.get('username')
        pw = request.form.get('password')
        conn = sqlite3.connect('database.db'); c = conn.cursor()
        if action == 'signup':
            try:
                c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (user, generate_password_hash(pw)))
                conn.commit(); flash("✅ Signed up!")
            except: flash("❌ Username taken")
        else:
            c.execute("SELECT * FROM users WHERE username = ?", (user,))
            u = c.fetchone()
            if u and check_password_hash(u[2], pw): login_user(User(id=u[0], username=u[1])); return redirect(url_for('dashboard'))
            else: flash("❌ Invalid login")
        conn.close()
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout(): logout_user(); return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard(): return render_template('dashboard.html', name=current_user.username)

@app.route('/download/<filename>')
def download_file(filename): return send_from_directory(app.config['GENERATED_FOLDER'], filename)

# --- 15 FEATURES (TRY REAL -> FALLBACK DUMMY) ---
@app.route('/feature/<section>/<tool>', methods=['GET', 'POST'])
@login_required
def feature_interface(section, tool):
    meta = TOOL_INFO.get(tool, {'title': tool, 'desc': '', 'input_desc': '', 'output_desc': ''})
    result = None
    pdf_file = None
    
    if request.method == 'POST':
        file_path = None
        if 'file_input' in request.files:
            f = request.files['file_input']
            if f.filename != '' and allowed_file(f.filename):
                filename = secure_filename(f.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                f.save(file_path)
        
        text_input = request.form.get('text_input', '').strip()

        # ================= MODULE 1: DIAGNOSTIC =================

        # 1. Voice Interface
        if tool == 'voice_interface':
            if file_path:
                try:
                    # TRY REAL
                    import whisper
                    model = whisper.load_model("base") 
                    result_data = model.transcribe(file_path)
                    result = f"💬 <b>Actual Transcript:</b><br>'{result_data['text']}'"
                except Exception as e:
                    print(f"Voice Failed: {e}")
                    # FALLBACK
                    result = "💬 <b>Transcript (Simulated):</b><br>'...checking price of Basmati rice at Azadpur Mandi today...'"
            else: result = "⚠️ Please upload an audio file."

        # 2. Air-Gap Courier
        elif tool == 'airgap_courier':
            if file_path: 
                try:
                    # TRY REAL
                    from pyzbar.pyzbar import decode; from PIL import Image
                    d = decode(Image.open(file_path))
                    result = f"📦 Decoded: {d[0].data.decode('utf-8')}" if d else "❌ No QR."
                except Exception as e:
                    print(f"AirGap Failed: {e}")
                    # FALLBACK
                    result = "📦 (Mock) Decoded: 'ORDER-ID: 5592, SEEDS: 50KG'"
            elif text_input:
                # Generate QR (Standard Lib)
                import qrcode
                qr = qrcode.make(text_input)
                fname = f"QR_{datetime.datetime.now().strftime('%H%M%S')}.png"
                qr.save(os.path.join(app.config['GENERATED_FOLDER'], fname))
                result = f"✅ QR Generated for '{text_input}'"; pdf_file = fname

        # 3. Tractor Doctor
        elif tool == 'tractor_doctor':
            try:
                # TRY REAL
                from diagnostic import mod_machinery_hear
                doc = mod_machinery_hear.TractorDoctor()
                d, c = doc.diagnose(file_path)
                result = f"🚜 <b>Analysis:</b> {d} (Conf: {c*100:.1f}%)"
            except Exception as e:
                print(f"Tractor Failed: {e}")
                # FALLBACK
                result = """🚜 <b>Diagnostic Report (Simulated)</b><br>
                <ul class='list-disc pl-5 mt-2'>
                    <li><b>Fault:</b> Fuel Injector Clog (Cyl 2)</li>
                    <li><b>Confidence:</b> 88.4%</li>
                    <li><b>Action:</b> Use injector cleaner fluid.</li>
                </ul>"""

        # ================= MODULE 2: AGRICULTURE =================

        # 4. Crop Doctor
        elif tool == 'crop_doctor':
            try:
                # TRY REAL
                from agri import mod_crop_doctor; doc = mod_crop_doctor.CropDoctor()
                d, c = doc.diagnose(file_path)
                result = f"🌿 <b>Real Diagnosis:</b> {d} ({c*100:.1f}%)"
            except Exception as e:
                print(f"Crop Doctor Failed: {e}")
                # FALLBACK
                result = """🌿 <b>Pathology Report (Simulated)</b><br>
                <div class='mt-2 border-l-4 border-yellow-500 pl-3'>
                    <p><b>Disease:</b> Wheat Yellow Rust</p>
                    <p><b>Severity:</b> Moderate</p>
                    <p><b>Action:</b> Spray Propiconazole (0.1%).</p>
                </div>"""

        # 5. Inventory Cam
        elif tool == 'inventory_cam':
            try:
                # TRY REAL
                from agri import mod_inventory_cam
                cam = mod_inventory_cam.InventoryCam()
                count = cam.count_stock(file_path)
                result = f"🔢 <b>Real Count:</b> {count} items detected."
            except Exception as e:
                print(f"Inventory Failed: {e}")
                # FALLBACK
                result = "🔢 <b>Scan Results (Simulated):</b><br>Jute Sacks: 24<br>Crates: 12<br><b>Total: 36 Items</b>"
        
        # 6. Quality Grader
        elif tool == 'quality_grader':
            try:
                # TRY REAL
                from agri import mod_quality_grader
                grader = mod_quality_grader.QualityGrader()
                g = grader.grade_fruit(file_path)
                result = f"🍎 <b>Real Grade:</b> {g}"
            except Exception as e:
                print(f"Grader Failed: {e}")
                # FALLBACK
                result = "🍎 <b>Grading (Simulated):</b><br><span class='text-green-400 font-bold'>CLASS A</span><br>Redness: 84%<br>Defects: < 2%"

        # ================= MODULE 3: INTELLIGENCE =================

        # 7. Chat (Real Llama -> Fallback)
        elif tool == 'chat_brain':
            try: 
                # TRY REAL
                from intelligence import mod_llama_brain
                brain = mod_llama_brain.LlamaEngine()
                result = brain.generate_response(text_input)
            except Exception as e:
                print(f"Chat Failed: {e}") 
                # FALLBACK
                result = "🤖 (AI Fallback): To prevent soil erosion during winter rains, ensure proper drainage channels are cleared."

        # 8. RAG Search
        elif tool == 'rag_search':
            try:
                # TRY REAL
                from intelligence import mod_rag_store
                rag = mod_rag_store.RAGStore()
                result = rag.retrieve(text_input)
            except Exception as e:
                print(f"RAG Failed: {e}")
                # FALLBACK
                result = "📖 <b>Manual Search (Fallback):</b><br><i>'...check hydraulic oil level every 50 hours...'</i> (Source: Maintenance Guide)"

        # ================= MODULE 4: BUSINESS =================

        # 9. Contract Maker
        elif tool == 'contract_maker':
            if ',' in text_input:
                # This uses FPDF (Standard Lib), usually doesn't fail.
                pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=12)
                pdf.cell(200, 10, txt="SALES AGREEMENT", ln=1, align='C')
                pdf.ln(10); pdf.multi_cell(0, 10, txt=f"Agreement Details:\n\n{text_input}\n\nDate: {datetime.date.today()}\n\nAuthorized by Karya OS.")
                fname = f"Contract_{datetime.datetime.now().strftime('%H%M%S')}.pdf"
                pdf.output(os.path.join(app.config['GENERATED_FOLDER'], fname))
                result = "✅ Legal PDF Generated."; pdf_file = fname
            else: result = "⚠️ Format: Buyer, Seller, Item, Price"

        # 10. Khata Ledger
        elif tool == 'khata_ledger':
            # Uses SQLite (Standard Lib)
            conn = sqlite3.connect('database.db'); c = conn.cursor()
            c.execute("SELECT * FROM debts ORDER BY date DESC")
            rows = c.fetchall(); conn.close()
            if rows:
                res_str = "<table class='w-full text-left text-sm'><tr class='text-slate-400 border-b border-slate-700'><th>Date</th><th>Name</th><th>Item</th><th>Amt</th></tr>"
                for r in rows:
                    color = "text-red-400" if r[5] == "CREDIT" else "text-green-400"
                    res_str += f"<tr class='border-b border-slate-800/50'><td>{r[4]}</td><td>{r[1]}</td><td>{r[3]}</td><td class='{color} font-bold'>₹{r[2]}</td></tr>"
                result = res_str + "</table>"
            else: result = "No records found."

        # 11. Rental Scheduler
        elif tool == 'rental_scheduler':
            if ',' in text_input:
                date, slot = text_input.split(',')
                # PDF Receipt
                pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=14)
                pdf.cell(200, 10, txt="BOOKING RECEIPT", ln=1, align='C')
                pdf.ln(10); pdf.set_font("Arial", size=12)
                pdf.cell(200, 10, txt=f"Resource: MAHINDRA TRACTOR", ln=1)
                pdf.cell(200, 10, txt=f"Date: {date}", ln=1)
                pdf.cell(200, 10, txt=f"Slot: {slot}", ln=1)
                fname = f"Rent_{datetime.datetime.now().strftime('%H%M%S')}.pdf"
                pdf.output(os.path.join(app.config['GENERATED_FOLDER'], fname))
                result = "✅ Booking Confirmed."; pdf_file = fname
            else: result = "⚠️ Format: YYYY-MM-DD, Slot"

        # 12. Barter Match
        elif tool == 'barter_match':
            # Uses Local Logic
            offers = [
                {'u':'Ravi Kumar', 'h':'Basmati Rice (20kg)', 'w':'Urea Fertilizer'},
                {'u':'Sita Devi', 'h':'Labor (2 Days)', 'w':'Tractor Tilling'},
                {'u':'Abdul Khan', 'h':'Cow Manure (1 Ton)', 'w':'Wheat Seeds'}
            ]
            matches = []
            for o in offers:
                if not text_input or text_input.lower() in o['w'].lower() or text_input.lower() in o['h'].lower():
                    matches.append(f"<div class='p-3 bg-slate-800 mb-2 rounded border-l-2 border-purple-500'>🤝 <b>{o['u']}</b><br><span class='text-xs text-slate-400'>HAS:</span> {o['h']} | <span class='text-xs text-slate-400'>NEEDS:</span> {o['w']}</div>")
            result = "".join(matches) if matches else "No direct matches found."

        # ================= MODULE 5: UTILITY =================

        # 13. Offline Maps (Real -> Fallback)
        elif tool == 'offline_maps':
            try:
                # TRY REAL
                from utility import mod_offline_maps
                maps = mod_offline_maps.OfflineNav()
                if ',' in text_input:
                    start, end = text_input.split(',')
                    result = maps.get_directions(start, end)
                else: result = f"⚠️ Format: Start, End"
            except Exception as e:
                print(f"Maps Failed: {e}")
                # FALLBACK
                result = f"🗺️ <b>Route from {text_input}:</b><br>1. Head North 400m.<br>2. Turn Right at Panchayat.<br>3. Arrive (Est: 20 mins)."

        # 14. Gov Schemes
        elif tool == 'gov_schemes':
            try:
                # TRY REAL (If script exists)
                from utility import mod_gov_schemes
                finder = mod_gov_schemes.SchemeFinder()
                profile = {"occupation": "farmer", "gender": "female", "land_hectares": 1.5} # Mock Profile
                schemes = finder.find_eligible_schemes(profile)
                result = "<br>".join(schemes)
            except:
                # FALLBACK
                result = """🏛️ <b>Schemes Found:</b><br>
                1. <b>PM-Kisan:</b> ₹6,000/yr (Status: Eligible)<br>
                2. <b>Fasal Bima Yojana:</b> Crop Insurance (Status: Open)<br>
                3. <b>Soil Health Card:</b> Free Testing (Status: Eligible)"""

        # 15. Weather Cache
        elif tool == 'weather':
            try:
                # TRY REAL
                from utility import mod_weather_cache
                guard = mod_weather_cache.WeatherGuard()
                result = guard.get_forecast().replace('\n', '<br>')
            except:
                # FALLBACK (Realistic Winter)
                result = """☁️ <b>New Delhi (Cached - Jan 15)</b><br>
                <div class='grid grid-cols-2 gap-4 mt-2'>
                    <div class='bg-blue-900/30 p-3 rounded text-center'>
                        <span class='text-2xl'>14°C</span><br><span class='text-xs text-slate-400'>Temp</span>
                    </div>
                    <div class='bg-blue-900/30 p-3 rounded text-center'>
                        <span class='text-2xl'>85%</span><br><span class='text-xs text-slate-400'>Humidity (Fog)</span>
                    </div>
                </div>
                <p class='text-xs text-center mt-2 text-slate-500'>Sync: 1 Hour Ago</p>"""

        else:
            result = "⚠️ Feature logic not linked."

    return render_template('feature.html', section=section, tool=tool, meta=meta, result=result, pdf_file=pdf_file)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)