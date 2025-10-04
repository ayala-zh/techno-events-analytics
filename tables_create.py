import psycopg2

def create_tables(db_name="techno_events", user="postgres", password="0000", host="localhost", port="5432"):
    schema = """
    CREATE TABLE IF NOT EXISTS countries (
      Id SERIAL PRIMARY KEY,
      Name VARCHAR(100) NOT NULL
    );

    CREATE TABLE IF NOT EXISTS locations (
      Id SERIAL PRIMARY KEY,
      Name VARCHAR(100) NOT NULL,
      CountryId INTEGER REFERENCES countries(Id)
    );

    CREATE TABLE IF NOT EXISTS genres (
      Id SERIAL PRIMARY KEY,
      Name VARCHAR(100) NOT NULL
    );

    CREATE TABLE IF NOT EXISTS users (
      Id SERIAL PRIMARY KEY,
      UserName VARCHAR(50) UNIQUE NOT NULL,
      FullName VARCHAR(150),
      Email VARCHAR(255),
      LocationId INTEGER REFERENCES locations(Id),
      RegistrationDate TIMESTAMP,
      Password VARCHAR(255),
      Bio TEXT
    );

    CREATE TABLE IF NOT EXISTS artists (
      Id SERIAL PRIMARY KEY,
      Name VARCHAR(150) NOT NULL,
      GenreId INTEGER REFERENCES genres(Id),
      Bio TEXT,
      PictureUrl TEXT,
      Spotify TEXT,
      Soundcloud TEXT,
      Youtube TEXT
    );

    CREATE TABLE IF NOT EXISTS events (
      Id SERIAL PRIMARY KEY,
      Name VARCHAR(200) NOT NULL,
      Description TEXT,
      Date TIMESTAMP,
      GenreId INTEGER REFERENCES genres(Id),
      LocationId INTEGER REFERENCES locations(Id),
      Venue VARCHAR(200),
      CoverUrl TEXT
    );

    CREATE TABLE IF NOT EXISTS eventhistory (
      Id SERIAL PRIMARY KEY,
      UserId INTEGER REFERENCES users(Id),
      EventId INTEGER REFERENCES events(Id),
      HasAttended BOOLEAN DEFAULT FALSE,
      IsInterested BOOLEAN DEFAULT FALSE,
      Rate SMALLINT CHECK (rate >= 1 AND rate <= 5)
    );

    CREATE TABLE IF NOT EXISTS favoriteartists (
      Id SERIAL PRIMARY KEY,
      UserId INTEGER REFERENCES users(Id),
      ArtistId INTEGER REFERENCES artists(Id)
    );

    CREATE TABLE IF NOT EXISTS favoritegenres (
      Id SERIAL PRIMARY KEY,
      UserId INTEGER REFERENCES users(Id),
      GenreId INTEGER REFERENCES genres(Id)
    );

    CREATE TABLE IF NOT EXISTS eventartists (
      Id SERIAL PRIMARY KEY,
      EventId INTEGER REFERENCES events(Id),
      ArtistId INTEGER REFERENCES artists(Id)
    );

    CREATE INDEX IF NOT EXISTS idx_events_location ON events(LocationId);
    CREATE INDEX IF NOT EXISTS idx_events_genre ON events(GenreId);
    CREATE INDEX IF NOT EXISTS idx_users_location ON users(LocationId);
    """

    try:
        conn = psycopg2.connect(dbname=db_name, user=user, password=password, host=host, port=port)
        cursor = conn.cursor()
        cursor.execute(schema)
        conn.commit()
        cursor.close()
        conn.close()
        print("Tables created successfully.")
    except Exception as e:
        print("Error creating tables:", e)

if __name__ == "__main__":
    create_tables()
