# magg

Metaculus Aggregator

## Description

This package is designed to help users aggregate predictions from Metaculus in a digest format. 
It is currently in beta and has not been tested for robustness.

By default, it sends an email every Wednesday 3:00pm UTC with the top 30 questions in all categories (in terms of activity) published in the last 30 days.

## Installation

Required: `python3.10` and `terraform` (for deployment).

```
$ python3.10 -m venv env
$ ./env/bin/pip install -r requirements.txt
```

Or to install the package in editable mode:

```
$ ./env/bin/pip install -e .
```

## Usage

```python
import datetime
from magg import MetaculusClient, generate_question_digest

config = {
    "metaculus_api_key": None,
    "database_location": "filesystem",
    "database_path": "forecasts.db"
}

client = MetaculusClient(config)
client.connect()

categories = client.get_categories_list()
questions_per_category = client.get_questions_per_category(
    limit_per_category=5,
    categories = categories[:2],
    min_published_time=datetime.datetime.now() - datetime.timedelta(days=60),
    renew=True,
)

projects = client.get_projects_list()
projects = [project for project in projects if "Quarterly Cup" in project.name]
questions_per_project = client.get_questions_per_project(
    limit_per_project=5,
    projects = projects,
    min_published_time=datetime.datetime.now() - datetime.timedelta(days=60),
    renew=True,
)

client.disconnect()

html = generate_question_digest(questions_per_project, projects)
```

or using the command line:

```
$ ./env/bin/python -m src.magg --renew --mail
$ # or, if installed in editable mode
$ ./env/bin/magg --renew --mail
```

## Deployment

### Setting up S3

You need to create an S3 bucket to store the database.

### Sending email with SES

To enable email (`--mail`), you need to configure SES. 
You can do this by following the instructions [here](https://docs.aws.amazon.com/ses/latest/dg/send-an-email-using-sdk-programmatically.html).

Fill in `config.json` with the appropriate values.

### Deploying to AWS Lambda

```
cd deploy/
./build.sh
terraform init
terraform apply
```

### TODO

- [ ] Fine-tune the queries and database operations to get the most relevant questions.
- [ ] Bug: if a question belongs to multiple categories, it will be counted multiple times.
- [ ] Bug: get_questions_per_project() doesn't assign categories to questions.
- [ ] Bug: limit_per_category and limit_per_project are not enforced really because the paginated calls always return a minimum of 10 questions