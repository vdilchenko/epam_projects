from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import lit, col, when, udf, unix_timestamp
from pyspark.sql.types import StructType, StructField, StringType, DateType, ArrayType, TimestampType, IntegerType, \
    BooleanType, LongType, DoubleType, DecimalType, Row
from datetime import datetime
from pytz import timezone


PI_STRING = "3.141592653589793238462643383279502884197169399375105820974944592307816406286208998628034825" \
            "342117067982148086513282306647093844609550582231725359408128481117450284102701938521105559" \
            "644622948954930381964428810975665933446128475648233786783165271201909145648566923460348610" \
            "454326648213393607260249141273724587006606315588174881520920962829254091715364367892590360" \
            "011330530548820466521384146951941511609433057270365759591953092186117381932611793105118548" \
            "074462379962749567351885752724891227938183011949129833673362440656643086021394946395224737" \
            "190702179860943702770539217176293176752384674818467669405132000568127145263560827785771342" \
            "757789609173637178721468440901224953430146549585371050792279689258923542019956112129021960" \
            "864034418159813629774771309960518707211349999998372978049951059731732816096318595024459455" \
            "346908302642522308253344685035261931188171010003137838752886587533208381420617177669147303" \
            "598253490428755468731159562863882353787593751957781857780532171226806613001927876611195909" \
            "2164201989"


class StringTypeTransformer:
    """
    Class provides transformation for columns with string types to other, where it possible.
    """

    def transform_dataframe(self, dataframe: DataFrame, expected_schema: StructType):
        for field in expected_schema:
            to_datetime = udf(lambda x: datetime.strptime(x, '%d-%m-%Y').date() if x is not None else x, DateType())
            to_ts = udf(lambda x: timezone('Europe/Moscow')
                        .localize(datetime.strptime(x, '%d-%m-%Y %H:%M:%S'))
                        .isoformat() if x is not None else x, StringType())
            name = field.name
            dtype = field.dataType
            nullable = field.nullable
            if isinstance(dtype, DateType):
                dataframe = dataframe\
                    .withColumn(name, to_datetime(col(name)))
            elif isinstance(dtype, TimestampType):
                dataframe = dataframe\
                    .withColumn(name, to_ts(col(name)))
            elif nullable is False:
                dataframe = dataframe.withColumn(name, when(
                    col(name).isin(['true', 'True']), True).otherwise(False))
            dataframe = dataframe.withColumn(name, col(name).cast(dtype))
        return dataframe
