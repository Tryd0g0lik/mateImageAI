import re
from django.core.signing import Signer
from dotenv_ import (APP_PROTOCOL, APP_HOST, APP_PORT)
from django.template.loader import render_to_string
signer = Signer()
def send_activation_notificcation(user) -> bool:
    """
    TODO: This function send (after the Signal) a message by email from user.\
     This is the part \
     authentication of the user.
     Note: Look up the 'user_registered_dispatcher' from 'apps.py'
    :param user: object
    """

    from project.settings import ALLOWED_HOSTS
    url = f"{APP_PROTOCOL}://{APP_HOST}"
    _resp_bool = False
    try:
        if APP_PORT:
            APP_PROTOCOL, APP_HOST,
            url += f":{APP_PORT}"


        context = {
            "user": user,
            "host": url,
            "sign": signer.sign(user.username).replace(":", "_mull_")
        }
        # LETTER 1
        subject = render_to_string(
            template_name="email/activation_letter_subject.txt",
            context=context,
        )
        # LETTER 2
        file_name = "email/activation_letter_body.txt"
        if user.is_superuser:
            file_name = "email/activation_admin_letter_body.txt"
        body_text = render_to_string(template_name=file_name,
                                     context=context)
        # RUN THE 'email_user' METHOD FROM BASIS THE uSER MODEL
        # https://docs.djangoproject.com/en/5.1/topics/email/
        user.email_user(
            subject,
            body_text
        )
    except Exception as error:
        pass
    finally:
        return _resp_bool
