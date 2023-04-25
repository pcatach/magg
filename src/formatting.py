def generate_question_digest(questions, categories):
    # Create the HTML header
    html = "<html><head><title>Question Digest</title></head><style>"

    # Add the CSS
    html += "body {font-family: Arial, sans-serif; padding: 20px;}"
    html += "h2 {font-size: 24px; margin-top: 40px;}"
    html += "a {color: #0077cc; text-decoration: none;}"
    html += "a:hover {text-decoration: underline;}"
    html += "p {font-size: 16px; line-height: 24px; margin-bottom: 16px;}"
    html += "hr {border: none; border-top: 1px solid #ddd; margin: 20px 0;}"
    html += "</style></head><body>"

    # Add the intro text
    html += (
        "<p>Hello, <p>\n"
        + "<p>This is your weekly digest of new metaculus questions on categories:\n<b>"
        + "</b>, <b>".join(categories)
        + "</b>.<p>"
    )

    html += "<p>Here are the latest questions:</p>"

    # Loop through the questions and add them to the HTML
    for question in questions:
        html += f'<h2><a href="{question.page_url}">{question.title}</a></h2>'
        html += f"<p><strong>Category:</strong> {question.category}</p>"
        html += f"<p><strong>Published Date:</strong> {question.publish_time}</p>"
        html += f"<p><strong>Closing Date:</strong> {question.close_time}</p>"
        html += f"<p><strong>Resolving Date:</strong> {question.resolve_time}</p>"
        html += f"<p><strong>Number of Predictions:</strong> {question.number_of_predictions}</p>"
        html += f"<p><strong>Community Prediction{' ('+question.community_prediction_statistic+')' if question.community_prediction_statistic else ''}</strong>: "
        if question.community_prediction is not None:
            if type(question.community_prediction) == float:
                html += f"{float(question.community_prediction):.2f}"
            else:
                html += f"{question.community_prediction}"
        else:
            html += f"N/A"
        html += "</p>\n<hr>"

    # Add the HTML footer
    html += "<p>Hope you have a great day,</p>" "<p><b>magg.</b></p>"
    html += "</body></html>"

    return html
