import createI18n from '@/i18n'
import type { ITranslatedSport } from '@/types/sports'
import type { TUnit } from '@/types/units'
import type { ICardRecord, IRecord, IRecordsBySports } from '@/types/workouts'
import { formatDate, getDateFormat } from '@/utils/dates'
import { convertDistance, units } from '@/utils/units'

const { locale } = createI18n.global

export const formatRecord = (
  record: IRecord,
  tz: string,
  useImperialUnits: boolean,
  date_format: string
): Record<string, string | number> => {
  const distanceUnitFrom: TUnit = 'km'
  const distanceUnitTo: TUnit = useImperialUnits
    ? units[distanceUnitFrom].defaultTarget
    : distanceUnitFrom
  const ascentUnitFrom: TUnit = 'm'
  const ascentUnitTo: TUnit = useImperialUnits
    ? units[ascentUnitFrom].defaultTarget
    : ascentUnitFrom
  let value
  switch (record.record_type) {
    case 'AS':
    case 'MS':
      value = `${convertDistance(
        +record.value,
        distanceUnitFrom,
        distanceUnitTo,
        2
      )} ${distanceUnitTo}/h`
      break
    case 'FD':
      value = `${convertDistance(
        +record.value,
        distanceUnitFrom,
        distanceUnitTo,
        3
      )} ${distanceUnitTo}`
      break
    case 'HA':
      value = `${convertDistance(
        +record.value,
        ascentUnitFrom,
        ascentUnitTo,
        2
      )} ${ascentUnitTo}`
      break
    case 'LD':
      value = record.value
      break
    default:
      throw new Error(
        `Invalid record type, expected: "AS", "FD", "HA", "LD", "MD", got: "${record.record_type}"`
      )
  }
  return {
    workout_date: formatDate(record.workout_date, tz, date_format, false),
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
  useImperialUnits: boolean,
  display_ascent: boolean,
  date_format: string
): IRecordsBySports => {
  date_format = getDateFormat(date_format, locale.value)
  return records
    .filter((r) => (display_ascent ? true : r.record_type !== 'HA'))
    .reduce((sportList: IRecordsBySports, record) => {
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
          formatRecord(record, tz, useImperialUnits, date_format)
        )
      }
      return sportList
    }, {})
}
