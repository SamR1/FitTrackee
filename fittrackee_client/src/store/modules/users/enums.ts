export enum UsersActions {
  EMPTY_USER = 'EMPTY_USER',
  EMPTY_USERS = 'EMPTY_USERS',
  GET_USER = 'GET_USER',
  GET_USERS = 'GET_USERS',
  GET_USERS_FOR_ADMIN = 'GET_USERS_FOR_ADMIN',
  UPDATE_USER = 'UPDATE_USER',
  DELETE_USER_ACCOUNT = 'DELETE_USER_ACCOUNT',
  UPDATE_RELATIONSHIP = 'UPDATE_RELATIONSHIP',
  GET_RELATIONSHIPS = 'GET_RELATIONSHIPS',
  EMPTY_RELATIONSHIPS = 'EMPTY_RELATIONSHIPS',
}

export enum UsersGetters {
  USER = 'USER',
  USER_RELATIONSHIPS = 'USER_RELATIONSHIPS',
  USERS = 'USERS',
  USERS_IS_SUCCESS = 'USERS_IS_SUCCESS',
  USERS_LOADING = 'USERS_LOADING',
  USERS_PAGINATION = 'USERS_PAGINATION',
}

export enum UsersMutations {
  UPDATE_USER = 'UPDATE_USER',
  UPDATE_USER_IN_USERS = 'UPDATE_USER_IN_USERS',
  UPDATE_USER_IN_RELATIONSHIPS = 'UPDATE_USER_IN_RELATIONSHIPS',
  UPDATE_USER_RELATIONSHIPS = 'UPDATE_USER_RELATIONSHIPS',
  UPDATE_USERS = 'UPDATE_USERS',
  UPDATE_USERS_LOADING = 'UPDATE_USERS_LOADING',
  UPDATE_USERS_PAGINATION = 'UPDATE_USERS_PAGINATION',
  UPDATE_IS_SUCCESS = 'UPDATE_IS_SUCCESS',
}
