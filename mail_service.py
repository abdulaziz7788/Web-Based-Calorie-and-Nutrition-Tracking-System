from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer

class MailService:
    def __init__(self, app):
        self.app = app
        self.mail = Mail(app)
        self.serializer = URLSafeTimedSerializer(app.secret_key)

    def send_email(self, subject, recipients, body):
        msg = Message(subject, sender=self.app.config['MAIL_USERNAME'], recipients=recipients)
        msg.body = body
        self.mail.send(msg)

    def generate_token(self, email, salt="email-confirm"):
        return self.serializer.dumps(email, salt=salt)

    def confirm_token(self, token, expiration=3600, salt="email-confirm"):
        try:
            email = self.serializer.loads(token, salt=salt, max_age=expiration)
        except Exception:
            return None
        return email
