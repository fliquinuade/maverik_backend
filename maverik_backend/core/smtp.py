import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

import requests


def send_mail_with_auth(
    send_from: str,
    send_to: list[str],
    subject: str,
    text: str,
    server: str = "",
    port: int = 0,
    username: str = "",
    password: str = "",
):
    assert isinstance(send_to, list), "sent-to is not a list"
    assert server != "", "server has not set yet"
    assert username != "", "username has not set yet"
    assert password != "", "password has not set yet"

    msg = MIMEMultipart(
        From=send_from,
        To=COMMASPACE.join(send_to),
        Date=formatdate(localtime=True),
        Subject=subject,
    )
    msg["Subject"] = subject
    msg.attach(MIMEText(text))

    with smtplib.SMTP(host=server, port=port) as smtp:
        smtp.login(username, password)
        smtp.sendmail(send_from, send_to, msg.as_string())


def send_email_with_api(
    to_email: str,
    subject: str,
    body: str,
    api_url: str,
    api_key: str,
    sender: tuple[str, str],
):
    payload = json.dumps(
        {
            "sender": {"name": sender[0], "email": sender[1]},
            "to": [{"email": to_email}],
            "subject": subject,
            "textContent": body,
        }
    )
    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json",
    }
    response = requests.request("POST", api_url, headers=headers, data=payload)
    print(response)
