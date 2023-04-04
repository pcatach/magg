import datetime
import logging

import requests

from models import Question, BASE_URL

LOG = logging.getLogger(__name__)


def get_categories_list(limit: int = None):
    next_url = f"{BASE_URL}/api2/categories/"
    categories = []

    while next_url:
        LOG.debug(f"Fetching categories from {next_url}")
        response = requests.get(next_url)
        data = response.json()
        next_url = data["next"]

        categories.extend([category["id"] for category in data["results"]])
        if limit is not None and len(categories) >= limit:
            break

    return categories


def get_questions_list(
    *,
    categories: list[str],
    min_published_time: datetime.datetime | None = None,
    limit: int = None,
    include_descriptions: bool = False,
):
    next_url = (
        f"{BASE_URL}/api2/questions/?include_description=true&order_by=created_time"
    )
    for category in categories:
        next_url += f"&categories={category}"
    if min_published_time is not None:
        next_url = f"{next_url}&publish_time__gt={min_published_time.isoformat()}"
        next_url = f"{next_url}&publish_time__lt={datetime.datetime.now().isoformat()}"
    questions = []

    while next_url:
        LOG.debug(f"Fetching questions from {next_url}")
        response = requests.get(next_url)
        data = response.json()
        next_url = data["next"]

        if include_descriptions:
            for question in data["results"]:
                question_url = f"{BASE_URL}/api2/questions/{question['id']}/"
                question_response = requests.get(question_url)
                question_data = question_response.json()
                question["description"] = question_data["description_html"]

        questions.extend(
            [
                Question.from_api_response(question, category=category)
                for question in data["results"]
            ]
        )
        if limit is not None and len(questions) >= limit:
            break

    return questions
