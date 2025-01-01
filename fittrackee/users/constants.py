USER_DATE_FORMAT = 'MM/dd/yyyy'
USER_LANGUAGE = 'en'
USER_TIMEZONE = 'Europe/Paris'
USER_LINK_TEMPLATE = (
    '<a href="{profile_url}" target="_blank" rel="noopener noreferrer">'
    '{username}</a>'
)

ADMINISTRATOR_NOTIFICATION_TYPES = [
    'account_creation',
]
MODERATOR_NOTIFICATION_TYPES = [
    'report',
    'suspension_appeal',
    'user_warning_appeal',
]
NOTIFICATION_TYPES = (
    ADMINISTRATOR_NOTIFICATION_TYPES
    + MODERATOR_NOTIFICATION_TYPES
    + [
        'comment_like',
        'comment_suspension',
        'comment_unsuspension',
        'follow',
        'follow_request',
        'follow_request_approved',
        'mention',
        'user_warning',
        'user_warning_lifting',
        'workout_comment',
        'workout_like',
        'workout_suspension',
        'workout_unsuspension',
    ]
)
