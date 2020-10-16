 #!/usr/bin/env python3

import psycopg2
import argparse


parser = argparse.ArgumentParser(
    description=u"""Allows to see issues and related attributes for the most issued state of the company""")
parser.add_argument("company_name", type=str, metavar="COMPANY", help=u"Type company name")
parser.add_argument("--output_size", type=int, default=10, required=False, metavar="OUTPUT_SIZE", help=u"Choose the amount of data to be displayed")
parser.add_argument("--fetch_all", type=bool, default=False, metavar="FETCH_ALL", help=u"Choose to fetch each row or not")


def main(cur, conn, company, size, fetch_all):
    cur.execute("""
        with max_issues_state as (
            select state_name, count(issue) amount_issues
            from consumer_complaints
            where company = '{0}' and state_name is not null
            group by state_name
            order by amount_issues desc
            limit 1)
        select * from consumer_complaints
        where company = '{0}' and state_name = (select state_name from max_issues_state)
    """.format(company))

    if(fetch_all):
        rows = cur.fetchall()
    else:
        rows = cur.fetchmany(size)

    cur.execute("Select * FROM consumer_complaints LIMIT 0")
    colnames = [desc[0] for desc in cur.description]
    print(' | '.join(colnames))
    print(rows)

if __name__ == "__main__":
    host = ""
    db = ""
    user = ""

    args = parser.parse_args()
    company = args.company_name
    size = args.output_size
    fetch = args.fetch_all

    try:
        conn = psycopg2.connect(f"host={host} dbname={db} user={user}")
        cur = conn.cursor()
        main(cur, conn, company, size, fetch)
    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from PostgreSQL\n", error)
    finally:
        if(conn):
            cur.close()
            conn.close()
