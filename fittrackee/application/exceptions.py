class AppConfigException(Exception):
    def __init__(self) -> None:
        super().__init__(
            "Error when getting configuration from database, "
            "please restart the application."
        )
