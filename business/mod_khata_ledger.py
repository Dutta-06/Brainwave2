import sqlite3
from datetime import datetime, timedelta

class KhataLedger:
    def __init__(self, db_name="village_khata.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS debts (
                id INTEGER PRIMARY KEY,
                customer_name TEXT,
                amount REAL,
                item TEXT,
                date_added TEXT,
                due_date TEXT,
                status TEXT
            )
        ''')
        self.conn.commit()

    def add_entry(self, name, amount, item, days_credit=7):
        """Records a new debt (Udhaar)."""
        date_added = datetime.now().strftime("%Y-%m-%d")
        due_date = (datetime.now() + timedelta(days=days_credit)).strftime("%Y-%m-%d")
        
        self.cursor.execute('''
            INSERT INTO debts (customer_name, amount, item, date_added, due_date, status)
            VALUES (?, ?, ?, ?, ?, 'PENDING')
        ''', (name, amount, item, date_added, due_date))
        self.conn.commit()
        print(f"[Ledger] Added credit: {name} owes {amount} for {item}.")

    def get_collection_list(self):
        """
        Agentic Feature: Tells user who to visit TODAY.
        """
        today = datetime.now().strftime("%Y-%m-%d")
        # Find debts that are due today or overdue
        self.cursor.execute('''
            SELECT customer_name, amount, item FROM debts 
            WHERE status='PENDING' AND due_date <= ?
        ''', (today,))
        
        results = self.cursor.fetchall()
        
        if not results:
            return ["No collections due today. Enjoy your day!"]
        
        report = []
        for row in results:
            report.append(f"COLLECT: Rs {row[1]} from {row[0]} ({row[2]})")
        
        return report

# --- Test Block ---
if __name__ == "__main__":
    ledger = KhataLedger()
    # 1. Add some mock debts
    ledger.add_entry("Ravi", 500, "Fertilizer", days_credit=0) # Due today
    ledger.add_entry("Sita", 1200, "Pesticide", days_credit=10) # Due later
    
    # 2. Generate Agentic Report
    daily_tasks = ledger.get_collection_list()
    print("\n--- DAILY AGENT REPORT ---")
    for task in daily_tasks:
        print(task)