from dataclasses import dataclass
import datetime

BASE_URL = "https://metacalculus.com"
DATETIME_FORMAT_1 = "%Y-%m-%dT%H: %M: %S.%fZ"
DATETIME_FORMAT_2 = "%Y-%m-%dT%H: %M: %SZ"


@dataclass
class Question:
    id: int
    page_url: str
    author_name: str
    title: str
    description: str
    created_time: datetime.datetime
    publish_time: datetime.datetime
    close_time: datetime.datetime
    resolve_time: datetime.datetime
    active_state: str
    number_of_predictions: int
    metacalculus_prediction: float
    category: str | None = None

    @classmethod
    def from_api_response(cls, question_dict, category=None):
        return cls(
            id=question_dict["id"],
            page_url=f"{BASE_URL}/{question_dict['page_url']}",
            author_name=question_dict["author_name"],
            title=question_dict["title"],
            description=question_dict["description"],
            created_time=datetime.datetime.strptime(
                question_dict["created_time"], DATETIME_FORMAT_1
            ),
            publish_time=datetime.datetime.strptime(
                question_dict["publish_time"], DATETIME_FORMAT_2
            ),
            close_time=datetime.datetime.strptime(
                question_dict["close_time"], DATETIME_FORMAT_2
            ),
            resolve_time=datetime.datetime.strptime(
                question_dict["resolve_time"], DATETIME_FORMAT_1
            ),
            active_state=question_dict["active_state"],
            number_of_predictions=question_dict["number_of_predictions"],
            metacalculus_prediction=question_dict["metaculus_prediction"]["full"],
            category=category,
        )
