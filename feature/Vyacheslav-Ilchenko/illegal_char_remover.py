from pyspark.sql.dataframe import DataFrame
from pyspark.sql.functions import regexp_replace
from pyspark.sql import SparkSession
from typing import List
import re
import pytest


class IllegalCharRemover:
    """
    Class provides possibilities to remove illegal chars from string column.
    """
    def __init__(self, chars: List[str], replacement):
        if chars:
            self.chars = chars
        else:
            raise ValueError
        if replacement is not None:
            self.replacement = replacement
        else:
            raise ValueError

    def remove_illegal_chars(self, dataframe: DataFrame,
                             source_column: str, target_column: str):

        remove_str = ''
        for char in self.chars:
            if re.match('[A-Za-z0-9]', char) is not None:
                remove_str = remove_str + char
            else:
                remove_str = remove_str + '\\' + char
        df = dataframe.withColumn(target_column, regexp_replace(source_column,
                                  '[' + remove_str + ']', self.replacement))\
                      .drop('string')
        return df
