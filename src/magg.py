import argparse
import datetime
import json
import logging

import boto3

from client.metaculus import MetaculusClient
from formatting import generate_question_digest
from mailing import send_email


def main(renew, mail, config_path):
    with open(config_path) as config_file:
        config = json.load(config_file)

    with MetaculusClient(config) as client:
        projects = client.get_projects_list()
        projects = [
            project for project in projects if project.name in config["projects"]
        ]
        questions = client.get_questions_per_project(
            projects=projects,
            min_published_time=datetime.datetime.now() - datetime.timedelta(days=30),
            limit_per_project=30,
            renew=renew,
        )

    html = generate_question_digest(questions, projects)

    with open("/tmp/digest.html", "w") as f:
        f.write(html)

    if mail:
        send_email(
            subject="Magg's Metaculus Digest",
            from_address=config["from_address"],
            to_address=config["to_address"],
            html_content=html,
            aws_region=config["aws_region"],
        )


def lambda_handler(event, context):
    client = boto3.client("ssm")
    response = client.get_parameter(Name="config.json", WithDecryption=True)
    with open("/tmp/config.json", "w") as f:
        f.write(response["Parameter"]["Value"])

    main(renew=True, mail=True, config_path="/tmp/config.json")


def cli():
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
        "-c", "--config", help="path to config file", default="config.json"
    )
    parser.add_argument(
        "-v", "--verbose", help="increase output verbosity", action="store_true"
    )
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)
    main(args.renew, args.mail, args.config)


if __name__ == "__main__":
    cli()
