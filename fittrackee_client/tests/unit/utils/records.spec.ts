import { assert, expect } from 'chai'

import { sports } from './constants'

import { formatRecord, getRecordsBySports } from '@/utils/records'

describe('formatRecord', () => {
  const testsParams = [
    {
      description: "return formatted record for 'Average speed'",
      inputParams: {
        record: {
          id: 9,
          record_type: 'AS',
          sport_id: 1,
          user: 'admin',
          value: 18,
          workout_date: 'Sun, 07 Jul 2019 08:00:00 GMT',
          workout_id: 'hvYBqYBRa7wwXpaStWR4V2',
        },
        timezone: 'Europe/Paris',
      },
      expected: {
        id: 9,
        record_type: 'AS',
        value: '18 km/h',
        workout_date: '2019/07/07',
        workout_id: 'hvYBqYBRa7wwXpaStWR4V2',
      },
    },
    {
      description: "return formatted record for 'Farest distance'",
      inputParams: {
        record: {
          id: 10,
          record_type: 'FD',
          sport_id: 1,
          user: 'admin',
          value: 18,
          workout_date: 'Sun, 07 Jul 2019 22:00:00 GMT',
          workout_id: 'hvYBqYBRa7wwXpaStWR4V2',
        },
        timezone: 'Europe/Paris',
      },
      expected: {
        id: 10,
        record_type: 'FD',
        value: '18 km',
        workout_date: '2019/07/08',
        workout_id: 'hvYBqYBRa7wwXpaStWR4V2',
      },
    },
    {
      description: "return formatted record for 'Longest duration'",
      inputParams: {
        record: {
          id: 11,
          record_type: 'LD',
          sport_id: 1,
          user: 'admin',
          value: '1:01:00',
          workout_date: 'Sun, 07 Jul 2019 08:00:00 GMT',
          workout_id: 'hvYBqYBRa7wwXpaStWR4V2',
        },
        timezone: 'Europe/Paris',
      },
      expected: {
        id: 11,
        record_type: 'LD',
        value: '1:01:00',
        workout_date: '2019/07/07',
        workout_id: 'hvYBqYBRa7wwXpaStWR4V2',
      },
    },
    {
      description: "return formatted record for 'Max. speed'",
      inputParams: {
        record: {
          id: 12,
          record_type: 'MS',
          sport_id: 1,
          user: 'admin',
          value: 18,
          workout_date: 'Sun, 07 Jul 2019 22:00:00 GMT',
          workout_id: 'hvYBqYBRa7wwXpaStWR4V2',
        },
        timezone: 'Europe/Paris',
      },
      expected: {
        id: 12,
        record_type: 'MS',
        value: '18 km/h',
        workout_date: '2019/07/08',
        workout_id: 'hvYBqYBRa7wwXpaStWR4V2',
      },
    },
  ]
  testsParams.map((testParams) => {
    it(testParams.description, () => {
      assert.deepEqual(
        formatRecord(
          testParams.inputParams.record,
          testParams.inputParams.timezone
        ),
        testParams.expected
      )
    })
  })
})

describe('formatRecord (invalid record type)', () => {
  it('it throws an error if record type is invalid', () => {
    expect(() =>
      formatRecord(
        {
          id: 12,
          record_type: 'M',
          sport_id: 1,
          user: 'admin',
          value: 18,
          workout_date: 'Sun, 07 Jul 2019 22:00:00 GMT',
          workout_id: 'hvYBqYBRa7wwXpaStWR4V2',
        },
        'Europe/Paris'
      )
    ).to.throw(
      'Invalid record type, expected: "AS", "FD", "LD", "MD", got: "M"'
    )
  })
})

describe('getRecordsBySports', () => {
  const testsParams = [
    {
      description: 'returns empty object if no records',
      input: {
        records: [],
        tz: 'Europe/Paris',
      },
      expected: {},
    },
    {
      description: 'returns record grouped by Sport',
      input: {
        records: [
          {
            id: 9,
            record_type: 'AS',
            sport_id: 1,
            user: 'admin',
            value: 18,
            workout_date: 'Sun, 07 Jul 2019 08:00:00 GMT',
            workout_id: 'hvYBqYBRa7wwXpaStWR4V2',
          },
        ],
        tz: 'Europe/Paris',
      },
      expected: {
        'Cycling (Sport)': {
          img: '/img/sports/cycling-sport.png',
          records: [
            {
              id: 9,
              record_type: 'AS',
              value: '18 km/h',
              workout_date: '2019/07/07',
              workout_id: 'hvYBqYBRa7wwXpaStWR4V2',
            },
          ],
        },
      },
    },
    {
      description: 'returns record grouped by Sport',
      input: {
        records: [
          {
            id: 9,
            record_type: 'AS',
            sport_id: 1,
            user: 'admin',
            value: 18,
            workout_date: 'Sun, 07 Jul 2019 08:00:00 GMT',
            workout_id: 'hvYBqYBRa7wwXpaStWR4V2',
          },
          {
            id: 10,
            record_type: 'FD',
            sport_id: 2,
            user: 'admin',
            value: 18,
            workout_date: 'Sun, 07 Jul 2019 22:00:00 GMT',
            workout_id: 'n6JcLPQt3QtZWFfiSnYm4C',
          },
          {
            id: 12,
            record_type: 'MS',
            sport_id: 1,
            user: 'admin',
            value: 18,
            workout_date: 'Sun, 07 Jul 2019 08:00:00 GMT',
            workout_id: 'hvYBqYBRa7wwXpaStWR4V2',
          },
        ],
        tz: 'Europe/Paris',
      },
      expected: {
        'Cycling (Sport)': {
          img: '/img/sports/cycling-sport.png',
          records: [
            {
              id: 9,
              record_type: 'AS',
              value: '18 km/h',
              workout_date: '2019/07/07',
              workout_id: 'hvYBqYBRa7wwXpaStWR4V2',
            },
            {
              id: 12,
              record_type: 'MS',
              value: '18 km/h',
              workout_date: '2019/07/07',
              workout_id: 'hvYBqYBRa7wwXpaStWR4V2',
            },
          ],
        },
        'Cycling (Transport)': {
          img: '/img/sports/cycling-transport.png',
          records: [
            {
              id: 10,
              record_type: 'FD',
              value: '18 km',
              workout_date: '2019/07/08',
              workout_id: 'n6JcLPQt3QtZWFfiSnYm4C',
            },
          ],
        },
      },
    },
  ]
  testsParams.map((testParams) =>
    it(testParams.description, () => {
      assert.deepEqual(
        getRecordsBySports(
          testParams.input.records,
          sports,
          testParams.input.tz
        ),
        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
        // @ts-ignore
        testParams.expected
      )
    })
  )
})
