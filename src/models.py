from dataclasses import dataclass
import datetime
import math

BASE_URL = "https://www.metaculus.com"
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


def sanitize_datetime(datetime_string: str) -> datetime.datetime:
    return datetime.datetime.strptime(
        datetime_string.split(".")[0].rstrip("Z"), DATETIME_FORMAT
    )


@dataclass
class Project:
    id: int
    name: str
    subtitle: str
    description: str
    type: str
    tournament_close_date: datetime.datetime | None

    @classmethod
    def from_api_response(cls, project_dict: dict, db_connection) -> "Project":
        close_date = None
        if project_dict["tournament_close_date"] is not None:
            close_date = sanitize_datetime(project_dict["tournament_close_date"])

        project = cls(
            id=project_dict["id"],
            name=project_dict["name"],
            subtitle=project_dict["subtitle"],
            description=project_dict["description"],
            type=project_dict["type"],
            tournament_close_date=close_date,
        )
        project.save_to_db(db_connection)
        return project

    def save_to_db(self, db_connection) -> None:
        c = db_connection.cursor()
        c.execute(
            """CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY,
                name TEXT,
                subtitle TEXT,
                description TEXT,
                type TEXT,
                tournament_close_date TEXT
            )"""
        )
        c.execute(
            """INSERT OR REPLACE INTO projects (
                id,
                name,
                subtitle,
                description,
                type,
                tournament_close_date
                )
                VALUES
                (?, ?, ?, ?, ?, ?)
            """,
            (
                self.id,
                self.name,
                self.subtitle,
                self.description,
                self.type,
                self.tournament_close_date,
            ),
        )
        db_connection.commit()

    @classmethod
    def load_from_db(cls, db_connection) -> list["Project"]:
        c = db_connection.cursor()
        c.execute("""SELECT * FROM projects""")
        projects = c.fetchall()
        return [cls(*project) for project in projects]


@dataclass
class Category:
    id: str
    short_name: str
    long_name: str

    @classmethod
    def from_api_response(cls, category_dict: dict, db_connection) -> "Category":
        category = cls(
            id=category_dict["id"],
            short_name=category_dict["short_name"],
            long_name=category_dict["long_name"],
        )
        category.save_to_db(db_connection)
        return category

    def save_to_db(self, db_connection) -> None:
        c = db_connection.cursor()
        c.execute(
            """CREATE TABLE IF NOT EXISTS categories (
                id TEXT PRIMARY KEY,
                short_name TEXT,
                long_name TEXT
            )"""
        )
        c.execute(
            """INSERT OR REPLACE INTO categories (
                id,
                short_name,
                long_name
                )
                VALUES
                (?, ?, ?)
            """,
            (
                self.id,
                self.short_name,
                self.long_name,
            ),
        )
        db_connection.commit()

    @classmethod
    def load_from_db(cls, db_connection) -> list["Category"]:
        c = db_connection.cursor()
        c.execute("""SELECT * FROM categories""")
        categories = c.fetchall()
        return [cls(*category) for category in categories]


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
    number_of_forecasters: int
    activity: float
    community_prediction: str | None = None
    community_prediction_statistic: str | None = None
    category: Category | None = None

    @classmethod
    def from_api_response(
        cls, question_dict: dict, db_connection, category: Category | None = None
    ) -> "Question":
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
            number_of_forecasters=question_dict["number_of_forecasters"],
            community_prediction=community_prediction,
            community_prediction_statistic=statistic,
            category=category,
        )
        question.save_to_db(db_connection)
        return question

    def save_to_db(self, db_connection):
        c = db_connection.cursor()

        # Create the questions table if it does not already exist
        c.execute(
            """CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY,
                page_url TEXT,
                author_name TEXT,
                title TEXT,
                created_time TIMESTAMP,
                publish_time TIMESTAMP,
                close_time TIMESTAMP,
                resolve_time TIMESTAMP,
                active_state TEXT,
                number_of_forecasters INTEGER,
                activity FLOAT,
                community_prediction FLOAT,
                community_prediction_statistic TEXT,
                category TEXT
            )"""
        )

        c.execute(
            """INSERT OR REPLACE INTO questions (
                id, 
                page_url, 
                author_name, 
                title, 
                created_time, 
                publish_time, 
                close_time, 
                resolve_time, 
                active_state, 
                number_of_forecasters, 
                activity, 
                community_prediction, 
                community_prediction_statistic, 
                category
                )
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
                self.number_of_forecasters,
                self.activity,
                self.community_prediction,
                self.community_prediction_statistic,
                self.category.id if self.category else None,
            ),
        )
        db_connection.commit()

    @classmethod
    def load_from_db(cls, db_connection) -> list["Question"]:
        c = db_connection.cursor()

        c.execute("SELECT * FROM questions")
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
