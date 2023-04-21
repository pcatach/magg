import argparse
import datetime
import json
import logging

from api import get_questions
from formatting import generate_question_digest
from mailing import send_email

logging.basicConfig(level=logging.DEBUG)

with open("config.json") as config_file:
    config = json.load(config_file)


def main(renew, mail):
    categories = [
        "bio",
        "business",
        # "category",
        # "comp-sci",
        # "computing",
        # "economy",
        # "environment",
        # "finance",
        # "geopolitics",
        # "human-sci",
        # "industry",
        # "infrastructure",
        # "law",
        # "math",
        # "patents",
        # "phys-sci",
        # "plantbased",
        # "social",
        # "tech",
        # "ukraine",
    ]

    questions = get_questions(
        categories=categories,
        min_published_time=datetime.datetime.now() - datetime.timedelta(days=60),
        renew=renew,
    )

    html = generate_question_digest(questions, categories)

    with open("digest.html", "w") as f:
        f.write(html)

    if mail:
        send_email(
            subject="Magg's Metaculus Digest",
            from_address=config["from_address"],
            to_address=config["to_address"],
            html_content=html,
            password=config["password"],
        )


# use argparse to parse command line arguments
parser = argparse.ArgumentParser(description="Magg's Metaculus Digest")
parser.add_argument(
    "-r",
    "--renew",
    help="renew questions from Metaculus API",
    action="store_true",
)
parser.add_argument(
    "-m",
    "--mail",
    help="send email",
    action="store_true",
)
args = parser.parse_args()
main(args.renew, args.mail)
