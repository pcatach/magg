import datetime
import logging
import sqlite3

import boto3
import requests

from .models import Question, BASE_URL, LIMIT_PER_CATEGORY

LOG = logging.getLogger(__name__)


class MetaculusClient:
    def __init__(self, config):
        self.session = requests.Session()
        self.config = config
        self.db_connection = None
        self.s3_client = None

        if config["metaculus_api_key"] is not None:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Token {config['metaculus_api_key']}",
            }
            self.session.headers.update(headers)

    def __enter__(self):
        if self.config["database_location"] == "filesystem":
            self.db_connection = sqlite3.connect(self.config["database_path"])
        elif self.config["database_location"] == "s3":
            self.s3_client = boto3.client("s3")
            try:
                self.s3_client.download_file(
                    self.config["s3_bucket"],
                    self.config["database_path"],
                    "/tmp/forecasts.db",
                )
            except self.s3_client.exceptions.NoSuchKey:
                LOG.info("No database found in S3, creating a new one")
        else:
            raise ValueError(f"Unknown database type: {self.config['database']}")

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db_connection.close()
        if self.config["database_location"] == "s3":
            self.s3_client.upload_file(
                "/tmp/forecasts.db",
                self.config["s3_bucket"],
                self.config["database_path"],
            )

    def get_categories_list(self, limit: int = None):
        next_url = f"{BASE_URL}/api2/categories/"
        categories = []

        while next_url:
            LOG.debug(f"Fetching categories from {next_url}")
            response = self.session.get(next_url)
            data = response.json()
            next_url = data["next"]

            categories.extend([category["id"] for category in data["results"]])
            if limit is not None and len(categories) >= limit:
                break

        return categories

    def get_questions(
        self,
        *,
        categories: list[str],
        limit: int,
        min_published_time: datetime.datetime | None = None,
        renew: bool = False,
    ):
        if not renew:
            return Question.load_from_db(self.db_connection)

        questions = []
        for category in categories:
            next_url = f"{BASE_URL}/api2/questions/?order_by=-activity&type=forecast"
            next_url += f"&categories={category}"

            if min_published_time is not None:
                next_url = (
                    f"{next_url}&publish_time__gt={min_published_time.isoformat()}"
                )
                next_url = (
                    f"{next_url}&publish_time__lt={datetime.datetime.now().isoformat()}"
                )

            while next_url:
                LOG.debug(f"Fetching questions from {next_url}")
                response = self.session.get(next_url)
                data = response.json()
                next_url = data["next"]

                questions.extend(
                    [
                        Question.from_api_response(
                            question,
                            category=category,
                            db_connection=self.db_connection,
                        )
                        for question in data["results"]
                    ]
                )

                if len(questions) >= LIMIT_PER_CATEGORY:
                    break

        questions = sorted(questions, key=lambda q: q.activity, reverse=True)[:limit]

        return questions
