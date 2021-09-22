import { ISport } from '@/types/sports'
import { IRecord, IRecordsBySports } from '@/types/workouts'
import { formatWorkoutDate, getDateWithTZ } from '@/utils/dates'

export const formatRecord = (
  record: IRecord,
  tz: string
): Record<string, string | number> => {
  let value
  switch (record.record_type) {
    case 'AS':
    case 'MS':
      value = `${record.value} km/h`
      break
    case 'FD':
      value = `${record.value} km`
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

export const getRecordsBySports = (
  records: IRecord[],
  sports: ISport[],
  tz: string
): IRecordsBySports =>
  records.reduce((sportList: IRecordsBySports, record) => {
    const sport = sports.find((s) => s.id === record.sport_id)
    if (sport && sport.label) {
      if (sportList[sport.label] === void 0) {
        sportList[sport.label] = {
          img: sport.img,
          records: [],
        }
      }
      sportList[sport.label].records.push(formatRecord(record, tz))
    }
    return sportList
  }, {})
