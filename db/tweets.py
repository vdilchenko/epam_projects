import sqlite3
import json


def extract_keys(key, var, visited, tweet_data):
    if hasattr(var, 'items'):
        for k, v in var.items():
            if k == key and k not in visited:
                visited.add(k)
                tweet_data[k] = v
            if isinstance(v, dict):
                extract_keys(key, v, visited, tweet_data)
            elif isinstance(v, list) is True and len(v) == 1:
                extract_keys(key, v[0], visited, tweet_data)
    return tweet_data


def execute_import(cur, conn, data):
    cur.execute("insert into Tweet (name, tweet_text, \
        country_code, display_url, lang, created_at, location) \
        values (?, ?, ?, ?, ?, ?, ?)", (
        data['name'], data['text'], data['country_code'], data['display_url'],
        data['lang'], data['created_at'], data['location']))
    conn.commit()


def main(tweets, columns, cur, conn):
    for tweet in tweets:
        keys = tweet.keys()
        if "delete" in keys:
            continue
        visited = set()
        tweet_data = {k: None for k in columns}
        for col in columns:
            tweet_data.update(extract_keys(col, tweet, visited, tweet_data))
        execute_import(cur, conn, tweet_data)


if __name__ == "__main__":
    tweets_path = "/Users/ilchenkoslava/Downloads/test dwh engineer/three_minutes_tweets.json"
    tweets = (json.loads(tweet) for tweet in open(tweets_path, "r"))

    columns = ["name", "text", "country_code", "display_url",
               "lang", "created_at", "location"]

    db = "/Users/ilchenkoslava/Downloads/tweets.db"
    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        main(tweets, columns, cur, conn)
        query = cur.execute("select count(1) from Tweet;").fetchone()
        assert query[0] > 100
    except sqlite3.Error as e:
        print(e)
    finally:
        if(conn):
            cur.close()
            conn.close()
