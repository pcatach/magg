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
    metacalculus_prediction: float
    category: str | None = None
    description: str | None = None

    @classmethod
    def from_api_response(cls, question_dict, category=None):
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
            metacalculus_prediction=question_dict["metaculus_prediction"]["full"],
            category=category,
            description=question_dict.get("description"),
        )
