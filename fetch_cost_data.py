import boto3
import sqlite3
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# Load AWS credentials from .env file
load_dotenv()

# AWS credentials from environment variables
ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
REGION = "ap-south-1"

# Initialize AWS Cost Explorer client
client = boto3.client(
    'ce',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name=REGION
)

# Get today's date
today = datetime.now().date()
start_date = str(today)
end_date = str(today)

# Fetch cost data
response = client.get_cost_and_usage(
    TimePeriod={
        'Start': start_date,
        'End': end_date
    },
    Granularity='DAILY',
    Metrics=['UnblendedCost'],
    GroupBy=[
        {
            'Type': 'DIMENSION',
            'Key': 'SERVICE'
        }
    ]
)

# Connect to SQLite database
conn = sqlite3.connect('finops_data.db')
cur = conn.cursor()

# Create table if not exists
cur.execute('''
    CREATE TABLE IF NOT EXISTS aws_costs (
        date TEXT,
        service TEXT,
        cost REAL
    )
''')

# Insert data into database
for result in response['ResultsByTime']:
    date = result['TimePeriod']['Start']
    for group in result['Groups']:
        service = group['Keys'][0]
        cost = float(group['Metrics']['UnblendedCost']['Amount'])
        
        cur.execute(
            "INSERT INTO aws_costs (date, service, cost) VALUES (?, ?, ?)",
            (date, service, cost)
        )

# Commit and close
conn.commit()
conn.close()

print("✅ Data stored successfully!")
