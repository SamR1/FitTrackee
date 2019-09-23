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
}
