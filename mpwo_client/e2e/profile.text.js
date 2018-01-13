import { Selector } from 'testcafe'

import { TEST_URL } from './utils'

const randomstring = require('randomstring')

const username = randomstring.generate(8)
const email = `${username}@test.com`
const password = 'lentghOk'


// eslint-disable-next-line no-undef
fixture('/profile').page(`${TEST_URL}/profile`)

test('should be able to access his profile page', async t => {
  // register user
  await t
    .navigateTo(`${TEST_URL}/register`)
    .typeText('input[name="username"]', username)
    .typeText('input[name="email"]', email)
    .typeText('input[name="password"]', password)
    .typeText('input[name="passwordConf"]', password)
    .click(Selector('input[type="submit"]'))

  await t
    .navigateTo(`${TEST_URL}/logout`)
    .navigateTo(`${TEST_URL}/login`)
    .expect(Selector('H1').withText('Login').exists).ok()
    .typeText('input[name="email"]', email)
    .typeText('input[name="password"]', password)
    .click(Selector('input[type="submit"]'))

  await t
    .navigateTo(`${TEST_URL}/profile`)
    .expect(Selector('H1').withText('Login').exists).notOk()
    .expect(Selector('H1').withText('Dashboard').exists).notOk()
    .expect(Selector('H1').withText('Profile').exists).ok()
    .expect(Selector('.userName').withText(username).exists).ok()

})
