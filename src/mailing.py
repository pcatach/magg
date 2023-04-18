import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(
    subject: str, from_address: str, to_address: str, html_content: str, password: str
) -> None:
    # Set up the email message
    message = MIMEMultipart()
    message["Subject"] = subject
    message["From"] = from_address
    message["To"] = to_address

    # Attach the HTML content to the email message
    message.attach(MIMEText(html_content, "html"))

    # Set up the SMTP server and send the email
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(from_address, password)
        server.sendmail(from_address, to_address, message.as_string())
