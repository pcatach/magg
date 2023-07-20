import logging
import sqlite3

import boto3

from client.exceptions import BucketNotFound

LOG = logging.getLogger(__name__)
LOCAL_FILE = "/tmp/forecasts.db"


class DatabaseMixin:
    def __init__(self, config):
        self.config = config
        self.db_connection = None
        self.use_s3 = False

        if self.config["database_location"] == "s3":
            self.use_s3 = True
            self.s3_client = boto3.client("s3", region_name=self.config["aws_region"])

    def __enter__(self):
        if self.use_s3:
            try:
                get_database_from_s3(self.s3_client, self.config)
            except BucketNotFound as e:
                LOG.info("No database found in S3, creating a new one")
                create_bucket(self.s3_client, self.config)
            self.db_connection = sqlite3.connect(LOCAL_FILE)
        else:
            self.db_connection = sqlite3.connect(self.config["database_path"])
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db_connection.close()
        if self.use_s3:
            upload_database_to_s3(self.s3_client, self.config)


def get_database_from_s3(s3_client: boto3.client, config):
    try:
        s3_client.download_file(
            config["s3_bucket"], config["database_path"], LOCAL_FILE
        )
    except (s3_client.exceptions.ClientError, s3_client.exceptions.NoSuchKey) as e:
        raise BucketNotFound() from e


def upload_database_to_s3(s3_client: boto3.client, config):
    s3_client.upload_file(
        LOCAL_FILE,
        config["s3_bucket"],
        config["database_path"],
    )


def create_bucket(s3_client: boto3.client, config):
    s3_client.create_bucket(
        Bucket=config["s3_bucket"],
        CreateBucketConfiguration={"LocationConstraint": config["aws_region"]},
    )
