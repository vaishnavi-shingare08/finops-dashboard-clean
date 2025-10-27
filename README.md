Absolutely! Here’s a **ready-to-paste, clean, GitHub-friendly README** for your repo `finops-dashboard-clean`. It’s polished, structured, and easy to follow:

---

# 💰 FinOps Dashboard for Cloud Cost Visibility (Free Tier Usage Tracker)

### 🎯 Objective

The goal of this project is to **monitor AWS Free Tier usage and cloud costs**, detect services approaching billing limits, and visualize trends in **Grafana** using automated data collection stored in **SQLite**.

---

## 🧠 Project Overview

This FinOps Dashboard helps you:

* Monitor AWS Free Tier service usage daily.
* Fetch real-time cost data using **AWS Cost Explorer API**.
* Store data in a **SQLite database** on an EC2 instance.
* Automate daily updates using **cron jobs**.
* Visualize data in **Grafana dashboards**.
* Identify services at risk of exceeding Free Tier limits.

Think of it as a **smart expense tracker** for your AWS account!

---

## 🧩 Tech Stack

| Component                   | Purpose                               |
| --------------------------- | ------------------------------------- |
| AWS EC2 (Amazon Linux 2023) | Hosting Python scripts & Grafana      |
| AWS Cost Explorer API       | Fetches daily AWS cost and usage data |
| Python 3 + Boto3            | Fetch & parse API data                |
| SQLite                      | Store usage and cost data             |
| Grafana                     | Dashboard visualization               |
| Cron (cronie)               | Automate daily data collection        |

---

## 🏗 Setup and Implementation Steps

### Stage 1: AWS Setup

#### 1.1 Create AWS Account

* Sign up at [https://aws.amazon.com](https://aws.amazon.com).
* Enable Free Tier (automatic for new accounts).

#### 1.2 Enable Cost Explorer

* Go to **Billing → Cost Explorer → Enable Cost Explorer**.

#### 1.3 Create IAM User

* Go to **IAM → Users → Create User**
* Username: `finops-tracker`
* Enable **Programmatic Access**
* Attach policy: `AmazonCostExplorerReadOnlyAccess`
* Download **Access Key ID** and **Secret Access Key**.

---

### Stage 2: EC2 Instance Setup

#### 2.1 Launch EC2 Instance

* Use **Amazon Linux 2023 (Free Tier)**
* Instance type: `t2.micro`
* Allow **SSH (port 22)** and later **HTTP (port 3000)**

Connect using SSH:

```bash
ssh -i "your-key.pem" ec2-user@<EC2-Public-IP>
```

---

### Stage 3: Install Required Packages

```bash
sudo dnf update -y
sudo dnf install python3 python3-pip sqlite -y
```

Create project folder:

```bash
mkdir FinOpsDashboard && cd FinOpsDashboard
```

Create virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install boto3 python-dotenv
```

---

### Stage 4: Fetch AWS Cost Data

Create `fetch_cost_data.py` inside your project folder:

```python
import boto3
import sqlite3
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load AWS credentials from .env
load_dotenv()
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
REGION = os.getenv("AWS_REGION", "ap-south-1")

# Connect to AWS Cost Explorer
client = boto3.client(
    'ce',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=REGION
)

# Connect to SQLite DB
conn = sqlite3.connect('finops_data.db')
cursor = conn.cursor()

# Create table if not exists
cursor.execute('''
CREATE TABLE IF NOT EXISTS aws_costs (
    date TEXT,
    service TEXT,
    amount REAL
)
''')

# Fetch yesterday’s cost
end = datetime.utcnow().date()
start = end - timedelta(days=1)

response = client.get_cost_and_usage(
    TimePeriod={'Start': str(start), 'End': str(end)},
    Granularity='DAILY',
    Metrics=['UnblendedCost'],
    GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
)

# Insert data into DB
for group in response['ResultsByTime'][0]['Groups']:
    service = group['Keys'][0]
    amount = float(group['Metrics']['UnblendedCost']['Amount'])
    cursor.execute("INSERT INTO aws_costs VALUES (?, ?, ?)", (str(start), service, amount))

conn.commit()
conn.close()
print("✅ Data stored successfully!")
```

Run it:

```bash
python3 fetch_cost_data.py
```

Check stored data:

```bash
sqlite3 finops_data.db "SELECT * FROM aws_costs;"
```

---

### Stage 5: Automate Daily Data Collection

Install and start cron:

```bash
sudo dnf install cronie -y
sudo systemctl enable crond
sudo systemctl start crond
```

Add cron job:

```bash
(crontab -l 2>/dev/null; echo "0 9 * * * /home/ec2-user/FinOpsDashboard/venv/bin/python3 /home/ec2-user/FinOpsDashboard/fetch_cost_data.py") | crontab -
```

Verify cron job:

```bash
crontab -l
```

---

### Stage 6: Install and Configure Grafana

Install Grafana:

```bash
sudo tee /etc/yum.repos.d/grafana.repo<<EOF
[grafana]
name=Grafana
baseurl=https://packages.grafana.com/oss/rpm
repo_gpgcheck=1
enabled=1
gpgcheck=1
gpgkey=https://packages.grafana.com/gpg.key
EOF

sudo dnf install grafana -y
sudo systemctl enable grafana-server
sudo systemctl start grafana-server
```

Open Port 3000 in EC2 Security Group.

Access Grafana:

```
http://<EC2-Public-IP>:3000
```

Default login:

* Username: `admin`
* Password: `admin`

---

### Stage 7: Add SQLite Data Source

Install SQLite plugin:

```bash
sudo grafana-cli plugins install frser-sqlite-datasource
sudo systemctl restart grafana-server
```

Configure data source in Grafana:

* Database path: `/home/ec2-user/FinOpsDashboard/finops_data.db`
* Click **Save & Test**

---

### Stage 8: Create Dashboard Panels

1. Dashboards → Create → New Dashboard
2. Add **Table Panel**

```sql
SELECT date, service, amount FROM aws_costs ORDER BY date DESC;
```

3. Add **Bar Chart Panel** for daily cost trends
4. Customize colors and alerts

---

## 🛠 Automation Summary

| Task            | Tool           | Frequency           |
| --------------- | -------------- | ------------------- |
| Fetch cost data | Python (boto3) | Daily (cron job)    |
| Store data      | SQLite         | Local database      |
| Visualize cost  | Grafana        | Real-time dashboard |

---

## 📊 Example Output

**Database Table (`aws_costs`)**:

| date       | service    | amount      |
| ---------- | ---------- | ----------- |
| 2025-10-25 | Amazon EC2 | 0.00        |
| 2025-10-25 | Amazon S3  | 0.000000009 |
| 2025-10-25 | AWS Glue   | 0.00        |

---

## 📫 Results

✅ Automated daily AWS cost tracking
✅ Visualized usage on Grafana dashboard
✅ Avoids accidental Free Tier overages
✅ Fully deployable on AWS EC2 (Free Tier)

---

## 👩‍💻 Author

**Vaishnavi Shingare**
AWS Engineer | FinOps Enthusiast | Cloud Cost Optimization

---

## 🚀 How to Use This Repository

```bash
# Clone the repository
git clone https://github.com/vaishnavi-shingare08/finops-dashboard-clean.git
cd finops-dashboard-clean

# Configure AWS credentials in .env
python3 fetch_cost_data.py
```

---

## 📝 License

MIT License — Feel free to use and modify
