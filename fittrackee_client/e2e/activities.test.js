import { Selector } from 'testcafe'

import { TEST_URL } from './utils'

const randomstring = require('randomstring')

const username = randomstring.generate(8)
const email = `${username}@test.com`
const password = 'lentghOk'


// eslint-disable-next-line no-undef
fixture('/activities').page(`${TEST_URL}/activities`)

test('standard user should be able to add a workout (w/o gpx)', async t => {
  await t
    .navigateTo(`${TEST_URL}/register`)
    .typeText('input[name="username"]', username)
    .typeText('input[name="email"]', email)
    .typeText('input[name="password"]', password)
    .typeText('input[name="passwordConf"]', password)
    .click(Selector('input[type="submit"]'))

  await t
    .navigateTo(`${TEST_URL}/activities/add`)
    .expect(Selector('H1').withText('Dashboard').exists).notOk()
    .expect(Selector('H2').withText('Add a workout').exists).ok()
    .click(Selector('input[name="withoutGpx"]'))
    .click(Selector('select').filter('[name="sport_id"]'))
    .click(Selector('option').filter('[value="1"]'))
    .typeText('input[name="activity_date"]', '2018-12-20')
    .typeText('input[name="activity_time"]', '14:05')
    .typeText('input[name="duration"]', '01:00:00')
    .typeText('input[name="distance"]', '10')
    .click(Selector('input[type="submit"]'))

  // pb w/ chromium to check
  // await t
  //   .expect(Selector('H1').withText('Dashboard').exists).notOk()
  //   .expect(Selector('H1').withText('Activity').exists).ok()

})

