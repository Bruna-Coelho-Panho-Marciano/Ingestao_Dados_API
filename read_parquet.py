import os
import io
import boto3
import pyarrow.parquet as pq
import pyarrow as pa
from dotenv import load_dotenv

load_dotenv()

BUCKET_URL = os.environ.get("MINIO_BUCKET_URL", "s3://currency-raw")

ENDPOINT_URL = os.environ.get("MINIO_ENDPOINT_URL", "http://localhost:9000").replace(
    "minio:","localhost:"
    
)
ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY")
SECRET_KEY = os.environ.get("MINIO_SECRET_ACCESS_KEY")

bucket = BUCKET_URL.removeprefix("s3://")
prefix = "latest/"

s3 = boto3.client(
    "s3",
    endpoint_url=ENDPOINT_URL,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name="us-east-1",
)

paginator = s3.get_paginator("list_objects_v2")
pages = paginator.paginate(Bucket=bucket, Prefix=prefix)

parquet_keys = [
    obj["Key"] 
    for page in pages 
    for obj in page.get("Contents", [])
    if obj["Key"].endswith(".parquet")
]

if not parquet_keys:
    print(f"Nenhum arquivo Parquet encontrado em: s3://{bucket}/{prefix}")

else:
    print(f"Encontrados {len(parquet_keys)} arquivo(s):\n")  
    for key in parquet_keys:  
        print(f" s3://{bucket}/{key}")

    print()

    tables = []
    for key in parquet_keys:
        response = s3.get_object(Bucket=bucket, Key=key)
        buffer = io.BytesIO(response["Body"].read())
        tables.append(pq.read_table(buffer))

    table = pa.concat_tables(tables)
    df = table.to_pandas()
    print(df.to_string(index=False))    
    print(f"\nTotal de linhas: {len(df)}")






