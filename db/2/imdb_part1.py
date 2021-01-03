#! /usr/bin/env python3

import argparse
import pandas as pd
import sqlalchemy
from sqlalchemy import Table, Column, Numeric, String, MetaData, create_engine


parser = argparse.ArgumentParser(
    description=u"""Creates a table from CSV file with 4 columns""")
parser.add_argument("dbname", type=str, metavar="DBNAME", help=u"Name of database")
parser.add_argument("user", type=str, metavar="USERNAME", help=u"Username for auth.")
parser.add_argument("--password", type=str, required=False, metavar="PASSWORD", help=u"Password for auth.")
parser.add_argument("--host", type=str, required=False, default="localhost", metavar="HOST", help=u"Database host")
parser.add_argument("--port", type=str, required=False, default=5432, metavar="PORT", help=u"Database port")


def main(conn, filename):
    meta = MetaData()

    imdb_movies = Table(
        'imdb_movies', meta,
        Column('movie_title', String),
        Column('actor_1_name', String),
        Column('genres', String),
        Column('imdb_score', Numeric(2, 1))
    )
    meta.create_all(conn)

    try:
        my_csv = pd.read_csv(filename, sep=',',
            usecols=['movie_title', 'actor_1_name', 'genres', 'imdb_score'])
        my_csv = my_csv[['movie_title', 'actor_1_name', 'genres', 'imdb_score']]
        my_csv.to_sql('imdb_movies', conn, index=False, if_exists='append')
    except FileNotFoundError:
        print('No such file')


if __name__ == "__main__":
    args = parser.parse_args()
    host = args.host
    db = args.dbname
    user = args.user
    password = args.password
    port = args.port
    filename = "movie_metadata.csv"

    try:
        engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')
        conn = engine.connect()
        main(conn, filename)
    except sqlalchemy.exc.OperationalError as error:
        print('Unable to connect\n', error)
        conn = None
    finally:
        if(conn):
            conn.close()
            print('Disconnected')
