# magg

Metaculus Aggregator

## Description

This package is designed to help users aggregate predictions from Metaculus in a digest format. 
It is currently in beta and has not been tested for robustness.

## Installation

Required: `python3.9` and `docker` (for deployment).

```
$ python3.9 -m venv env
$ ./env/bin/pip install -r requirements.txt
```

## Usage

```python
from api import get_questions
categories = ["computing", "bio"]

questions = get_questions(
    categories=categories,
    min_published_time=datetime.datetime.now() - datetime.timedelta(days=60),
    renew=renew,
)

html = generate_question_digest(questions, categories)
```

or using the command line:

```
$ ./env/bin/python src/magg.py --renew --mail
```

## Deployment

Create the python package with

```
./env/bin/python -m build --outdir deploy/
```

Then deploy to ec2 with

```
cd deploy
terraform init
terraform apply
```

### Making email work

To enable email (`--mail`), you need to configure SES. 
You can do this by following the instructions [here](https://docs.aws.amazon.com/ses/latest/dg/send-an-email-using-sdk-programmatically.html).

Fill in `config.json` with the appropriate values.