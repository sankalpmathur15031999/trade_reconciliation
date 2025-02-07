import pandas as pd
from datetime import datetime
import email
import os
from email import policy
from email.parser import BytesParser
from io import BytesIO  # Import BytesIO for handling byte streams

def identify_file_type(filename, df):
    """
    Identify if the Excel file is client orders or broker trades
    based on filename and/or content.
    """
    filename_lower = filename.lower()
    print(f"Identifying file type for: {filename}")

    # Check if the filename indicates client orders
    if 'client' in filename_lower or 'order' in filename_lower:
        print("Identified as client orders based on filename.")
        return 'client_orders'
    
    # Check if the filename indicates broker trades
    elif 'broker' in filename_lower or 'trade' in filename_lower:
        print("Identified as broker trades based on filename.")
        return 'broker_trades'
    
    # If filename is not conclusive, try to identify by columns
    columns = set(df.columns.str.lower())
    print(f"Columns found: {columns}")

    # Check for specific identifiers for broker trades
    if 'buy/sell flag' in columns and 'qty' in columns:
        print("Identified as broker trades based on column names.")
        return 'broker_trades'
    
    # Default to broker trades if we can't determine
    print("Defaulting to broker trades.")
    return 'broker_trades'

def extract_excel_from_email(email_path):
    """
    Extract all Excel attachments from a single email file.
    Returns tuple of (client_orders, broker_trades).
    """
    client_orders = []
    broker_trades = []
    
    try:
        print(f"\nProcessing email file: {email_path}")
        if not os.path.exists(email_path):
            print(f"File not found: {email_path}")
            return None, None
            
        with open(email_path, 'rb') as f:
            msg = BytesParser(policy=policy.default).parse(f)
            
            # Process each attachment in the email
            for part in msg.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get('Content-Disposition') is None:
                    continue
                    
                filename = part.get_filename()
                if filename and filename.lower().endswith(('.xlsx', '.xls')):
                    print(f"Found Excel attachment: {filename}")
                    # Extract the Excel file content
                    excel_data = part.get_payload(decode=True)
                    # Read into DataFrame using BytesIO
                    df = pd.read_excel(BytesIO(excel_data))
                    print(f"Loaded file with columns: {df.columns.tolist()}")
                    
                    # Identify file type
                    file_type = identify_file_type(filename, df)
                    if file_type == 'client_orders':
                        client_orders.append(df)
                        print("Client orders appended.")
                    else:
                        broker_trades.append(df)
                        print("Broker trades appended.")
        
        return client_orders, broker_trades
        
    except Exception as e:
        print(f"Error processing email file: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return None, None

def load_client_orders():
    """Load client orders from email attachments."""
    all_client_orders = []
    email_paths = [
        r'C:\Users\Sankalp\Desktop\trade_reconciliation\data\Trade File BROKER 1 - 31_01_2025.eml',
        r'C:\Users\Sankalp\Desktop\trade_reconciliation\data\Trade File BROKER 2 - 31_01_2025.eml',
        r'C:\Users\Sankalp\Desktop\trade_reconciliation\data\Trade File BROKER 3 - 31_01_2025.eml'
    ]
    
    for path in email_paths:
        client_orders, _ = extract_excel_from_email(path)
        if client_orders:
            all_client_orders.extend(client_orders)
            print(f"Loaded {len(client_orders)} client orders from {path}.")
        else:
            print(f"No client orders found in {path}.")
    
    if all_client_orders:
        return pd.concat(all_client_orders, ignore_index=True)
    
    print("No client orders found after processing all emails.")
    return None

def extract_broker_files(email_paths):
    """Extract broker trade data from email attachments."""
    all_broker_trades = []
    
    for path in email_paths:
        _, broker_trades = extract_excel_from_email(path)
        if broker_trades:
            all_broker_trades.extend(broker_trades)
    
    return all_broker_trades

if __name__ == "__main__":
    # Test the functions
    print("Testing data extraction...")
    
    email_paths = [
        r'C:\Users\Sankalp\Desktop\trade_reconciliation\data\Trade File BROKER 1 - 31_01_2025.eml',
        r'C:\Users\Sankalp\Desktop\trade_reconciliation\data\Trade File BROKER 2 - 31_01_2025.eml',
        r'C:\Users\Sankalp\Desktop\trade_reconciliation\data\Trade File BROKER 3 - 31_01_2025.eml'
    ]
    
    print("\nLoading client orders...")
    client_orders = load_client_orders()
    
    if client_orders is not None:
        print("Client orders loaded successfully:")
        print(client_orders.head())
    else:
        print("No client orders found.")
    
    print("\nLoading broker trades...")
    broker_trades = extract_broker_files(email_paths)
    
    if broker_trades:
        print(f"Successfully loaded {len(broker_trades)} broker trade files.")
        for i, df in enumerate(broker_trades, 1):
            print(f"\nBroker {i} trades preview:")
            print(df.head())
    else:
        print("No broker trades found.")
