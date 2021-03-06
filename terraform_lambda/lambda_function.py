import my_methods
import boto3
import logging
import os

if logging.getLogger().hasHandlers():
    logging.getLogger().setLevel(logging.INFO)
else:
    logging.basicConfig(level=logging.INFO)


def lambda_handler(event, context):
    s3 = boto3.client('s3')
    rds = boto3.client('rds')

    bucket_name = os.environ['bucket_name']
    db_instance_name = os.environ['db_instance']
    filename = 'bank_test.csv'
    db_user = os.environ['db_username']
    db_password = os.environ['db_password']
    db_name = os.environ['db_name']

    db_instance = rds.describe_db_instances(
        DBInstanceIdentifier=db_instance_name)['DBInstances'][0]['Endpoint']

    bucket_files = [bucket['Key'] for bucket in s3.list_objects(
        Bucket=bucket_name)['Contents']]

    try:
        filename = event['Records'][0]['s3']['object']['key']\
            .replace('folder1/', '')
    except KeyError:
        logging.info(
            f'Lambda started not from trigger, reading CSV from {bucket_name}')
        if f'folder1/{filename}' in bucket_files:
            logging.info(f'{filename} exists.')
        else:
            logging.error(f'{filename} doesn''t exist in folder1!')
            raise Exception('Add CSV file to folder1!')

    df1 = my_methods.read_csv_from_s3(s3, bucket_name,
                                      filename=filename)
    assert df1.shape[0] == 9, 'method read_csv_from_s3 is not working as intended'
    logging.info('Just read file from S3.')

    df2 = my_methods.filter_df(df1)
    assert df2.shape[0] == 3, 'method filter_df is not working as intended'
    logging.info('Just filtered DataFrame.')

    write_func = my_methods.write_df_to_s3(s3, bucket_name, df2, filename)
    new_name = filename.replace('.csv', '')
    logging.info(write_func)
    bucket_files = [bucket['Key'] for bucket in s3.list_objects(
        Bucket=bucket_name)['Contents']]
    assert f'folder2/filtered {new_name}.parquet' in bucket_files, 'method write_df_to_s3 is not working as intended'

    query = my_methods.write_df_to_db(df1, db_instance,
                                      db_user, db_password, db_name)
    assert query['count'][0] == 9, 'method write_df_to_db is not working as intended'
    logging.info('Just wrote data to database.')

    return logging.info('Everything worked!')
