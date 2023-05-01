from dataclasses import dataclass
import datetime
import math
import sqlite3

BASE_URL = "https://www.metaculus.com"
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
LIMIT_PER_CATEGORY = (
    60  # should be a multiple of 20, which is the default pagination limit
)


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
    activity: float
    community_prediction: str | None = None
    community_prediction_statistic: str | None = None
    category: str | None = None

    @classmethod
    def from_api_response(
        cls, question_dict, category=None, database_path="forecasts.db"
    ):
        community_prediction, statistic = cls.get_community_prediction(question_dict)
        question = cls(
            id=question_dict["id"],
            page_url=f"{BASE_URL}{question_dict['page_url']}",
            author_name=question_dict["author_name"],
            title=question_dict["title"],
            created_time=sanitize_datetime(question_dict["created_time"]),
            publish_time=sanitize_datetime(question_dict["publish_time"]),
            close_time=sanitize_datetime(question_dict["close_time"]),
            resolve_time=sanitize_datetime(question_dict["resolve_time"]),
            active_state=question_dict["active_state"],
            activity=question_dict["activity"],
            number_of_predictions=question_dict["number_of_predictions"],
            community_prediction=community_prediction,
            community_prediction_statistic=statistic,
            category=category,
        )
        question.save_to_db(database_path)
        return question

    def save_to_db(self, path="forecasts.db"):
        # Set up the database connection
        with sqlite3.connect(path) as connection:
            c = connection.cursor()

            # Create the forecasts table if it does not already exist
            c.execute(
                """CREATE TABLE IF NOT EXISTS forecasts (
                    id INTEGER PRIMARY KEY,
                    page_url TEXT,
                    author_name TEXT,
                    title TEXT,
                    created_time TIMESTAMP,
                    publish_time TIMESTAMP,
                    close_time TIMESTAMP,
                    resolve_time TIMESTAMP,
                    active_state TEXT,
                    number_of_predictions INTEGER,
                    activity FLOAT,
                    community_prediction FLOAT,
                    community_prediction_statistic TEXT,
                    category TEXT
                )"""
            )

            c.execute(
                """INSERT OR REPLACE INTO forecasts (
                    id, 
                    page_url, 
                    author_name, 
                    title, 
                    created_time, 
                    publish_time, 
                    close_time, 
                    resolve_time, 
                    active_state, 
                    number_of_predictions, 
                    activity, 
                    community_prediction, 
                    community_prediction_statistic, 
                    category) 
                    VALUES 
                    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    self.id,
                    self.page_url,
                    self.author_name,
                    self.title,
                    self.created_time,
                    self.publish_time,
                    self.close_time,
                    self.resolve_time,
                    self.active_state,
                    self.number_of_predictions,
                    self.activity,
                    self.community_prediction,
                    self.community_prediction_statistic,
                    self.category,
                ),
            )

    @classmethod
    def load_from_db(cls, path="forecasts.db"):
        with sqlite3.connect(path) as connection:
            c = connection.cursor()

            c.execute("SELECT * FROM forecasts")
            results = c.fetchall()

            return [cls(*result) for result in results]

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

        probability = None
        statistic = None

        if type(latest_prediction) == float:
            probability = latest_prediction
            statistic = None
        elif "avg" in latest_prediction:
            probability = latest_prediction["avg"]
            statistic = "avg"
        elif "q2" in latest_prediction:
            probability = latest_prediction["q2"]
            statistic = "median"

        prediction_type = question_dict["possibilities"]["type"]

        if prediction_type == "continuous":
            prediction_format = question_dict["possibilities"]["format"]
            prediction_scale = question_dict["possibilities"]["scale"]
            if prediction_format == "date":
                return (
                    cls.format_date_prediction(
                        float(probability),
                        min=prediction_scale["min"],
                        max=prediction_scale["max"],
                    ),
                    statistic,
                )
            elif prediction_format == "num":
                return (
                    cls.format_num_prediction(
                        float(probability),
                        min=float(prediction_scale["min"]),
                        max=float(prediction_scale["max"]),
                    ),
                    statistic,
                )

        return probability, statistic

    @classmethod
    def format_date_prediction(cls, probability, min, max):
        min = datetime.datetime.strptime(min, "%Y-%m-%d")
        max = datetime.datetime.strptime(max, "%Y-%m-%d")
        date_range = max - min
        date_prediction = min + date_range * probability
        return date_prediction.strftime("%Y-%m-%d")

    @classmethod
    def format_num_prediction(cls, probability, min, max):
        if min > 0:
            log_range = math.log10(max) - math.log10(min)
            log_prob = math.log10(min) + log_range * probability
        else:
            log_range = math.log10(max)
            log_prob = log_range * probability
        return 10**log_prob
