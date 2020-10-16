 #!/usr/bin/env python3

import psycopg2


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

    sql = "COPY consumer_complaints FROM STDIN DELIMITER ',' CSV HEADER"
    with open(filename, "r") as f:
        cur.copy_expert(sql, f)
    conn.commit()


if __name__ == "__main__":
    host = ""
    db = ""
    user = ""
    filename = "P9-ConsumerComplaints.csv"

    try:
        conn = psycopg2.connect(f"host={host} dbname={db} user={user}")
        cur = conn.cursor()
        main(cur, conn, filename)
    except (Exception, psycopg2.Error) as error:
        print("Error while working with PostgreSQL", error)
    finally:
        if(conn):
            cur.close()
            conn.close()