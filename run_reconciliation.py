import os
import pandas as pd
from reconcile_trades import TradeReconciliation
from extract_trades import extract_broker_files  # Removed load_client_orders
from report_generation import calculate_costs, generate_matched_trades_report, generate_broker_summary

def automate_trade_reconciliation():
    # Define directories for data and output
    data_dir = r'C:\Users\Sankalp\Desktop\trade_reconciliation\data'  # Directory containing trade files
    output_dir = r'C:\Users\Sankalp\Desktop\trade_reconciliation\Reports'  # Directory to save reports
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Step 1: Load broker trades
    print("Loading broker trades from email files...")
    email_paths = [
        os.path.join(data_dir, 'Trade File BROKER 1 - 31_01_2025.eml'),
        os.path.join(data_dir, 'Trade File BROKER 2 - 31_01_2025.eml'),
        os.path.join(data_dir, 'Trade File BROKER 3 - 31_01_2025.eml')
    ]
    broker_trades = extract_broker_files(email_paths)
    if not broker_trades:
        print("No broker trades found. Exiting reconciliation.")
        return
    
    # Combine all broker trades into a single DataFrame
    combined_broker_trades = pd.concat(broker_trades)
    
    # Step 2: Calculate costs for broker trades
    print("Calculating costs for broker trades...")
    combined_broker_trades = calculate_costs(combined_broker_trades)
    
    # Step 3: Generate reports
    print("Generating reports...")
    
    # Generate matched trades report
    generate_matched_trades_report(combined_broker_trades, output_dir)
    
    # Generate broker summary report
    generate_broker_summary(combined_broker_trades, output_dir)
    
    print("\nAll reports generated successfully!")

if __name__ == "__main__":
    automate_trade_reconciliation()
