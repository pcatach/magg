import datetime

from api import get_questions_list
from formatting import format_email

category = "computing--ai"

questions = get_questions_list(
    category=category,
    limit=10,
    min_published_time=datetime.datetime.now() - datetime.timedelta(days=7),
)

email = format_email([category], questions)

with open("example.html", "w+") as example_file:
    example_file.write(email)
