const emptyData = {
  data: [],
}

export default {
  language: 'en',
  message: '',
  messages: [],
  user: {
    isAuthenticated: false,
  },
  activities: {
    ...emptyData,
  },
  application: {
    statistics: {},
    config: {
      gpx_limit_import: null,
      is_registration_enabled: null,
      max_single_file_size: null,
      max_users: null,
      max_zip_file_size: null,
      registration: null,
    },
  },
  calendarActivities: {
    ...emptyData,
  },
  chartData: [],
  // check if storing gpx content is OK
  gpx: null,
  loading: false,
  records: {
    ...emptyData,
  },
  sports: {
    ...emptyData,
  },
  statistics: {
    data: {},
  },
  users: {
    ...emptyData,
  },
}
