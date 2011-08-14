import datetime
import smtplib

from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders

from twisted.python import log


class Plugin(object):

    """ Email sending plugin """

    name = "email"
    description = "Email integration"
    author = "MHub"

    default_config = {
        "from_address": "user@gmail.com",
        "host": "smtp.gmail.com",
        "port": 587,
        "username": "user@gmail.com",
        "password": "password",
        "start_tls": True
    }
    

    def on_init(self):

        """ On initialisation handler """

        pass


    def on_message(self, data, message):

        """ AMQP on-message handler """

        action, params = data.get("action"), data.get("params")

        if action == "%s.action" % (self.name):

            recipients = params.get("recipients")
            subject = params.get("subject", "No Subject")
            body = params.get("body", "No Body")

            if recipients is not None:
                self.logger.info("Sending Email")
                self.send_email(recipients, subject, body)


    def send_email(self, recipients, subject, body, attachments=None):

        """ Send email helper """

        self.logger.debug("To: %s" % (", ".join(recipients)))
        self.logger.debug("Subject: %s" % (subject))

        msg = MIMEMultipart()

        msg["From"] = self.cfg.get("from_address")
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = subject

        msg.attach(MIMEText(body))

        if attachments is None: attachments = []

        for attachment in attachments:

            part = MIMEBase("application", "octet-stream")
            part.set_payload(open(attachment, "rb").read())
            Encoders.encode_base64(part)
            part.add_header("Content-Disposition", 'attachment; filename="%s"' % os.path.basename(attachment))
            msg.attach(part)

        smtp = smtplib.SMTP(self.cfg.get("smtp_host"), int(self.cfg.get("smtp_port")))
        if(bool(self.cfg.get("smtp_start_tls")) == True):
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
        smtp.login(self.cfg.get("smtp_username"), self.cfg.get("smtp_password"))
        smtp.sendmail(self.cfg.get("smtp_username"), recipients, msg.as_string())
        smtp.close()
