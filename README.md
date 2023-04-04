# magg

Metaculus Aggregator

## Description

This package is designed to help users aggregate predictions from Metaculus in a digest format. 
It is currently in beta and has not been tested for robustness.

## Usage

```python
from api import get_questions_list
categories = ["computing--ai", "bio"]

questions = get_questions_list(
    categories=categories,
    limit=10,
    min_published_time=datetime.datetime.now() - datetime.timedelta(days=15),
    include_descriptions=True,
)
```

## TODO

- Restrict questions only to forecasts (exclude tournaments and challenges)
- Convert community predictions to date or number
