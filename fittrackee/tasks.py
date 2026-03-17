import dramatiq

from fittrackee import create_app

app = create_app()
broker = dramatiq.get_broker()
