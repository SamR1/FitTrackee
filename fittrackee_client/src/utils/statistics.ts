import { format } from 'date-fns'

import { genericObject } from '@/types/generic'
import { ISport } from '@/types/sports'
import {
  IStatisticsChartData,
  IStatisticsChartDataset,
  IStatisticsDateParams,
  TDatasetKeys,
  TStatisticsDatasets,
  TStatisticsFromApi,
} from '@/types/statistics'
import { incrementDate, startDate } from '@/utils/dates'

// date format from api
const dateFormats: genericObject = {
  week: 'yyyy-MM-dd',
  month: 'yyyy-MM',
  year: 'yyyy',
}

export const datasetKeys: TDatasetKeys[] = [
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

export const sportColors: Record<string, string> = {
  'Cycling (Sport)': '#55A8A3',
  'Cycling (Transport)': '#98C3A9',
  Hiking: '#D0838A',
  'Mountain Biking': '#ECC77E',
  Running: '#926692',
  Walking: '#929292',
}

const getStatisticsChartDataset = (
  sportLabel: string,
  color: string
): IStatisticsChartDataset =>
  Object.assign(
    {},
    {
      label: sportLabel,
      backgroundColor: [color],
      data: [],
    }
  )

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
    displayedSportsId.length == 0 ? true : displayedSportsId.includes(sport.id)
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
