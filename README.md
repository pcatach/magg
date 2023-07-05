# magg

Metaculus Aggregator

## Description

This package is designed to help users aggregate predictions from Metaculus in a digest format. 
It is currently in beta and has not been tested for robustness.

By default, it sends an email every Wednesday 3:30pm UTC with the top 30 questions in all categories (in terms of activity) published in the last 30 days.

## Installation

Required: `python3.9` and `terraform` (for deployment).

```
$ python3.9 -m venv env
$ ./env/bin/pip install -r requirements.txt
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
```

## Deployment

### Setting up S3

You need to create an S3 bucket to store the database.

### Sending email with SES

To enable email (`--mail`), you need to configure SES. 
You can do this by following the instructions [here](https://docs.aws.amazon.com/ses/latest/dg/send-an-email-using-sdk-programmatically.html).

Fill in `config.json` with the appropriate values.

### Deploying to AWS

Create the packer package with

```
cd deploy
packer build image.pkr.hcl
```

This will output the AMI ID you will input into `main.tf`.
Then deploy to AWS with

```
terraform init
terraform apply
```

### TODO

- [ ] Fine-tune the queries and database operations to get the most relevant questions.