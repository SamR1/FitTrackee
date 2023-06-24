Authentication and account
##########################

.. autoflask:: fittrackee:create_app()
   :endpoints:
    auth.register_user,
    auth.confirm_account,
    auth.resend_account_confirmation_email,
    auth.login_user,
    auth.get_authenticated_user_profile,
    auth.edit_user,
    auth.edit_user_preferences,
    auth.edit_user_sport_preferences,
    auth.reset_user_sport_preferences,
    auth.edit_picture,
    auth.del_picture,
    auth.request_password_reset,
    auth.update_user_account,
    auth.update_password,
    auth.update_email,
    auth.logout_user,
    auth.accept_privacy_policy,
    auth.get_user_data_export,
    auth.request_user_data_export,
    auth.download_data_export