import {
  addDays,
  addMonths,
  addWeeks,
  addYears,
  endOfDay,
  endOfMonth,
  endOfWeek,
  endOfYear,
  format,
  intlFormat,
  startOfDay,
  startOfMonth,
  startOfWeek,
  startOfYear,
  subDays,
  subMonths,
  subWeeks,
  subYears,
} from 'date-fns'

import createI18n from '@/i18n'
import type { IChartDataset } from '@/types/chart'
import type { ISport } from '@/types/sports'
import type {
  IStatisticsChartData,
  IStatisticsDateParams,
  IStatisticsWorkoutsAverageChartData,
  TStatisticsDatasetKeys,
  TStatisticsDatasets,
  TStatisticsFromApi,
  TStatisticsTimeFrame,
  TStatisticsType,
} from '@/types/statistics'
import { incrementDate, getStartDate, getDateFormat } from '@/utils/dates'
import { localeFromLanguage } from '@/utils/locales'
import { sportColors } from '@/utils/sports'
import { convertStatsDistance } from '@/utils/units'

const { locale } = createI18n.global

export const dateFormats: Record<string, Record<string, string>> = {
  day: {
    api: 'yyyy-MM-dd',
    chart: 'MM/dd/yyyy',
  },
  week: {
    api: 'yyyy-MM-dd',
    chart: 'MM/dd/yyyy',
  },
  month: {
    api: 'yyyy-MM',
    chart: 'MM/yyyy',
  },
  year: {
    api: 'yyyy',
    chart: 'yyyy',
  },
}

export const datasetKeys: TStatisticsDatasetKeys[] = [
  'average_ascent',
  'average_descent',
  'average_distance',
  'average_duration',
  'average_speed',
  'total_workouts',
  'total_duration',
  'total_distance',
  'total_ascent',
  'total_descent',
]

export const getDateKeys = (
  params: IStatisticsDateParams,
  weekStartingMonday: boolean
): Date[] => {
  const days = []
  for (
    let day = getStartDate(params.duration, params.start, weekStartingMonday);
    day <= params.end;
    day = incrementDate(params.duration, day)
  ) {
    days.push(day)
  }
  return days
}

const getStatisticsChartDataset = (
  sportLabel: string,
  color: string,
  isLineChart = false
): IChartDataset => {
  const dataset: IChartDataset = {
    label: sportLabel,
    backgroundColor: [color],
    data: [],
  }
  if (isLineChart) {
    dataset.type = 'line'
    dataset.borderColor = [color]
    dataset.spanGaps = true
  } else {
    dataset.type = 'bar'
  }
  return dataset
}

export const getDatasets = (displayedSports: ISport[]): TStatisticsDatasets => {
  const datasets: TStatisticsDatasets = {
    average_ascent: [],
    average_descent: [],
    average_distance: [],
    average_duration: [],
    average_speed: [],
    average_workouts: [],
    total_workouts: [],
    total_distance: [],
    total_duration: [],
    total_ascent: [],
    total_descent: [],
  }
  displayedSports.forEach((sport) => {
    const color = sport.color ? sport.color : sportColors[sport.label]
    datasets.average_ascent.push(
      getStatisticsChartDataset(sport.label, color, true)
    )
    datasets.average_descent.push(
      getStatisticsChartDataset(sport.label, color, true)
    )
    datasets.average_distance.push(
      getStatisticsChartDataset(sport.label, color, true)
    )
    datasets.average_duration.push(
      getStatisticsChartDataset(sport.label, color, true)
    )
    datasets.average_speed.push(
      getStatisticsChartDataset(sport.label, color, true)
    )
    datasets.total_workouts.push(getStatisticsChartDataset(sport.label, color))
    datasets.total_distance.push(getStatisticsChartDataset(sport.label, color))
    datasets.total_duration.push(getStatisticsChartDataset(sport.label, color))
    datasets.total_ascent.push(getStatisticsChartDataset(sport.label, color))
    datasets.total_descent.push(getStatisticsChartDataset(sport.label, color))
  })
  return datasets
}

export const convertStatsValue = (
  datasetKey: TStatisticsDatasetKeys,
  value: number,
  useImperialUnits: boolean
): number => {
  switch (datasetKey) {
    case 'average_speed':
    case 'total_distance':
    case 'total_ascent':
    case 'total_descent':
    case 'average_distance':
    case 'average_ascent':
    case 'average_descent':
      return convertStatsDistance(
        ['average_speed', 'total_distance', 'average_distance'].includes(
          datasetKey
        )
          ? 'km'
          : 'm',
        value,
        useImperialUnits
      )
    case 'total_workouts':
    case 'total_duration':
    case 'average_duration':
    default:
      return value
  }
}

export const formatDateLabel = (
  date: Date,
  duration: string,
  userDateFormat: string,
  dateFormat: string
): string => {
  if (['day', 'week'].includes(duration)) {
    // note: for now, statistics are not publicly available.
    if (userDateFormat === 'browser_settings') {
      return intlFormat(date)
    }
    return format(date, getDateFormat(userDateFormat, locale.value), {
      locale: localeFromLanguage[locale.value],
    })
  }
  return format(date, dateFormat, { locale: localeFromLanguage[locale.value] })
}

