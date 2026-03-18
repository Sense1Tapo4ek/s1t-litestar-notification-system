from dishka import make_async_container
from shared.provider import SharedProvider
from core.provider import CoreProvider
from notifications.provider import NotificationsProvider


def build_container():
    return make_async_container(
        SharedProvider(),
        CoreProvider(),
        NotificationsProvider(),
    )
