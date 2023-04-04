import datetime
import logging

from api import get_questions_list
from formatting import format_email

logging.basicConfig(level=logging.DEBUG)

categories = ["computing--ai", "bio"]

questions = get_questions_list(
    categories=categories,
    limit=10,
    min_published_time=datetime.datetime.now() - datetime.timedelta(days=15),
    include_descriptions=True,
)

email = format_email(categories, questions)

with open("example.html", "w+") as example_file:
    example_file.write(email)
