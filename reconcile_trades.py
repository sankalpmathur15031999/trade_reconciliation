import pandas as pd
import sqlite3
from datetime import datetime
from extract_trades import load_client_orders, extract_broker_files

class TradeReconciliation:
    def __init__(self, client_orders, broker_trades):
        self.client_orders = client_orders
        self.broker_trades = broker_trades
        self.matched_trades = []
        self.unmatched_trades = []
        self.excess_trades = []

    def reconcile(self):
        """Main reconciliation function."""
        for _, order in self.client_orders.iterrows():
            matches = self._find_matching_trades(order)
            
            if matches.empty:
                # No matches found - mark as pending
                self._mark_as_pending(order)
            else:
                # Process matches based on quantity
                self._process_matches(order, matches)

    def _find_matching_trades(self, order):
        """Find potential matching trades based on basic criteria."""
        matches = self.broker_trades[
            (self.broker_trades['Ticker'] == order['Ticker']) &
            (self.broker_trades['Direction'] == order['Direction']) &
            (self.broker_trades['Date'] == order['Date'])  # Assuming Date is a column
        ]
        return matches

    def _process_matches(self, order, matching_trades):
        """Process matching trades based on quantity logic."""
        order_quantity = order['Quantity']
        total_matched = 0

        for _, trade in matching_trades.iterrows():
            if total_matched >= order_quantity:
                break

            trade_quantity = trade['Quantity']
            
            if trade_quantity + total_matched <= order_quantity:
                # Full match or partial match
                self.matched_trades.append({
                    'order_id': order['UCC'],
                    'trade_id': trade['UCC'],
                    'symbol': trade['Ticker'],
                    'matched_quantity': trade_quantity,
                    'status': 'MATCHED' if trade_quantity == order_quantity else 'PARTIAL',
                    'brokerage_cost': trade['Brokerage Amount'],
                    'stt': trade['STT'],
                    'total_cost': trade['Brokerage Amount'] + trade['STT'],
                    'execution_slippage': trade['Net Amount'] / trade_quantity if trade_quantity > 0 else 0
                })
                total_matched += trade_quantity
            else:
                # Excess quantity
                remaining_needed = order_quantity - total_matched
                self.excess_trades.append({
                    'order_id': order['UCC'],
                    'trade_id': trade['UCC'],
                    'symbol': trade['Ticker'],
                    'matched_quantity': remaining_needed,
                    'status': 'EXCESS',
                    'brokerage_cost': trade['Brokerage Amount'],
                    'stt': trade['STT'],
                    'total_cost': trade['Brokerage Amount'] + trade['STT'],
                    'execution_slippage': trade['Net Amount'] / remaining_needed if remaining_needed > 0 else 0
                })
                total_matched += remaining_needed

    def _mark_as_pending(self, order):
        """Mark unmatched orders as pending."""
        self.unmatched_trades.append({
            'order_id': order['UCC'],
            'symbol': order['Ticker'],
            'quantity': order['Quantity'],
            'status': 'PENDING'
        })

    def get_results(self):
        """Return reconciliation results."""
        return {
            'matched': pd.DataFrame(self.matched_trades),
            'unmatched': pd.DataFrame(self.unmatched_trades),
            'excess': pd.DataFrame(self.excess_trades)
        }

    def save_to_database(self, db_name='trades.db'):
        """Store data in SQLite database."""
        conn = sqlite3.connect(db_name)
        
        # Create tables if they do not exist
        conn.execute('''
            CREATE TABLE IF NOT EXISTS client_orders (
                UCC TEXT,
                Ticker TEXT,
                Quantity INTEGER,
                Direction TEXT,
                Date TEXT
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS broker_trades (
                UCC TEXT,
                Ticker TEXT,
                Quantity INTEGER,
                Direction TEXT,
                Date TEXT,
                Brokerage_Amount REAL,
                STT REAL,
                Net_Amount REAL
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS reconciliation_results (
                order_id TEXT,
                trade_id TEXT,
                symbol TEXT,
                matched_quantity INTEGER,
                status TEXT,
                brokerage_cost REAL,
                stt REAL,
                total_cost REAL,
                execution_slippage REAL
            )
        ''')
        
        # Insert client orders into the database
        if not self.client_orders.empty:
            self.client_orders.to_sql('client_orders', conn, if_exists='append', index=False)

        # Insert broker trades into the database
        if not self.broker_trades.empty:
            self.broker_trades.to_sql('broker_trades', conn, if_exists='append', index=False)

        # Insert matched trades into the reconciliation results table
        matched_df = pd.DataFrame(self.matched_trades)
        if not matched_df.empty:
            matched_df.to_sql('reconciliation_results', conn, if_exists='append', index=False)

        conn.commit()
        conn.close()

def main():
    # Load data
    client_orders = load_client_orders()
    
    # Check if client orders were loaded successfully
    if client_orders is None:
        print("No client orders found. Exiting reconciliation.")
        return  # Exit if no client orders are found

    email_paths = [
        r'C:\Users\Sankalp\Desktop\trade_reconciliation\data\Trade File BROKER 1 - 31_01_2025.eml',
        r'C:\Users\Sankalp\Desktop\trade_reconciliation\data\Trade File BROKER 2 - 31_01_2025.eml',
        r'C:\Users\Sankalp\Desktop\trade_reconciliation\data\Trade File BROKER 3 - 31_01_2025.eml'
    ]
    
    broker_trades = extract_broker_files(email_paths)

    # Initialize reconciliation
    reconciler = TradeReconciliation(client_orders, pd.concat(broker_trades))
    
    # Run reconciliation
    reconciler.reconcile()
    
    # Get results
    results = reconciler.get_results()
    
    # Print summary
    print("\nMatched Trades:")
    print(results['matched'])
    
    print("\nUnmatched Trades:")
    print(results['unmatched'])
    
    print("\nExcess Trades:")
    print(results['excess'])

if __name__ == "__main__":
    main()
