import pandas as pd
from datetime import datetime
from extract_trades import extract_broker_files
import os

def calculate_costs(broker_trades_df):
    """Calculate costs for each trade and return updated DataFrame."""
    try:
        # Calculate total cost as sum of Brokerage Amount and STT
        broker_trades_df['Total Cost'] = broker_trades_df['Brokerage Amount'] + broker_trades_df['STT']
        return broker_trades_df
    except Exception as e:
        print(f"Error calculating costs: {str(e)}")
        return broker_trades_df  # Return original DataFrame in case of error

def generate_matched_trades_report(broker_trades_df, output_dir):
    """Generate detailed report of matched broker trades."""
    if broker_trades_df is None or broker_trades_df.empty:
        print("No broker trades data available.")
        return False
    
    try:
        # Add timestamp to each record
        broker_trades_df['generated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Save to CSV
        output_path = os.path.join(output_dir, 'matched_trades.csv')
        broker_trades_df.to_csv(output_path, index=False)
        print(f"Generated matched trades report: {output_path}")
        
        return True
    except Exception as e:
        print(f"Error generating matched trades report: {str(e)}")
        return False

def generate_unmatched_trades_report(broker_trades_df, output_dir):
    """Generate report of unmatched broker trades."""
    if broker_trades_df is None or broker_trades_df.empty:
        print("No broker trades data available.")
        return False

    try:
        # Print columns to check if 'trade_id' exists
        print("Columns in broker trades:", broker_trades_df.columns)
        
        # Assuming unmatched trades are those with a missing 'trade_id' or an empty 'match_status'
        # Option 1: Filter based on 'trade_id' being null
        unmatched_trades_df = broker_trades_df[broker_trades_df['trade_id'].isnull()]
        
        # Option 2: Alternatively, filter by match status
        # unmatched_trades_df = broker_trades_df[broker_trades_df['match_status'] == 'unmatched']

        if unmatched_trades_df.empty:
            print("No unmatched trades found.")
            return False
        
        # Add timestamp to each record for report tracking
        unmatched_trades_df['generated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Save the unmatched trades to a CSV file
        output_path = os.path.join(output_dir, 'unmatched_trades.csv')
        unmatched_trades_df.to_csv(output_path, index=False)
        print(f"Generated unmatched trades report: {output_path}")

        return True
    except Exception as e:
        print(f"Error generating unmatched trades report: {str(e)}")
        return False


def generate_broker_summary(broker_trades_df, output_dir):
    """Generate summary report by broker."""
    try:
        # Create broker summary
        summary = []
        
        # Get unique brokers from broker trades DataFrame
        brokers = broker_trades_df['party code/SEBI regn code of party'].unique()
        
        for broker in brokers:
            broker_data = broker_trades_df[broker_trades_df['party code/SEBI regn code of party'] == broker]
            total_quantity = broker_data['QTY'].sum()
            total_brokerage_cost = broker_data['Brokerage Amount'].sum()
            total_stt = broker_data['STT'].sum()
            total_cost = broker_data['Total Cost'].sum()  # Use calculated total cost
            
            summary.append({
                'broker_id': broker,
                'total_trades': len(broker_data),
                'total_quantity': total_quantity,
                'total_brokerage_cost': total_brokerage_cost,
                'total_stt': total_stt,
                'total_cost': total_cost,
            })
        
        # Create summary DataFrame
        summary_df = pd.DataFrame(summary)
        
        # Add timestamp
        summary_df['generated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Save to CSV
        output_path = os.path.join(output_dir, 'broker_summary.csv')
        summary_df.to_csv(output_path, index=False)
        print(f"Generated broker summary report: {output_path}")
        
        return True
    except Exception as e:
        print(f"Error generating broker summary report: {str(e)}")
        return False

def main():
    try:
        # Define the output directory for reports
        output_dir = r'C:\Users\Sankalp\Desktop\trade_reconciliation\Reports'
        
        # Create reports directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Load data from email attachments for broker trades
        print("Loading broker trades...")
        
        email_paths = [
            r'C:\Users\Sankalp\Desktop\trade_reconciliation\data\Trade File BROKER 1 - 31_01_2025.eml',
            r'C:\Users\Sankalp\Desktop\trade_reconciliation\data\Trade File BROKER 2 - 31_01_2025.eml',
            r'C:\Users\Sankalp\Desktop\trade_reconciliation\data\Trade File BROKER 3 - 31_01_2025.eml'
        ]
        
        # Extract broker trades from emails
        broker_trades = extract_broker_files(email_paths)

        if not broker_trades:
            print("No broker trades found. Exiting report generation.")
            return
        
        combined_broker_trades = pd.concat(broker_trades)

        # Calculate costs for each trade
        combined_broker_trades = calculate_costs(combined_broker_trades)

        # Generate reports directly from the loaded data 
        print("\nGenerating reports...")

        # Generate matched trades report
        generate_matched_trades_report(combined_broker_trades, output_dir)

        # Generate unmatched trades report
        generate_unmatched_trades_report(combined_broker_trades, output_dir)

        # Generate broker summary report
        generate_broker_summary(combined_broker_trades, output_dir)

        print("\nAll reports generated successfully!")
       
    except Exception as e:
        print(f"Error in report generation: {str(e)}")

if __name__ == "__main__":
    main()
