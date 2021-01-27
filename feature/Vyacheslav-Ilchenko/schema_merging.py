from pyspark.sql import DataFrame, SparkSession, Row
from pyspark.sql.functions import lit


class SchemaMerging:
    """
    Class provides possibilities to union tow datasets with different schemas.
    Result dataset should contain all rows from both with columns from both dataset.
    If columns have the same name and type - they are identical.
    If columns have different types and the same name, 2 new column should be provided with next pattern:
    {field_name}_{field_type}
    """

    # ToDo: Implement dataset union with schema merging
    def union(self, dataframe1: DataFrame, dataframe2: DataFrame):
        df_left = dataframe1
        df_right = dataframe2
        left_types = {f.name: f.dataType for f in df_left.schema}
        right_types = {f.name: f.dataType for f in df_right.schema}
        left_fields = set((f.name, f.dataType, f.nullable) for f in df_left.schema)
        right_fields = set((f.name, f.dataType, f.nullable) for f in df_right.schema)

        for l_name, l_type, l_nullable in left_fields.difference(right_fields):
            if l_name in right_types:
                r_type = right_types[l_name]
                if l_type != r_type:
                    df_left = df_left.withColumnRenamed(l_name, l_name + '_' + l_type.simpleString())
    
        for r_name, r_type, r_nullable in right_fields.difference(left_fields):
            if r_name in left_types:
                l_type = left_types[r_name]
                if r_type != l_type:
                    df_right = df_right.withColumnRenamed(r_name, r_name + '_' + r_type.simpleString())

        cols1 = df_left.columns
        cols2 = df_right.columns
        total_cols = cols1 + list(set(cols2) - set(cols1))
        len_cols = len(total_cols)

        def expr(mycols, allcols, left=True):
            def processCols(colname):
                if colname in mycols:
                    return colname
                else:
                    return lit(None).alias(colname)
            cols = map(processCols, allcols)
            if left:
                return mycols + list(cols)[len(mycols):]
            else:
                if len_cols == (len(cols1) + len(cols2)):
                    return list(cols)[:-len(mycols)] + mycols
                else:
                    return list(cols)
        appended = df_left.select(expr(cols1, total_cols)).union(df_right.select(expr(cols2, total_cols, left=False)))
        return appended
