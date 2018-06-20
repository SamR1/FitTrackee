import { Selector } from 'testcafe'

import { TEST_URL } from './utils'

const randomstring = require('randomstring')

const username = randomstring.generate(8)
const email = `${username}@test.com`
const password = 'lentghOk'

// database must be initialiazed
const adminEmail = 'admin@example.com'
const adminPassword = 'mpwoadmin'


// eslint-disable-next-line no-undef
fixture('/admin').page(`${TEST_URL}/admin`)

test('standard user should not be able to access admin page', async t => {
  // register user
  await t
    .navigateTo(`${TEST_URL}/register`)
    .typeText('input[name="username"]', username)
    .typeText('input[name="email"]', email)
    .typeText('input[name="password"]', password)
    .typeText('input[name="password_conf"]', password)
    .click(Selector('input[type="submit"]'))

  await t
    .navigateTo(`${TEST_URL}/admin`)
    .expect(Selector('H1').withText('Access denied').exists).ok()
    .expect(Selector('H1').withText('Dashboard').exists).notOk()

})

test('admin should be able to access admin page', async t => {
  // admin login
  await t
    .navigateTo(`${TEST_URL}/login`)
    .typeText('input[name="email"]', adminEmail)
    .typeText('input[name="password"]', adminPassword)
    .click(Selector('input[type="submit"]'))

  await t
    .navigateTo(`${TEST_URL}/admin`)
    .expect(Selector('H1').withText('Access denied').exists).notOk()
    .expect(Selector('H1').withText('Administration').exists).ok()
    .expect(Selector('.admin-items').withText('Sports').exists).ok()

})
