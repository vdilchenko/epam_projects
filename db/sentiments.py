import collections
import sqlite3
import re


def calc_sentiment(rates, sen, sentiment=0):
    length = len(sen.split())
    for word in sen.split():
        cleaned_word = re.sub('\W+$', '', word)
        for k, v in rates.items():
            if cleaned_word in set(v):
                sentiment += int(k)
    sentiment = sentiment / length
    return sentiment


def main(conn, cur, rates):
    cur.execute("select id, tweet_text from texts")
    one = cur.fetchall()
    for _id, text in one:
        t_s = calc_sentiment(rates, text)
        cur.execute("update tweets set tweet_sentiment = (?) where text_id = (?)", (t_s, _id))
        conn.commit()


if __name__ == '__main__':
    rates = collections.defaultdict(list)
    with open('/Users/ilchenkoslava/Downloads/test dwh engineer/AFINN-111.txt', 'r') as f:
        for line in f:
            line_splitted = line.split('\t')
            rates[line_splitted[1].replace('\n', '')].append(line_splitted[0])

    db = "/Users/ilchenkoslava/Downloads/tweets.db"
    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        main(conn, cur, rates)
        query = cur.execute("select count(1) from tweets where tweet_sentiment is null").fetchone()
        assert query[0] == 0
    except sqlite3.Error as e:
        print(e)
    finally:
        if(conn):
            cur.close()
            conn.close()
