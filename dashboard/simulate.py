import os
import sys
import time
import random
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from dashboard.services import evaluate_transaction

# Expanded account pool to reduce collision frequency
ACCOUNTS = [f'ACC_{i}' for i in range(1001, 1020)]
LOCATIONS = ['Uganda', 'Kenya', 'United States', 'United Kingdom', 'Nigeria']

def start_simulation():
    print(" Starting Cleaned Real-Time Transaction Stream...")
    print("Press Ctrl + C to stop at any time.\n")
    
    count = 0
    while True:
        count += 1
        account = random.choice(ACCOUNTS)
        
        # 90% chance of normal transaction
        if random.random() < 0.90:
            amount = round(random.uniform(10.0, 450.0), 2)
            location = "Uganda"
        else:
            # 10% chance of high amount fraud
            amount = round(random.uniform(11000.0, 50000.0), 2)
            location = random.choice(LOCATIONS)

        # Trigger a deliberate rapid attack only every 15th cycle
        if count % 15 == 0:
            target_account = "ACC_ATTACKER"
            print(f"\n⚡ Simulating Rapid Velocity Attack on {target_account}...")
            for _ in range(6):
                tx = evaluate_transaction(target_account, round(random.uniform(20.0, 100.0), 2), "Uganda")
                print(f" -> TX #{tx.id} | Amount: ${tx.amount} | Flagged: {tx.is_suspicious}")
                time.sleep(0.2)
            continue

        tx = evaluate_transaction(account, amount, location)
        status = " FLAGGED" if tx.is_suspicious else " APPROVED"
        print(f"[{status}] Acc: {account} | Amount: ${amount:<8} | Location: {location}")
        
        # Pause 3 seconds between normal transactions
        time.sleep(3)

if __name__ == '__main__':
    try:
        start_simulation()
    except KeyboardInterrupt:
        print("\n Simulation stopped.")