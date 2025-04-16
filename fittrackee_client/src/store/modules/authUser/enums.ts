export enum AuthUserActions {
  ABORT_ARCHIVE_UPLOAD_TASK = 'ABORT_ARCHIVE_UPLOAD_TASK',
  ACCEPT_PRIVACY_POLICY = 'ACCEPT_PRIVACY_POLICY',
  APPEAL = 'APPEAL',
  CHECK_AUTH_USER = 'CHECK_AUTH_USER',
  CONFIRM_ACCOUNT = 'CONFIRM_ACCOUNT',
  CONFIRM_EMAIL = 'CONFIRM_EMAIL',
  DELETE_ACCOUNT = 'DELETE_ACCOUNT',
  DELETE_ARCHIVE_UPLOAD_TASK = 'DELETE_ARCHIVE_UPLOAD_TASK',
  DELETE_PICTURE = 'DELETE_PICTURE',
  GET_ACCOUNT_SUSPENSION = 'GET_ACCOUNT_SUSPENSION',
  GET_ARCHIVE_UPLOAD_TASK = 'GET_ARCHIVE_UPLOAD_TASK',
  GET_ARCHIVE_UPLOAD_TASKS = 'GET_ARCHIVE_UPLOAD_TASKS',
  GET_BLOCKED_USERS = 'GET_BLOCKED_USERS',
  GET_FOLLOW_REQUESTS = 'GET_FOLLOW_REQUESTS',
  GET_REQUEST_DATA_EXPORT = 'GET_REQUEST_DATA_EXPORT',
  GET_USER_PROFILE = 'GET_USER_PROFILE',
  GET_USER_SANCTION = 'GET_USER_SANCTION',
  GET_TIMEZONES = 'GET_TIMEZONES',
  LOGIN_OR_REGISTER = 'LOGIN_OR_REGISTER',
  LOGOUT = 'LOGOUT',
  REQUEST_DATA_EXPORT = 'REQUEST_DATA_EXPORT',
  RESEND_ACCOUNT_CONFIRMATION_EMAIL = 'RESEND_ACCOUNT_CONFIRMATION_EMAIL',
  RESET_USER_PASSWORD = 'RESET_USER_PASSWORD',
  RESET_USER_SPORT_PREFERENCES = 'RESET_USER_SPORT_PREFERENCES',
  SEND_PASSWORD_RESET_REQUEST = 'SEND_PASSWORD_RESET_REQUEST',
  UPDATE_FOLLOW_REQUESTS = 'UPDATE_FOLLOW_REQUESTS',
  UPDATE_USER_ACCOUNT = 'UPDATE_USER_ACCOUNT',
  UPDATE_USER_PICTURE = 'UPDATE_USER_PICTURE',
  UPDATE_USER_PROFILE = 'UPDATE_USER_PROFILE',
  UPDATE_USER_PREFERENCES = 'UPDATE_USER_PREFERENCES',
  UPDATE_USER_NOTIFICATIONS_PREFERENCES = 'UPDATE_USER_NOTIFICATIONS_PREFERENCES',
  UPDATE_USER_SPORT_PREFERENCES = 'UPDATE_USER_SPORT_PREFERENCES',
}

export enum AuthUserGetters {
  ACCOUNT_SUSPENSION = 'ACCOUNT_SUSPENSION',
  ARCHIVE_UPLOAD_TASK = 'ARCHIVE_UPLOAD_TASK',
  ARCHIVE_UPLOAD_TASKS = 'ARCHIVE_UPLOAD_TASKS',
  ARCHIVE_UPLOAD_TASKS_LOADING = 'ARCHIVE_UPLOAD_TASKS_LOADING',
  ARCHIVE_UPLOAD_TASKS_PAGINATION = 'ARCHIVE_UPLOAD_TASKS_PAGINATION',
  AUTH_TOKEN = 'AUTH_TOKEN',
  AUTH_USER_PROFILE = 'AUTH_USER_PROFILE',
  BLOCKED_USERS = 'BLOCKED_USERS',
  EXPORT_REQUEST = 'EXPORT_REQUEST',
  FOLLOW_REQUESTS = 'FOLLOW_REQUESTS',
  HAS_ADMIN_RIGHTS = 'HAS_ADMIN_RIGHTS',
  HAS_MODERATOR_RIGHTS = 'HAS_MODERATOR_RIGHTS',
  HAS_OWNER_RIGHTS = 'HAS_OWNER_RIGHTS',
  IS_AUTHENTICATED = 'IS_AUTHENTICATED',
  IS_PROFILE_NOT_LOADED = 'IS_PROFILE_NOT_LOADED',
  IS_SUCCESS = 'IS_SUCCESS',
  IS_SUSPENDED = 'IS_SUSPENDED',
  IS_REGISTRATION_SUCCESS = 'IS_REGISTRATION_SUCCESS',
  IS_PROFILE_LOADED = 'IS_PROFILE_LOADED',
  TIMEZONES = 'TIMEZONES',
  USER_LOADING = 'USER_LOADING',
  USER_SANCTION = 'USER_SANCTION',
}

export enum AuthUserMutations {
  CLEAR_AUTH_USER_TOKEN = 'CLEAR_AUTH_USER_TOKEN',
  SET_EXPORT_REQUEST = 'SET_EXPORT_REQUEST',
  SET_ARCHIVE_UPLOAD_TASK = 'SET_ARCHIVE_UPLOAD_TASK',
  SET_ARCHIVE_UPLOAD_TASKS = 'SET_ARCHIVE_UPLOAD_TASKS',
  SET_ARCHIVE_UPLOAD_TASKS_LOADING = 'SET_ARCHIVE_UPLOAD_TASKS_LOADING',
  SET_ARCHIVE_UPLOAD_TASKS_PAGINATION = 'SET_ARCHIVE_UPLOAD_TASKS_PAGINATION',
  SET_ACCOUNT_SUSPENSION = 'SET_ACCOUNT_SUSPENSION',
  SET_TIMEZONES = 'SET_TIMEZONES',
  SET_USER_SANCTION = 'SET_USER_SANCTION',
  UPDATE_AUTH_TOKEN = 'UPDATE_AUTH_TOKEN',
  UPDATE_AUTH_USER_PROFILE = 'UPDATE_AUTH_USER_PROFILE',
  UPDATE_BLOCKED_USERS = 'UPDATE_BLOCKED_USERS',
  UPDATE_FOLLOW_REQUESTS = 'UPDATE_FOLLOW_REQUESTS',
  UPDATE_IS_SUCCESS = 'UPDATE_USER_IS_SUCCESS',
  UPDATE_IS_REGISTRATION_SUCCESS = 'UPDATE_IS_REGISTRATION_SUCCESS',
  UPDATE_USER_LOADING = 'UPDATE_USER_LOADING',
}
