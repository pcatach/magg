import argparse
import datetime
import json
import logging

from api import get_questions
from formatting import generate_question_digest
from mailing import send_email

logging.basicConfig(level=logging.DEBUG)


def main(renew, mail, config_path, mail_from, mail_to):
    with open(config_path) as config_file:
        config = json.load(config_file)

    questions = get_questions(
        categories=config["categories"],
        min_published_time=datetime.datetime.now() - datetime.timedelta(days=30),
        limit=30,
        renew=renew,
    )

    html = generate_question_digest(questions, config["categories"])

    with open("~/digest.html", "w") as f:
        f.write(html)

    if mail:
        send_email(
            subject="Magg's Metaculus Digest",
            from_address=mail_from or config["from_address"],
            to_address=mail_to or config["to_address"],
            html_content=html,
            aws_region=config["aws_region"],
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
parser.add_argument(
    "-c", "--config", help="path to config file", default="/config.json"
)
parser.add_argument(
    "--mail-from",
    help="email address to send from",
    dest=None,
)
parser.add_argument(
    "--mail-to",
    help="email address to send to",
    dest=None,
)
args = parser.parse_args()
main(args.renew, args.mail, args.config, args.mail_from, args.mail_to)
