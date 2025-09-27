# 🎧 RavePulse – Techno Events Analytics

## 📌 Project Overview

Our **company**, **RavePulse**, is a data-driven platform for techno music enthusiasts.  
It tracks events, artists, and users’ preferences worldwide, providing insights into:

- 🌍 **Popular event locations** – Find out which cities host the most raves.
- 🎶 **Most-followed artists** – Discover trending DJs and performers.
- 👥 **User attendance trends** – See how participation changes over time.
- 🎼 **Genre preferences per region** – Understand what sound the crowd wants.
- ⭐ **Event ratings and feedback** – Measure audience satisfaction.

The goal of this project is to build a **complete analytics solution** using:

- **SQL** – For complex business-oriented queries
- **Python** – To automate data processing
- **Apache Superset** – To create interactive visual dashboards

This helps event organizers **plan better events**, **target the right audience**, and **increase overall engagement**.

---

## 🗄 Database Schema

RavePulse is powered by a relational database with the following main tables:

- **users** 👤 – stores user information (id, name, age, city, country)
- **events** 🎟 – stores event details (id, name, date, venue, genre)
- **eventhistory** 📜 – a join table connecting users and events (attendance, rating, interest)

This schema allows us to explore **who attended what**, **when**, and **where**,  
making it easy to build meaningful insights.
<img width="1850" height="1415" alt="image" src="https://github.com/user-attachments/assets/d3cd2a1f-a38d-4099-acbb-630bc16e5976" />
---

## 📊 Business Insights & Queries

Our analytics include:

- **Top Venues** – Find the most frequently used venues
- **Monthly Event Trends** – See which months are the most active
- **City Participation Rates** – Understand which cities have the highest engagement
- **Average Ratings per Event** – Detect events that left the best impression
- **Active Users** – Identify loyal participants who attend the most raves
- **Genre Popularity Analysis** – Measure which genres dominate the techno scene

All queries are stored in [`queries.sql`](queries.sql) and can be executed automatically via Python.

---

## 🐍 Python Automation

We built a Python script that:

- Connects to the PostgreSQL database
- Reads all SQL queries from `queries.sql`
- Executes them in sequence
- Prints results in a clean, readable format

This ensures we can **rerun the entire analysis with a single command**,  
even if new data is added to the database.

---

## 📊 Visualization with Apache Superset



---

## 🚀 Getting Started

1. **Clone this repository:**
   ```bash
   git clone (https://github.com/ayala-zh/techno-events-analytics)
   cd techno-events-analytics
2. **Set up the database**
# Open psql
psql -U postgres
# Create and populate the database
CREATE DATABASE techno_events_db;
\c techno_events_db
\i queries.sql
3. **Configure Project**
   - Open `main.py`
   - Update your database password if needed:
     ```python
     conn = psycopg2.connect(
         host="localhost",
         user="postgres",
         password="your_password",
         dbname="techno_events_db"
     )
     ```
4. **Run Script**
   ```bash
python Main.py

