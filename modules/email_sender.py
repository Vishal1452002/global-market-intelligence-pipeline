import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from settings import settings
from database import get_db_session
from models import EmailLog


def send_email(subject, html_content, report_id):
    logging.info("Email sending started")
    print("Email sending started")

    recipients = settings.RECIPIENTS

    session = get_db_session()

    try:
        print("Connecting to Gmail...")

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()

            print("Logging in...")
            server.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)

            # ✅ Create message ONCE
            msg = MIMEMultipart("alternative")
            msg["From"] = settings.EMAIL_USER
            msg["To"] = ", ".join(recipients)   # 👈 ALL recipients here
            msg["Subject"] = subject

            msg.attach(MIMEText(html_content, "html"))

            print("Sending email to all recipients...")

            # ✅ Send once to all
            server.sendmail(
                settings.EMAIL_USER,
                recipients,   # list of emails
                msg.as_string()
            )

            print("Email sent successfully")

            # ✅ Log once (or you can log per recipient if needed)
            for recipient in recipients:
                log = EmailLog(
                    report_id=report_id,
                    recipient=recipient,
                    status="SENT",
                    error_message=None,
                )
                session.add(log)

            session.commit()

    except Exception as e:
        session.rollback()
        print("EMAIL ERROR:", e)

        for recipient in recipients:
            log = EmailLog(
                report_id=report_id,
                recipient=recipient,
                status="FAILED",
                error_message=str(e),
            )
            session.add(log)

        session.commit()

    finally:
        session.close()