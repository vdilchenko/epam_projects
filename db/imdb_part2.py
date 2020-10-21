#! /usr/bin/env python3

import argparse
from sqlalchemy import create_engine


parser = argparse.ArgumentParser(
    description=u"""Allows to search movies that are found by some input string""")
parser.add_argument("string", type=str, metavar="SOMESTRING", help=u"String input to search by (in quotes)")
parser.add_argument("dbname", type=str, metavar="DBNAME", help=u"Name of database")
parser.add_argument("user", type=str, metavar="USERNAME", help=u"Username for auth.")
parser.add_argument("--password", type=str, required=False, metavar="PASSWORD", help=u"Password for auth.")
parser.add_argument("--host", type=str, required=False, default="localhost", metavar="HOST", help=u"Database host")
parser.add_argument("--port", type=str, required=False, default=5432, metavar="PORT", help=u"Database port")
    

def main(conn, filename, somestring):
    somestring = somestring.replace(" ", "|")
    query = conn.execute("""
        SELECT movie_title, actor_1_name, genres, imdb_score
        FROM imdb_movies
        WHERE to_tsvector(movie_title) @@ to_tsquery('{}')
        ORDER BY imdb_score
    """.format(somestring))

    for data in query:
        print(data)


if __name__ == "__main__":
    args = parser.parse_args()
    host = args.host
    db = args.dbname
    user = args.user
    password = args.password
    port = args.port
    filename = "movie_metadata.csv"
    somestring = args.string

    try:
        engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')
        conn = engine.connect()
        main(conn, filename, somestring)
    except (Exception) as error:
        print("Error while working with PostgreSQL", error)
    finally:
        if(conn):
            conn.close()
