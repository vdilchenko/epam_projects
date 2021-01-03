 #!/usr/bin/env python3

import psycopg2
import argparse

parser = argparse.ArgumentParser(
    description=u"""Allows to create a table from CSV file""")
parser.add_argument("dbname", type=str, metavar="DBNAME", help=u"Name of database")
parser.add_argument("user", type=str, metavar="USERNAME", help=u"Username for auth.")
parser.add_argument("--password", type=str, required=False, metavar="PASSWORD", help=u"Password for auth.")
parser.add_argument("--host", type=str, required=False, default="localhost", metavar="HOST", help=u"Database host")
parser.add_argument("--port", type=str, required=False, default=5432, metavar="PORT", help=u"Database port")


def main(cur, conn, filename):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS consumer_complaints(
        date_received date not null,
        product_name text not null,
        sub_product text,
        issue text not null,
        sub_issue text,
        consumer_complaint_narrative text,
        company_public_response text,
        company text not null,
        state_name varchar(2),
        zip_code varchar(10),
        tags text,
        consumer_consent_provided varchar(30),
        CHECK (consumer_consent_provided in ('', 'N/A', 'Consent provided', 'Consent not provided', 'Other')),
        submitted_via text not null,
        date_sent_to_company date not null,
        company_response_to_consumer varchar(35),
        CHECK (company_response_to_consumer in ('', 'Closed with explanation', 'Closed', 'Closed with monetary relief', 'Closed with non-monetary relief', 'Untimely response')),
        timely_response varchar(3) CHECK (timely_response in ('Yes', 'No', '')),
        consumer_disputed varchar(3) CHECK (consumer_disputed in ('Yes', 'No', '')),
        complaint_id serial,
        CONSTRAINT pk_consumer_complaint PRIMARY KEY (complaint_id)
    )
    """)
    conn.commit()

    cur.execute("""
        SELECT count(1) FROM consumer_complaints
    """)
    conn.commit()
    table_count = cur.fetchone()
    assert table_count[0] == 0, 'table has data in it'

    sql = "COPY consumer_complaints FROM STDIN DELIMITER ',' CSV HEADER"
    with open(filename, "r") as f:
        cur.copy_expert(sql, f)
    conn.commit()

    cur.execute("SELECT count(*) FROM consumer_complaints;")
    conn.commit()

    table_count = cur.fetchone()
    assert table_count[0] != 0, 'Table has no data in it'


if __name__ == "__main__":
    args = parser.parse_args()
    host = args.host
    db = args.dbname
    user = args.user
    password = args.password
    port = args.port
    filename = "P9-ConsumerComplaints.csv"

    try:
        conn = psycopg2.connect(f"dbname={db} user={user} password={password} host={host} port={port}")
        cur = conn.cursor()
        main(cur, conn, filename)
    except psycopg2.OperationalError as error:
        print('Unable to connect\n', error)
        conn = None
    finally:
        if(conn):
            cur.close()
            conn.close()
            print('Disconnected')