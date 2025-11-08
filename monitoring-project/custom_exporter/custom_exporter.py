from prometheus_client import start_http_server, Gauge, Counter, Histogram
import time
import requests
import random
from datetime import datetime
import psycopg2
import os

CITIES = {
    "Berlin": {"lat": 52.52, "lon": 13.41, "timezone": "Europe/Berlin"},
    "London": {"lat": 51.51, "lon": -0.13, "timezone": "Europe/London"},
    "Paris": {"lat": 48.85, "lon": 2.35, "timezone": "Europe/Paris"},
    "Amsterdam": {"lat": 52.37, "lon": 4.90, "timezone": "Europe/Amsterdam"},
}
SELECTED_CITY = os.getenv("CITY", "Berlin")  # default is Berlin

# Database connection
def get_db_connection():
    return psycopg2.connect(
        dbname="techno_events_db",
        user="postgres",
        password="0000",
        host="host.docker.internal",
        port="5432"
    )


# Create metrics - Database metrics
events_total = Gauge('techno_events_total', 'Total number of events in database')
active_users = Gauge('techno_active_users', 'Number of active users')
avg_rating = Gauge('techno_avg_rating', 'Average event rating')
top_genre_popularity = Gauge('techno_top_genre_popularity', 'Popularity of top genre')
api_requests_total = Counter('techno_api_requests_total', 'Total API requests')
request_duration = Histogram('techno_request_duration_seconds', 'Request duration')
event_attendance_rate = Gauge('techno_event_attendance_rate', 'Event attendance rate')
user_engagement_score = Gauge('techno_user_engagement_score', 'User engagement score')
database_size = Gauge('techno_database_size_mb', 'Database size in MB')
uptime_seconds = Gauge('techno_uptime_seconds', 'Service uptime in seconds')

# Weather API metrics
weather_temperature = Gauge('techno_weather_temperature', 'Current temperature in Celsius', ['city'])
weather_humidity = Gauge('techno_weather_humidity', 'Current humidity percentage', ['city'])
weather_windspeed = Gauge('techno_weather_windspeed', 'Current wind speed in km/h', ['city'])
weather_rain = Gauge('techno_weather_rain', 'Current rain volume', ['city'])
weather_api_status = Gauge('techno_weather_api_status', 'Weather API status (1=up, 0=down)', ['city'])

def get_weather_data():
    """Collect weather data for all configured cities"""
    for city, info in CITIES.items():
        try:
            lat, lon, tz = info["lat"], info["lon"], info["timezone"]
            response = requests.get(
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,rain&timezone={tz}",
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            current = data['current']

            weather_temperature.labels(city=city).set(current['temperature_2m'])
            weather_humidity.labels(city=city).set(current['relative_humidity_2m'])
            weather_windspeed.labels(city=city).set(current['wind_speed_10m'])
            weather_rain.labels(city=city).set(current.get('rain', 0))
            weather_api_status.labels(city=city).set(1)

            print(f"{city}: {current['temperature_2m']}°C, {current['relative_humidity_2m']}% humidity")

        except Exception as e:
            print(f"Weather API error ({city}): {e}")
            weather_temperature.labels(city=city).set(20.0)
            weather_humidity.labels(city=city).set(65.0)
            weather_windspeed.labels(city=city).set(15.0)
            weather_rain.labels(city=city).set(0.0)
            weather_api_status.labels(city=city).set(0)


def get_real_database_metrics():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Get total events
        cur.execute("SELECT COUNT(*) FROM events")
        events_total.set(cur.fetchone()[0])

        # Get active users
        cur.execute("SELECT COUNT(DISTINCT user_id) FROM eventhistory WHERE has_attended = true")
        active_users.set(cur.fetchone()[0])

        # Get average rating
        cur.execute("SELECT AVG(rate) FROM eventhistory WHERE rate IS NOT NULL")
        avg_rating.set(round(cur.fetchone()[0] or 0, 2))

        # Get attendance rate
        cur.execute("""
            SELECT 
                COUNT(*) FILTER (WHERE has_attended = true) * 100.0 / COUNT(*)
            FROM eventhistory
        """)
        event_attendance_rate.set(round(cur.fetchone()[0] or 0, 2))

        # Get database size (approximate)
        cur.execute("""
            SELECT pg_database_size('techno_events_db') / 1024 / 1024
        """)
        database_size.set(round(cur.fetchone()[0] or 0, 1))

        cur.close()
        conn.close()

    except Exception as e:
        print(f"Database error: {e}")
        # Fallback to simulated metrics
        events_total.set(random.randint(50, 100))
        active_users.set(random.randint(10, 25))
        avg_rating.set(round(random.uniform(3.5, 4.8), 2))
        event_attendance_rate.set(round(random.uniform(60, 90), 2))
        database_size.set(round(random.uniform(50, 150), 1))


def simulate_api_calls():
    api_requests_total.inc()

    # Simulate request duration
    with request_duration.time():
        time.sleep(random.uniform(0.1, 0.5))

    # Update uptime
    uptime_seconds.set(time.time() - start_time)

    # Simulate additional metrics
    top_genre_popularity.set(random.randint(20, 40))
    user_engagement_score.set(round(random.uniform(70, 95), 1))


if __name__ == '__main__':
    start_time = time.time()

    # Start Prometheus metrics server
    start_http_server(8000)
    print("Custom exporter started on port 8000")
    print("Collecting weather data for Berlin, Germany...")

    while True:
        get_real_database_metrics()
        get_weather_data()  # New: Get weather data every cycle
        simulate_api_calls()
        time.sleep(20)  # Update every 20 seconds as required