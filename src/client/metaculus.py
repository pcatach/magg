import datetime
import logging

import requests

from client.exceptions import MetaculusAPIError
from client.mixins import DatabaseMixin
from models import Category, Question, BASE_URL

LOG = logging.getLogger(__name__)
LIMIT = 60  # should be a multiple of 20, which is the default pagination limit


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

    def get_categories_list(self, limit: int = None) -> list[Category]:
        url = f"{BASE_URL}/api2/categories/"
        categories_dicts = self.get_paginated_results(url, limit)
        categories = [
            Category.from_api_response(
                category_dict=category_dict,
                db_connection=self.db_connection,
            )
            for category_dict in categories_dicts
        ]
        return categories

    def get_projects_list(self, limit: int = None):
        url = f"{BASE_URL}/api2/projects/"
        return self.get_paginated_results(url, limit)

    def get_questions_per_category(
        self,
        *,
        categories: list[Category],
        limit_per_category: int,
        min_published_time: datetime.datetime | None = None,
        renew: bool = False,
    ) -> list[Question]:
        if not renew:
            return Question.load_from_db(self.db_connection)

        url = f"{BASE_URL}/api2/questions/?order_by=-activity&type=forecast"
        if min_published_time is not None:
            url = f"{url}&publish_time__gt={min_published_time.isoformat()}"
            url = f"{url}&publish_time__lt={datetime.datetime.now().isoformat()}"

        questions = []
        for category in categories:
            url_with_category = url + f"&categories={category.id}"

            questions_dicts = self.get_paginated_results(
                url_with_category, limit=limit_per_category
            )

            questions.extend(
                [
                    Question.from_api_response(
                        question,
                        db_connection=self.db_connection,
                        category=category,
                    )
                    for question in questions_dicts
                ]
            )

        questions = sorted(questions, key=lambda q: q.activity, reverse=True)

        return questions

    def get_paginated_results(self, url: str, limit: int = None) -> list[dict]:
        results = []

        while url:
            LOG.info(f"Fetching results from {url}")
            response = self.session.get(url)
            data = response.json()
            if "results" not in data:
                LOG.error(f"Error fetching questions: {data}")
                raise MetaculusAPIError(data.get("detail", "unknown"))

            url = data["next"]

            results.extend(data["results"])
            if limit is not None and len(results) >= limit:
                break

        return results
