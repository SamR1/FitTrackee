import { ITranslatedSport } from '@/types/sports'
import { TUnit } from '@/types/units'
import { ICardRecord, IRecord, IRecordsBySports } from '@/types/workouts'
import { formatWorkoutDate, getDateWithTZ } from '@/utils/dates'
import { convertDistance, units } from '@/utils/units'

export const formatRecord = (
  record: IRecord,
  tz: string,
  useImperialUnits: boolean
): Record<string, string | number> => {
  const unitFrom: TUnit = 'km'
  const unitTo: TUnit = useImperialUnits
    ? units[unitFrom].defaultTarget
    : unitFrom
  let value
  switch (record.record_type) {
    case 'AS':
    case 'MS':
      value = `${convertDistance(
        +record.value,
        unitFrom,
        unitTo,
        2
      )} ${unitTo}/h`
      break
    case 'FD':
      value = `${convertDistance(+record.value, unitFrom, unitTo, 3)} ${unitTo}`
      break
    case 'LD':
      value = record.value
      break
    default:
      throw new Error(
        `Invalid record type, expected: "AS", "FD", "LD", "MD", got: "${record.record_type}"`
      )
  }
  return {
    workout_date: formatWorkoutDate(getDateWithTZ(record.workout_date, tz))
      .workout_date,
    workout_id: record.workout_id,
    id: record.id,
    record_type: record.record_type,
    value: value,
  }
}

export const sortRecords = (a: ICardRecord, b: ICardRecord): number => {
  const recordALabel = a.label.toLowerCase()
  const recordBLabel = b.label.toLowerCase()
  return recordALabel > recordBLabel ? 1 : recordALabel < recordBLabel ? -1 : 0
}

export const getRecordsBySports = (
  records: IRecord[],
  translatedSports: ITranslatedSport[],
  tz: string,
  useImperialUnits: boolean
): IRecordsBySports =>
  records.reduce((sportList: IRecordsBySports, record) => {
    const sport = translatedSports.find((s) => s.id === record.sport_id)
    if (sport && sport.label) {
      if (sportList[sport.translatedLabel] === void 0) {
        sportList[sport.translatedLabel] = {
          label: sport.label,
          color: sport.color,
          records: [],
        }
      }
      sportList[sport.translatedLabel].records.push(
        formatRecord(record, tz, useImperialUnits)
      )
    }
    return sportList
  }, {})
