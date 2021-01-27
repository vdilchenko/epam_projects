from typing import Union, List

from pyspark.sql import DataFrame, SparkSession


class Deduplicator:
    """
    Current class provides possibilities to remove duplicated rows in data depends on provided primary key.
    If no primary keys were provided should be removed only identical rows.
    """

    # ToDo: Implement this method
    def deduplicate(self, primary_keys: Union[str, List[str]], dataframe: DataFrame) -> DataFrame:
        if len(primary_keys) == 0:
            return dataframe.dropDuplicates()
        else:
            if isinstance(primary_keys, str):
                primary_keys = [primary_keys]
            return dataframe.dropDuplicates(subset=primary_keys)
