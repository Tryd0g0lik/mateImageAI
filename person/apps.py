from django.apps import AppConfig
from django.dispatch import Signal


class PersonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "person"


# send message from the registration part
# https://docs.djangoproject.com/en/4.2/topics/signals/#defining-signals
signal_user_registered = Signal(use_caching=False)


def user_registered_dispatcher(sender, **kwargs) -> bool:
    """
    This is a handler of signal. Send an activation message by \
        the user email.\
        This is interface from part from registration the new user.\
        Message, it contains the signature of link for authentication
        /
        All interface by the user's authentication in folder '**/contribute'  and \
        look up the  'signal_user_registered.send(....)' code, and
        by module the 'person', plus the function 'user_activate' by \
        module the 'person'.
    :param sender:
    :param kwargs:
    :return: bool
    """
    from person.contribute.utilite import send_activation_notificcation

    __text = "Function: %s" % user_registered_dispatcher.__name__
    _resp_bool = False
    try:
        res_bool = send_activation_notificcation(kwargs["isinstance"])
        _resp_bool = True
        if not res_bool:
            raise ValueError(f"Something what wrong. {__text}")

    except Exception:
        _resp_bool = False
    finally:
        return _resp_bool


signal_user_registered.connect(weak=False, receiver=user_registered_dispatcher)
# After connect
# https://docs.djangoproject.com/en/4.2/topics/signals/#sending-signals
# Find the line where, it has sub-string 'signal_user_registered.send(....)'
