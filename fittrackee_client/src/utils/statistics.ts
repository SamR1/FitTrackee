import {
  addMonths,
  addWeeks,
  addYears,
  endOfMonth,
  endOfWeek,
  endOfYear,
  format,
  startOfMonth,
  startOfWeek,
  startOfYear,
  subMonths,
  subWeeks,
  subYears,
} from 'date-fns'

import { IChartDataset } from '@/types/chart'
import { ISport } from '@/types/sports'
import {
  IStatisticsChartData,
  IStatisticsDateParams,
  TStatisticsDatasetKeys,
  TStatisticsDatasets,
  TStatisticsFromApi,
} from '@/types/statistics'
import { incrementDate, startDate } from '@/utils/dates'
import { sportColors } from '@/utils/sports'

// date format from api
const dateFormats: Record<string, string> = {
  week: 'yyyy-MM-dd',
  month: 'yyyy-MM',
  year: 'yyyy',
}

export const datasetKeys: TStatisticsDatasetKeys[] = [
  'nb_workouts',
  'total_duration',
  'total_distance',
]

export const getDateKeys = (
  params: IStatisticsDateParams,
  weekStartingMonday: boolean
): Date[] => {
  const days = []
  for (
    let day = startDate(params.duration, params.start, weekStartingMonday);
    day <= params.end;
    day = incrementDate(params.duration, day)
  ) {
    days.push(day)
  }
  return days
}

const getStatisticsChartDataset = (
  sportLabel: string,
  color: string
): IChartDataset => {
  return {
    label: sportLabel,
    backgroundColor: [color],
    data: [],
  }
}

export const getDatasets = (displayedSports: ISport[]): TStatisticsDatasets => {
  const datasets: TStatisticsDatasets = {
    nb_workouts: [],
    total_distance: [],
    total_duration: [],
  }
  displayedSports.map((sport) => {
    const color = sportColors[sport.label]
    datasets.nb_workouts.push(getStatisticsChartDataset(sport.label, color))
    datasets.total_distance.push(getStatisticsChartDataset(sport.label, color))
    datasets.total_duration.push(getStatisticsChartDataset(sport.label, color))
  })
  return datasets
}

export const formatStats = (
  params: IStatisticsDateParams,
  weekStartingMonday: boolean,
  sports: ISport[],
  displayedSportsId: number[],
  apiStats: TStatisticsFromApi
): IStatisticsChartData => {
  const dayKeys = getDateKeys(params, weekStartingMonday)
  const dateFormat = dateFormats[params.duration]
  const displayedSports = sports.filter((sport) =>
    displayedSportsId.includes(sport.id)
  )
  const labels: string[] = []
  const datasets = getDatasets(displayedSports)
  const sportsId: Record<string, number> = {}
  displayedSports.map(
    (displayedSport) => (sportsId[displayedSport.label] = displayedSport.id)
  )

  dayKeys.map((key) => {
    const date: string = format(key, dateFormat)
    labels.push(date)
    datasetKeys.map((datasetKey) => {
      datasets[datasetKey].map((dataset) => {
        dataset.data.push(
          apiStats !== {} &&
            date in apiStats &&
            sportsId[dataset.label] in apiStats[date]
            ? apiStats[date][sportsId[dataset.label]][datasetKey]
            : 0
        )
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
  timeFrame: string,
  weekStartingMonday: boolean
): IStatisticsDateParams => {
  const weekStartsOn = weekStartingMonday ? 1 : 0
  const start =
    timeFrame === 'year'
      ? startOfYear(subYears(date, 9))
      : timeFrame === 'week'
      ? startOfWeek(subMonths(date, 2), { weekStartsOn })
      : startOfMonth(subMonths(date, 11)) // month
  const end =
    timeFrame === 'year'
      ? endOfYear(date)
      : timeFrame === 'week'
      ? endOfWeek(date, { weekStartsOn })
      : endOfMonth(date) // month
  return {
    duration: timeFrame,
    end,
    start,
  }
}

export const updateChartParams = (
  chartParams: IStatisticsDateParams,
  backward: boolean,
  weekStartingMonday: boolean
): IStatisticsDateParams => {
  const { duration, start, end } = chartParams
  const weekStartsOn = weekStartingMonday ? 1 : 0
  return {
    duration,
    end:
      duration === 'year'
        ? endOfYear(backward ? subYears(end, 1) : addYears(end, 1))
        : duration === 'week'
        ? endOfWeek(backward ? subWeeks(end, 1) : addWeeks(end, 1), {
            weekStartsOn,
          })
        : endOfMonth(backward ? subMonths(end, 1) : addMonths(end, 1)),
    start:
      duration === 'year'
        ? startOfYear(backward ? subYears(start, 1) : addYears(start, 1))
        : duration === 'week'
        ? startOfWeek(backward ? subWeeks(start, 1) : addWeeks(start, 1), {
            weekStartsOn,
          })
        : startOfMonth(backward ? subMonths(start, 1) : addMonths(start, 1)),
  }
}
