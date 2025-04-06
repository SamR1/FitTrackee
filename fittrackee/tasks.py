from fittrackee import create_app, dramatiq

app = create_app()
broker = dramatiq.broker
