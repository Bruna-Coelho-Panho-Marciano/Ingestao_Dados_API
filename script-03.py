import os
import dlt
from dotenv import load_dotenv
from dlt.destinations import filesystem
from ingestion.source import freecurrency_source

if __name__ == "__main__":
    load_dotenv()

    endpoint_url = os.environ.get("MINIO_ENDPOINT_URL", "http://localhost:9000")

    destination = filesystem(
        bucket_url=os.environ.get("MINIO_BUCKET_URL", "s3://latest"),
        credentials={
            "aws_access_key_id": os.environ.get("MINIO_ACCESS_KEY"),
            "aws_secret_access_key": os.environ.get("MINIO_SECRET_ACCESS_KEY"),
            "endpoint_url": endpoint_url,
            "region_name": "us-east-1",
            "s3_url_style": "path",
        },
    )

    pipeline = dlt.pipeline(
        pipeline_name="freecurrency_pipeline",
        destination=destination,
        dataset_name="latest",
    )
    
    api_key = os.environ["API_KEY"]
    
    load_info = pipeline.run(freecurrency_source(api_key=api_key), loader_file_format="parquet" )
    print(load_info)
    