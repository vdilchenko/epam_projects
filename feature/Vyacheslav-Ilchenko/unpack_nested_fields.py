from pyspark.sql import DataFrame
from pyspark.sql.functions import explode, col
from pyspark.sql.types import StructType, ArrayType


class UnpackNestedFields:
    """
    Class provides possibilities to unpack nested structures in row recursively and provide flat structure as result.
    To clarify rules, please investigate tests.
    After unpacking of structure additional columns should be provided with next name {struct_name}.{struct_field_name}
    """

    # ToDo implement unpacking of nested fields
    def unpack_nested(self, dataframe: DataFrame):
        def flatten_struct(schema, prefix=""):
            result = []

            for elem in schema:
                if isinstance(elem.dataType, StructType):
                    result += flatten_struct(
                        elem.dataType, prefix + elem.name + '.')
                elif isinstance(elem.dataType, ArrayType):
                    result.append(explode(col(prefix + elem.name)).alias(
                            prefix.replace('.', '_') + elem.name))
                else:
                    if elem.name.startswith('_'):
                        result.append(col(prefix + elem.name).alias(
                            prefix.replace('.', '_') + elem.name))
                    else:
                        result.append(col(prefix + elem.name).alias(
                            prefix + elem.name))
            return result

        flat_df = dataframe.select(flatten_struct(dataframe.schema))
        if flat_df.collect() == dataframe.collect():
            return dataframe
        else:
            return flat_df
