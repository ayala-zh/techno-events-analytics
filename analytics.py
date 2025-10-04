import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine

# Database connection details
DB_NAME = "techno_events_db"
DB_USER = "postgres"
DB_PASSWORD = "0000"
DB_HOST = "localhost"
DB_PORT = "5432"

engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# Helper function to run queries
def run_query(query):
    return pd.read_sql(query, engine)

# Helper function to save simple charts
def save_chart(df, kind, title, xlabel, ylabel, filename, **kwargs):
    ax = df.plot(kind=kind, **kwargs)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.savefig(f"charts/{filename}")
    plt.close()
    print(f"✅ Saved {kind} chart: {title}\n   Rows: {len(df)} | File: charts/{filename}\n")

def generate_charts():
    # 1. Pie chart: Events distribution by country
    df = run_query("""
        SELECT c.name AS country, COUNT(*) AS event_count
        FROM events e
        JOIN locations l ON e.location_id = l.id
        JOIN countries c ON l.country_id = c.id
        GROUP BY c.name
        ORDER BY event_count DESC;
    """)
    df.set_index("country")["event_count"].plot.pie(autopct='%1.1f%%')
    plt.title("Events Distribution by Country")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig("charts/events_by_country.png")
    plt.close()
    print(f"✅ Saved pie chart: Events Distribution by Country\n   Rows: {len(df)} | File: charts/events_by_country.png\n")

    # 2. Bar chart: Top 10 Artists by Performances
    df = run_query("""
        SELECT a.name, COUNT(ea.id) AS performances
        FROM eventartists ea
        JOIN artists a ON ea.artist_id = a.id
        JOIN events e ON ea.event_id = e.id
        GROUP BY a.id, a.name
        ORDER BY performances DESC
        LIMIT 10;
    """)
    save_chart(df.set_index("name"), "bar", "Top 10 Artists by Performances", "Artists", "Performances", "top_artists.png")

    # 3. Horizontal bar chart: Average Event Rating by Country
    df = run_query("""
        SELECT c.name AS country, ROUND(AVG(eh.rate), 2) AS avg_rating
        FROM eventhistory eh
        JOIN events e ON eh.event_id = e.id
        JOIN locations l ON e.location_id = l.id
        JOIN countries c ON l.country_id = c.id
        WHERE eh.rate IS NOT NULL
        GROUP BY c.name
        ORDER BY avg_rating DESC;
    """)
    save_chart(df.set_index("country"), "barh", "Average Event Rating by Country", "Avg Rating", "Country", "avg_rating_country.png")

    # 4. Line chart: Attendance by Day of the Week
    df = run_query("""
        SELECT TO_CHAR(e.date, 'Dy') AS day_of_week,
               COUNT(eh.id) FILTER (WHERE eh.has_attended) AS total_attendances
        FROM events e
        LEFT JOIN eventhistory eh ON eh.event_id = e.id
        JOIN locations l ON e.location_id = l.id
        JOIN countries c ON l.country_id = c.id
        GROUP BY TO_CHAR(e.date, 'Dy'), EXTRACT(DOW FROM e.date)
        ORDER BY EXTRACT(DOW FROM e.date);
    """)
    save_chart(df.set_index("day_of_week"), "line", "Attendance by Day of the Week", "Day", "Attendances", "attendance_by_day.png", marker="o")

    # 5. Top Countries by Attendance and Average Rating
    df = run_query("""
                   SELECT c.name                                      AS country,
                          COUNT(e.id)                                 AS total_events,
                          COUNT(CASE WHEN eh.has_attended THEN 1 END) AS total_attendance,
                          ROUND(AVG(eh.rate), 2)                      AS avg_rating
                   FROM events e
                            JOIN locations l ON e.location_id = l.id
                            JOIN countries c ON l.country_id = c.id
                            LEFT JOIN eventhistory eh ON e.id = eh.event_id
                   GROUP BY c.name
                   ORDER BY total_attendance DESC, avg_rating DESC LIMIT 10;
                   """)

    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Bar chart: total attendance
    ax1.bar(df["country"], df["total_attendance"], color="skyblue", label="Total Attendance")
    ax1.set_xlabel("Country")
    ax1.set_ylabel("Total Attendance", color="blue")

    # Line chart: average rating
    ax2 = ax1.twinx()
    ax2.plot(df["country"], df["avg_rating"], color="red", marker="o", label="Avg Rating")
    ax2.set_ylabel("Average Rating", color="red")

    plt.title("Top Countries by Attendance and Average Rating")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("charts/top_countries_attendance_rating.png")
    plt.close()
    print(
        f"✅ Saved chart: Top Countries by Attendance and Average Rating\n   Rows: {len(df)} | File: charts/top_countries_attendance_rating.png\n")

    # 6. Scatter plot: Ratings over Time (attendance highlighted)
    df = run_query("""
        SELECT e.date, eh.rate, eh.has_attended
        FROM eventhistory eh
        JOIN events e ON eh.event_id = e.id
        WHERE eh.rate IS NOT NULL;
    """)
    plt.figure(figsize=(10, 6))
    colors = df["has_attended"].map({True: "green", False: "red"})
    plt.scatter(df["date"], df["rate"], c=colors, alpha=0.6)
    plt.title("Scatter: Ratings Over Time (Attendance Highlighted)")
    plt.xlabel("Event Date")
    plt.ylabel("Rating")
    plt.tight_layout()
    plt.savefig("charts/scatter_ratings_over_time.png")
    plt.close()
    print(f"✅ Saved scatter plot: Ratings over Time\n   Rows: {len(df)} | File: charts/scatter_ratings_over_time.png\n")


if __name__ == "__main__":
    generate_charts()
