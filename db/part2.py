 #!/usr/bin/env python3

import psycopg2
import argparse
from datetime import datetime


parser = argparse.ArgumentParser(
    description=u"""Allows to see issues and more selected by product name within date range""")
parser.add_argument("start_date", type=str, metavar="START_DATE", help=u"Start date, format YYYY-MM-DD")
parser.add_argument("end_date", type=str, metavar="END_DATE", help=u"End date, format YYYY-MM-DD")


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
    host = "localhost"
    db = "postgres"
    user = "ilchenkoslava"

    args = parser.parse_args()
    start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
    end_date = datetime.strptime(args.end_date, "%Y-%m-%d")

    try:
        conn = psycopg2.connect(f"host={host} dbname={db} user={user}")
        cur = conn.cursor()
        main(cur, conn, start_date, end_date)
    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from PostgreSQL\n", error)
    finally:
        if(conn):
            cur.close()
            conn.close()
