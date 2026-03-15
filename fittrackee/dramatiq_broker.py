from threading import local
from typing import TYPE_CHECKING, Any, Optional

import dramatiq
from dramatiq import Middleware
from dramatiq.brokers.redis import RedisBroker
from dramatiq.middleware import Retries, ShutdownNotifications, TimeLimit

if TYPE_CHECKING:
    from dramatiq_abort import Abortable
    from flask import Flask


class AppContextMiddleware(Middleware):
    # From https://github.com/Bogdanp/flask_dramatiq_example

    state = local()

    def __init__(self, app: "Flask") -> None:
        self.app = app

    def before_process_message(
        self,
        broker: "dramatiq.broker.Broker",
        message: "dramatiq.broker.MessageProxy",
    ) -> None:
        context = self.app.app_context()
        context.push()

        self.state.context = context

    def after_process_message(
        self,
        broker: "dramatiq.broker.Broker",
        message: "dramatiq.broker.MessageProxy",
        *,
        result: Any = None,
        exception: Optional[BaseException] = None,
    ) -> None:
        try:
            context = self.state.context
            context.pop(exception)
            del self.state.context
        except AttributeError:
            pass

    after_skip_message = after_process_message


def init_dramatiq_broker(
    app: "Flask", abortable: "Abortable", redis_url: str
) -> None:
    broker_cls = app.config["DRAMATIQ_BROKER"]
    kw = {}
    if issubclass(broker_cls, RedisBroker):
        kw["url"] = redis_url
    middlewares = [
        AppContextMiddleware(app),
        TimeLimit(),
        ShutdownNotifications(),
        Retries(),
        abortable,
    ]
    broker = broker_cls(middleware=middlewares, **kw)

    # At startup, actors are already registered with the default global broker
    # (no lazy loading).
    # This allows to update actors in factory function and use broker from
    # application config
    default_broker = dramatiq.get_broker()
    for existing_actor_name in default_broker.get_declared_actors():
        actor = default_broker.get_actor(existing_actor_name)
        actor.broker = broker
        broker.declare_actor(actor)

    dramatiq.set_broker(broker)
