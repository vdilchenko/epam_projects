from pyspark.sql import DataFrame, SparkSession, Row
from pyspark.sql.functions import col, lit


class HistoryProduct:
    """
    Class provides possibilities to compute history of rows.
    You should compare old and new dataset and define next for each row:
     - row was changed
     - row was inserted
     - row was deleted
     - row not changed
     Result should contain all rows from both datasets and new column `meta`
     where status of each row should be provided ('not_changed', 'changed', 'inserted', 'deleted')
    """
    def __init__(self, primary_keys=None):
        self.primary_keys = primary_keys

    # ToDo: Implement history product
    def get_history_product(self, old_dataframe: DataFrame,
                            new_dataframe: DataFrame):

        if self.primary_keys is not None:
            not_changed_df = old_dataframe.intersect(new_dataframe)\
                .withColumn('meta', lit('not_changed'))

            changed_df = new_dataframe.join(old_dataframe, on=self.primary_keys)\
                                    .filter((new_dataframe.name != old_dataframe.name) | 
                                            (new_dataframe.score != old_dataframe.score) |
                                            (new_dataframe.score.isNull() != old_dataframe.score.isNull()))\
                                    .drop(old_dataframe.id)\
                                    .drop(old_dataframe.name)\
                                    .drop(old_dataframe.score)\
                                    .withColumn('meta', lit('changed'))
            inserted_df = new_dataframe.join(old_dataframe, how='leftanti',
                                            on=self.primary_keys).withColumn(
                                                    'meta', lit('inserted'))
            deleted_df = old_dataframe.join(new_dataframe, how='leftanti',
                                            on=self.primary_keys).withColumn(
                                                    'meta', lit('deleted'))
            
            df = not_changed_df.union(changed_df).union(inserted_df)\
                .union(deleted_df)\
                .orderBy(['id', 'meta'])
        else:
            not_changed_df = old_dataframe.intersect(new_dataframe)\
                .withColumn('meta', lit('not_changed'))
            changed_df = old_dataframe.join(new_dataframe, on=self.primary_keys)\
                                    .filter((old_dataframe.name != new_dataframe.name) | 
                                            (old_dataframe.score != new_dataframe.score) |
                                            (old_dataframe.score.isNull() != new_dataframe.score.isNull()))\
                                    .drop(new_dataframe.id)\
                                    .drop(new_dataframe.name)\
                                    .drop(new_dataframe.score)\
                                    .withColumn('meta', lit('changed'))
            inserted_df = new_dataframe.subtract(old_dataframe)\
                .withColumn('meta', lit('inserted'))
            deleted_df = old_dataframe.subtract(new_dataframe)\
                .withColumn('meta', lit('deleted'))

            df = not_changed_df.union(inserted_df).union(deleted_df)\
                .orderBy(['id', 'meta'])

        return df
