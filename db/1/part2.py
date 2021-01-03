 #!/usr/bin/env python3

import psycopg2
from psycopg2 import errorcodes
import argparse
from datetime import datetime
import re


parser = argparse.ArgumentParser(
    description=u"""Allows to see issues and more selected by product name within date range""")
parser.add_argument("dbname", type=str, metavar="DBNAME", help=u"Name of database")
parser.add_argument("user", type=str, metavar="USERNAME", help=u"Username for auth.")
parser.add_argument("start_date", type=str, metavar="START_DATE", help=u"Start date, format YYYY-MM-DD")
parser.add_argument("end_date", type=str, metavar="END_DATE", help=u"End date, format YYYY-MM-DD")
parser.add_argument("--password", type=str, required=False, metavar="PASSWORD", help=u"Password for auth.")
parser.add_argument("--host", type=str, required=False, default="localhost", metavar="HOST", help=u"Database host")
parser.add_argument("--port", type=str, required=False, default=5432, metavar="PORT", help=u"Database port")



def main(cur, conn, start_date, end_date):
    cur.execute("""
        SELECT 
            product_name, 
            count(issue) issues,
            count(issue) filter (where timely_response = 'Yes') as issues_done_timely,
            count(issue) filter (where consumer_disputed = 'Yes') as issues_disputed
        from consumer_complaints
        where date_received >= '{}' and date_received <= '{}'
        group by product_name
        order by issues desc
    """.format(start_date, end_date))

    rows = cur.fetchall()
    print("Product name | issues | issuesd_done_timely | issues_disuputed")
    for row in rows:
        print(row[0], row[1], row[2], row[3])

if __name__ == "__main__":
    args = parser.parse_args()
    host = args.host
    db = args.dbname
    user = args.user
    password = args.password
    port = args.port
    
    pattern='(?:[0-9]{2}(/|-)){2}[0-9]{2}'
    assert re.search(pattern, args.start_date), 'Bad input for start date'
    assert re.search(pattern, args.end_date), 'Bad input for end date'
    start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
    end_date = datetime.strptime(args.end_date, "%Y-%m-%d")

    try:
        conn = psycopg2.connect(f"dbname={db} user={user} password={password} host={host} port={port}")
        cur = conn.cursor()
        main(cur, conn, start_date, end_date)
    except psycopg2.errors.UndefinedTable as error:
        print('No such table\n', error.pgerror)
    except psycopg2.OperationalError as error:
        print('Unable to connect\n', error)
        conn = None
    finally:
        if(conn):
            cur.close()
            conn.close()
            print('Disconnected')
