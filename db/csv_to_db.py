 #!/usr/bin/env python3

import psycopg2
import csv

host = ""
db = ""
user = ""

conn = psycopg2.connect(f"host={host} dbname={db} user={user}")
cur = conn.cursor()

cur.execute("CREATE SCHEMA homework")
cur.execute("SET search_path to homework")
cur.execute("""
	CREATE TABLE consumer_complaints(
	date_received date not null,
	product_name text not null,
	sub_product text,
	issue text not null,
	sub_issue text,
	ccn text,
	cpr text,
	company text not null,
	state varchar(2),
	zip_code varchar(5),
	tags text,
	ccp varchar(30) CHECK (ccp in ('', 'N/A', 'Consent provided', 'Consent not provided', 'Other')),
	submition_type text not null,
	date_sent date not null,
	crtc varchar(35) CHECK (crtc in ('', 'Closed with explanation', 'Closed', 'Closed with monetary relief', 'Closed with non-monetary relief', 'Untimely response')),
	timely_response varchar(3) CHECK (timely_response in ('Yes', 'No', '')),
	consumer_disputed varchar(3) CHECK (consumer_disputed in ('Yes', 'No', '')),
	complaint_id numeric PRIMARY KEY
)
""")
conn.commit()

with open('P9-ConsumerComplaints.csv', 'r') as f:
	reader = csv.reader(f)
	next(reader)
	for row in reader:
		cur.execute(
		"INSERT INTO consumer_complaints VALUES \
		(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
		row
	)
conn.commit()
