import argparse
import datetime
import json
import logging

from .client.metaculus import MetaculusClient
from .formatting import generate_question_digest
from .mailing import send_email

def main(renew, mail, config_path):
    with open(config_path) as config_file:
        config = json.load(config_file)

    with MetaculusClient(config) as client:
        questions = client.get_questions(
            categories=config["categories"],
            min_published_time=datetime.datetime.now() - datetime.timedelta(days=30),
            limit=30,
            renew=renew,
        )

    html = generate_question_digest(questions, config["categories"])

    with open("digest.html", "w") as f:
        f.write(html)

    if mail:
        send_email(
            subject="Magg's Metaculus Digest",
            from_address=config["from_address"],
            to_address=config["to_address"],
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
parser.add_argument("-c", "--config", help="path to config file", default="config.json")
parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
args = parser.parse_args()
logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)
main(args.renew, args.mail, args.config)
