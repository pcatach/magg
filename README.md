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
from api import MetaculusClient
categories = ["computing", "bio"]

config = {
    "metaculus_api_key": None,
    "database_path": "forecast.db",
}
with MetaculusClient(config) as client:
    questions = client.get_questions(
        categories=categories,
        limit=5,
        min_published_time=datetime.datetime.now() - datetime.timedelta(days=60),
        renew=True,
    )

html = generate_question_digest(questions, categories)
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

Create and zip the package with

```
$ pip3.10 install . -t package/
$ cd package
$ zip -r ../magg.zip .
```

Apply the terraform configuration with

```
terraform init
terraform apply
```

### TODO

- [ ] Fine-tune the queries and database operations to get the most relevant questions.