from dataclasses import dataclass
import datetime

BASE_URL = "https://metaculus.com"
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


def sanitize_datetime(datetime_string: str) -> datetime.datetime:
    return datetime.datetime.strptime(
        datetime_string.split(".")[0].rstrip("Z"), DATETIME_FORMAT
    )


@dataclass
class Question:
    id: int
    page_url: str
    author_name: str
    title: str
    created_time: datetime.datetime
    publish_time: datetime.datetime
    close_time: datetime.datetime
    resolve_time: datetime.datetime
    active_state: str
    number_of_predictions: int
    community_prediction: str | None = None
    community_prediction_measure: str | None = None
    category: str | None = None
    description: str | None = None

    @classmethod
    def from_api_response(cls, question_dict, category=None):
        community_prediction, measure = cls.get_community_prediction(question_dict)
        return cls(
            id=question_dict["id"],
            page_url=f"{BASE_URL}{question_dict['page_url']}",
            author_name=question_dict["author_name"],
            title=question_dict["title"],
            created_time=sanitize_datetime(question_dict["created_time"]),
            publish_time=sanitize_datetime(question_dict["publish_time"]),
            close_time=sanitize_datetime(question_dict["close_time"]),
            resolve_time=sanitize_datetime(question_dict["resolve_time"]),
            active_state=question_dict["active_state"],
            number_of_predictions=question_dict["number_of_predictions"],
            community_prediction=community_prediction,
            community_prediction_measure=measure,
            category=category,
            description=question_dict.get("description"),
        )

    @classmethod
    def get_community_prediction(cls, question_dict):
        if (
            question_dict.get("prediction_timeseries") is None
            or question_dict["prediction_timeseries"] == []
        ):
            return None, None

        latest_prediction = question_dict["prediction_timeseries"][-1][
            "community_prediction"
        ]
        if type(latest_prediction) == float:
            return latest_prediction, None
        if "avg" in latest_prediction:
            return latest_prediction["avg"], "avg"
        elif "q2" in latest_prediction:
            return latest_prediction["q2"], "median"
        else:
            return None, None
