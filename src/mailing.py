import boto3
from botocore.exceptions import ClientError


def send_email(
    subject: str,
    from_address: str,
    to_address: str,
    html_content: str,
    aws_region: str,
) -> None:
    sender = f"Sender Name <{from_address}>"

    client = boto3.client("ses", region_name=aws_region)
    try:
        # Provide the contents of the email.
        response = client.send_email(
            Destination={
                "ToAddresses": [
                    to_address,
                ],
            },
            Message={
                "Body": {
                    "Html": {
                        "Charset": "UTF-8",
                        "Data": html_content,
                    },
                },
                "Subject": {
                    "Charset": "UTF-8",
                    "Data": subject,
                },
            },
            Source=sender,
        )
    # Display an error if something goes wrong.
    except ClientError as e:
        print(e.response["Error"]["Message"])
    else:
        print("Email sent! Message ID:"),
        print(response["MessageId"])
