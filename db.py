import psycopg2


class DB:
    def __init__(self, dsn: str):
        self.connection = psycopg2.connect(dsn=dsn)
        self.connection.autocommit = True
        self.cursor = self.connection.cursor()
        self.create_movies_table()

    def create_movies_table(self):
        sql = """
            CREATE TABLE IF NOT EXISTS movies (
                title     TEXT PRIMARY KEY,
                rank      INTEGER,
                genre     TEXT,
                run_time  TEXT,
                rating    DECIMAL,
                year      INTEGER
            )
        """

        self.cursor.execute(sql)
        self.connection.commit()

    def save_movie(self, movie: dict):
        sql = """
            INSERT INTO public.movies (title, rank, genre, run_time, rating, year)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        try:
            self.cursor.execute(
                sql, (movie["title"], movie["rank"], movie["genre"], movie["run_time"], movie["rating"], movie["year"])
            )
        except psycopg2.IntegrityError:
            # Don't do anything when insert fails (row with same primary key already exist)
            pass

    def get_movies(self, years: int, search: str):
        movies = []
        sql = """
            SELECT title, rank, genre, run_time, rating, year
            FROM movies
            WHERE year IN %s AND title LIKE %s
            ORDER BY year ASC
        """

        self.cursor.execute(sql, (tuple(years), f"%{search}%"))

        for result in self.cursor.fetchall():
            movies.append({
                "title": result[0],
                "rank": result[1],
                "genre": result[2],
                "run_time": result[3],
                "rating": float(result[4]) if result[4] else None,
                "year": int(result[5]) if result[5] else None,
            })

        return movies

    def close(self):
        self.cursor.close()
        self.connection.close()


db = DB(dsn="postgresql://postgres:postgres@postgres:5432/movies")
