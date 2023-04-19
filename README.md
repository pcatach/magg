# magg

Metaculus Aggregator

## Description

This package is designed to help users aggregate predictions from Metaculus in a digest format. 
It is currently in beta and has not been tested for robustness.

## Installation

Required: `python3.10`.

```
$ python3.10 -m venv env
$ ./env/bin/pip install -r requirements.in
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