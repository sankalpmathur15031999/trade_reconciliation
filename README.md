# trade_reconciliation
Project Overview
This project automates the trade reconciliation process between client orders and broker trades. It extracts trade data from emails, processes and reconciles the trades, and generates detailed reports on matched, unmatched, and excess trades.
Table of Contents
•	Prerequisites
•	Installation Instructions
•	Running the Project
•	Reconciliation Logic
•	Scheduler Setup
•	Report Generation
•	Contributing
________________________________________
Prerequisites
Before running the project, ensure you have the following installed:
•	Python 3.8+: The project is built with Python 3.
•	Required Python Libraries: The necessary libraries are listed in requirements.txt. You can install them using pip.
Installation Instructions
Activate the virtual environment:
•	On Windows:
.\myenv\Scripts\activate
•	On MacOS/Linux:
source myenv/bin/activate

Running the Project:
1. Set Up the Project Directory Structure
•	Ensure that the project directory has the following structure:

trade_reconciliation/
├── data/                # Email files with trade data
├── Scripts/            # Python scripts
├── Reports/         # Output reports will be generated here
└── README.md    # This file

2. Run the Reconciliation Script
•	Navigate to the Scripts folder and execute the scripts.
cd /Scripts
python run_reconciliation.py

The script will automatically:
•	Load client orders and broker trades.
•	Reconcile the trades.
•	Generate reports (matched, unmatched, and excess trades).
•	Save the results in the Reports directory.
Scheduler Setup
To automate the reconciliation process, you can schedule the script to run at specific intervals (e.g., daily, weekly). Below are instructions for setting up a scheduler:
1. Windows Task Scheduler:
•	Use Task Scheduler to schedule your Python script to run at specific times (e.g., every day at 8:00 AM).
•	Set up an action to run python.exe with your run_reconciliation.py script as an argument.
2. Cron Job (Linux/Mac):
•	Set up a cron job that runs the script at the specified intervals.
•	Example: To run the script every day at 2:00 AM:
bash
Copy
0 2 * * * /path/to/python /path/to/project/Scripts/run_reconciliation.py
________________________________________
Report Generation
Generated Reports
After the reconciliation process is completed, the following reports will be saved in the Reports folder:
1.	Matched Trades (matched_trades.xlsx)
o	This report contains the trades that were successfully matched between client orders and broker trades.
2.	Unmatched Trades (unmatched_trades.xlsx)
o	This report contains the trades that could not be matched. These could be due to missing trades or discrepancies between the client orders and broker trades.
3.	Excess Trades (excess_trades.xlsx)
o	This report contains the trades in the broker's dataset that do not have corresponding client orders.
________________________________________
This README provides a structured approach for users to understand the setup and usage of your trade reconciliation project.