export const formatStats = (
  params: IStatisticsDateParams,
  weekStartingMonday: boolean,
  sports: ISport[],
  displayedSportsId: number[],
  apiStats: TStatisticsFromApi,
  useImperialUnits: boolean,
  userDateFormat: string
): IStatisticsChartData => {
  const dayKeys = getDateKeys(params, weekStartingMonday)
  const dateFormat = dateFormats[params.duration]
  const displayedSports = sports.filter((sport) =>
    displayedSportsId.includes(sport.id)
  )
  const labels: string[] = []
  const datasets = getDatasets(displayedSports)
  const sportsId: Record<string, number> = {}
  displayedSports.forEach(
    (displayedSport) => (sportsId[displayedSport.label] = displayedSport.id)
  )

  dayKeys.forEach((key) => {
    const date: string = format(key, dateFormat.api)
    const label: string = formatDateLabel(
      key,
      params.duration,
      userDateFormat,
      dateFormat.chart
    )
    labels.push(label)
    datasetKeys.forEach((datasetKey) => {
      datasets[datasetKey].forEach((dataset) => {
        if (date in apiStats && sportsId[dataset.label] in apiStats[date]) {
          dataset.data.push(
            convertStatsValue(
              datasetKey,
              apiStats[date][sportsId[dataset.label]][datasetKey],
              useImperialUnits
            )
          )
        } else {
          dataset.data.push(datasetKey.startsWith('average') ? null : 0)
        }
      })
    })
  })
  return {
    labels,
    datasets,
  }
}

export const getStatsDateParams = (
  date: Date,
  timeFrame: TStatisticsTimeFrame,
  weekStartingMonday: boolean,
  statsType: TStatisticsType
): IStatisticsDateParams => {
  const weekStartsOn = weekStartingMonday ? 1 : 0

  let start, end
  if (timeFrame === 'year') {
    start = startOfYear(subYears(date, 9))
    end = endOfYear(date)
  } else if (timeFrame === 'week') {
    start = startOfWeek(subMonths(date, 2), { weekStartsOn })
    end = endOfWeek(date, { weekStartsOn })
  } else if (timeFrame === 'day') {
    start = startOfDay(subWeeks(date, 2))
    end = endOfDay(date)
  } else {
    start = startOfMonth(subMonths(date, 11)) // month
    end = endOfMonth(date) // month
  }
  return {
    duration: timeFrame,
    end,
    start,
    statsType,
  }
}

export const updateChartParams = (
  chartParams: IStatisticsDateParams,
  backward: boolean,
  weekStartingMonday: boolean
): IStatisticsDateParams => {
  const { duration, start, end } = chartParams
  const weekStartsOn = weekStartingMonday ? 1 : 0
  if (duration === 'year') {
    return {
      duration,
      end: endOfYear(backward ? subYears(end, 1) : addYears(end, 1)),
      start: startOfYear(backward ? subYears(start, 1) : addYears(start, 1)),
      statsType: chartParams.statsType,
    }
  }
  if (duration === 'week') {
    return {
      duration,
      end: endOfWeek(backward ? subWeeks(end, 1) : addWeeks(end, 1), {
        weekStartsOn,
      }),
      start: startOfWeek(backward ? subWeeks(start, 1) : addWeeks(start, 1), {
        weekStartsOn,
      }),
      statsType: chartParams.statsType,
    }
  }
  if (duration === 'day') {
    return {
      duration,
      end: endOfDay(backward ? subDays(end, 1) : addDays(end, 1)),
      start: startOfDay(backward ? subDays(start, 1) : addDays(start, 1)),
      statsType: chartParams.statsType,
    }
  }

  return {
    duration,
    end: endOfMonth(backward ? subMonths(end, 1) : addMonths(end, 1)),
    start: startOfMonth(backward ? subMonths(start, 1) : addMonths(start, 1)),
    statsType: chartParams.statsType,
  }
}

const getAverage = (values: (number | null)[]): number => {
  const sum = values.reduce((total, value) => (total ?? 0) + (value ?? 0), 0)
  const average = values.length ? (sum ?? 0) / values.length : 0
  return +average.toFixed(1)
}

const sortDatasets = (a: IChartDataset, b: IChartDataset): number => {
  const datasetALabel = a.label.toLowerCase()
  const datasetBLabel = b.label.toLowerCase()
  if (datasetALabel > datasetBLabel) {
    return 1
  }
  return datasetALabel < datasetBLabel ? -1 : 0
}

export const getWorkoutsAverageDatasets = (
  totalWorkouts: IChartDataset[],
  t: CallableFunction
): IStatisticsWorkoutsAverageChartData => {
  const labels: string[] = []
  const workoutsAverageDataset: IChartDataset = {
    label: 'workouts_average',
    backgroundColor: [],
    data: [],
  }
  let all_workouts: number[] = []
  const sortedTotalWorkouts = totalWorkouts
    .map((dataset) => {
      dataset.label = t(`sports.${dataset.label}.LABEL`)
      return dataset
    })
    .sort(sortDatasets)
  for (const dataset of sortedTotalWorkouts) {
    workoutsAverageDataset.data.push(getAverage(dataset.data))
    workoutsAverageDataset.backgroundColor.push(dataset.backgroundColor[0])
    labels.push(dataset.label)
    if (all_workouts.length > 0) {
      all_workouts = all_workouts.map(
        (value, index) => value + (dataset.data[index] ?? 0)
      )
    } else {
      all_workouts = dataset.data.map((value) => value ?? 0)
    }
  }
  return {
    labels,
    datasets: {
      workouts_average: [workoutsAverageDataset],
    },
    workoutsAverage: getAverage(all_workouts),
  }
}
