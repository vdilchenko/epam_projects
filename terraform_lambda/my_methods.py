import pandas as pd
from io import StringIO
from sqlalchemy import create_engine


def read_csv_from_s3(s3, bucket_name, filename):
    """
        Reads CSV from S3 Bucket.
    """
    csv_obj = s3.get_object(Bucket=bucket_name, Key=f'folder1/{filename}')
    body = csv_obj['Body']
    csv_string = body.read().decode('utf-8')
    df = pd.read_csv(StringIO(csv_string), sep=';')

    return df


def filter_df(df):
    """
        Filters given DataFrame.
    """
    df = df[df.value_rub > 10]
    return df


def write_df_to_s3(s3, bucket_name, df, name):
    """
        Writes given DataFrame to S3 bucket.
    """
    name = name.replace('.csv', '')
    filename = f'filtered {name}.parquet'
    df_csv = df.to_parquet()
    s3.put_object(
        Body=df_csv, Bucket=bucket_name, Key=f'folder2/{filename}')

    return f'Saved {filename} on S3'


def write_df_to_db(df, db_instance, user, password, db_name):
    """
        Writes given DataFrame to AWS RDS.
    """
    host = db_instance['Address']
    port = db_instance['Port']

    mydb = create_engine(f'postgres://{user}:{password}@{host}:{port}/{db_name}',
                         echo=False)
    df.to_sql('bank_table', mydb, if_exists='replace', index=False)

    return pd.read_sql('select count(*) from bank_table;', mydb)
