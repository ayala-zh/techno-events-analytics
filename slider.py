import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

DB_NAME = "techno_events_db"
DB_USER = "postgres"
DB_PASSWORD = "0000"
DB_HOST = "localhost"
DB_PORT = "5432"

engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

def run_query(query):
    return pd.read_sql(query, engine)

# --- Query for slider ---
df = run_query("""
    SELECT e.date::date AS event_date,
           g.name AS genre,
           COUNT(eh.id) FILTER (WHERE eh.has_attended) AS attendance
    FROM events e
    JOIN eventhistory eh ON eh.event_id = e.id
    JOIN genres g ON e.genre_id = g.id
    GROUP BY e.date, g.name
    ORDER BY e.date;
""")

# Add year for animation
df["year"] = pd.to_datetime(df["event_date"]).dt.year

# --- Plotly scatter with slider ---
fig = px.scatter(
    df,
    x="genre",
    y="attendance",
    size="attendance",
    color="genre",
    animation_frame="year",
    title="Techno Events Attendance Over Time"
)

fig.show()
