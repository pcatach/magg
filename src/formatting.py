def format_question(question):
    formatted_question = (
        f'<h1><a href="{question.page_url}">{question.title}</a></h2>\n'
        f"<p><b>Author</b>: {question.author_name}</p>\n"
        f"<p><b>Published at</b>: {question.publish_time}</p>\n"
        f'<p><b>Description</b>: <a href="{question.page_url}">{question.description[:400]}...</a></p>\n'
        f"<p><b>Closes at</b>: {question.close_time}</p>\n"
        f"<p><b>Resolves at</b>: {question.resolve_time}</p>\n"
        f"<p><b>Number of predictions</b>: {question.number_of_predictions}</p>\n"
        f"<p><b>Current prediction</b>: {question.metacalculus_prediction}</p>\n"
    )

    return formatted_question


def format_email(categories, questions):
    formatted_email = (
        "<p>Hello, <p>\n"
        + "<p>This is your weekly digest of new metaculus questions on categories:\n<b>"
        + "</b>, <b>".join(categories)
        + "</b>.<p>"
        + "<p>Here are this week's questions:</p>"
    )

    for question in questions:
        formatted_email += format_question(question)

    formatted_email += "<p>Hope you have a great week,</p>" "<p><b>magg.</b></p>"

    return formatted_email
