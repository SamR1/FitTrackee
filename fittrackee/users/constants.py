USER_DATE_FORMAT = "MM/dd/yyyy"
USER_LANGUAGE = "en"
USER_TIMEZONE = "Europe/Paris"
USER_LINK_TEMPLATE = (
    '<a href="{profile_url}" target="_blank" rel="noopener noreferrer">'
    "{username}</a>"
)

ADMINISTRATOR_NOTIFICATION_TYPES = [
    "account_creation",
]
MODERATOR_NOTIFICATION_TYPES = [
    "report",
    "suspension_appeal",
    "user_warning_appeal",
]
NOTIFICATION_TYPES = (
    ADMINISTRATOR_NOTIFICATION_TYPES
    + MODERATOR_NOTIFICATION_TYPES
    + [
        "comment_like",
        "comment_suspension",
        "comment_unsuspension",
        "follow",
        "follow_request",
        "follow_request_approved",
        "mention",
        "user_data_export",
        "user_warning",
        "user_warning_lifting",
        "workouts_archive_upload",
        "workout_comment",
        "workout_like",
        "workout_suspension",
        "workout_unsuspension",
    ]
)

NOTIFICATIONS_PREFERENCES_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "Notifications",
    "description": "Preferences for UI notifications",
    "type": "object",
    "properties": {
        "account_creation": {
            "type": "boolean",
            "default": True,
        },
        "comment_like": {
            "type": "boolean",
            "default": True,
        },
        "follow": {
            "type": "boolean",
            "default": True,
        },
        "follow_request": {
            "type": "boolean",
            "default": True,
        },
        "follow_request_approved": {
            "type": "boolean",
            "default": True,
        },
        "mention": {
            "type": "boolean",
            "default": True,
        },
        "workout_comment": {
            "type": "boolean",
            "default": True,
        },
        "workout_like": {
            "type": "boolean",
            "default": True,
        },
    },
    "additionalProperties": False,
}
