import datetime
import logging

import requests

from client.exceptions import MetaculusAPIError
from client.mixins import DatabaseMixin
from models import Question, BASE_URL, LIMIT_PER_CATEGORY

LOG = logging.getLogger(__name__)


class MetaculusClient(DatabaseMixin):
    def __init__(self, config):
        super().__init__(config)
        self.session = requests.Session()

        if config["metaculus_api_key"] is not None:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Token {config['metaculus_api_key']}",
            }
            self.session.headers.update(headers)

    def get_categories_list(self, limit: int = None):
        next_url = f"{BASE_URL}/api2/categories/"
        categories = []

        while next_url:
            LOG.info(f"Fetching categories from {next_url}")
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
                LOG.info(f"Fetching questions from {next_url}")
                response = self.session.get(next_url)
                data = response.json()
                if "results" not in data:
                    LOG.error(f"Error fetching questions: {data}")
                    raise MetaculusAPIError(data.get("detail", "unknown"))
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
