import datetime

import requests

from models import Question, BASE_URL


def get_categories_list(limit: int = None):
    next_url = f"{BASE_URL}/api2/categories/"
    categories = []

    while next_url:
        response = requests.get(next_url)
        data = response.json()
        next_url = data["next"]
        categories.extend([category["id"] for category in data["results"]])
        if limit is not None and len(categories) >= limit:
            break

    return categories


def get_questions_list(
    *,
    category: str,
    min_published_time: datetime.datetime | None = None,
    limit: int = None,
):
    next_url = (
        f"{BASE_URL}/api2/questions/?categories={category}"
        "&include_description=true&order_by=created_time"
    )
    if min_published_time is not None:
        next_url = f"{next_url}&publish_time__gt={min_published_time.isoformat()}"
    questions = []

    while next_url:
        response = requests.get(next_url)
        data = response.json()
        next_url = data["next"]
        questions.extend(
            [
                Question.from_api_response(question, category=category)
                for question in data["results"]
            ]
        )
        if limit is not None and len(questions) >= limit:
            break

    return questions
