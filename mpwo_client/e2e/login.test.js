import { Selector } from 'testcafe'

import { TEST_URL } from './utils'

const randomstring = require('randomstring')

const username = randomstring.generate(8)
const email = `${username}@test.com`
const password = 'lentghOk'


// eslint-disable-next-line no-undef
fixture('/login').page(`${TEST_URL}/login`)

test('should display the registration form', async t => {
  await t
    .navigateTo(`${TEST_URL}/login`)
    .expect(Selector('H1').withText('Login').exists).ok()
    .expect(Selector('form').exists).ok()
    .expect(Selector('input[name="username"]').exists).notOk()
    .expect(Selector('input[name="email"]').exists).ok()
    .expect(Selector('input[name="password"]').exists).ok()
    .expect(Selector('input[name="passwordConf"]').exists).notOk()
})

test('should throw an error if the user is not registered', async t => {

  // register user with duplicate user name
  await t
    .navigateTo(`${TEST_URL}/login`)
    .typeText('input[name="email"]', email)
    .typeText('input[name="password"]', password)
    .click(Selector('input[type="submit"]'))

  // assert user registration failed
  await t
    .expect(Selector('H1').withText('Login').exists).ok()
    .expect(Selector('H1').withText('Dashboard').exists).notOk()
    .expect(Selector('code').withText(
      'Invalid credentials.').exists).ok()
})

test('should allow a user to login', async t => {

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

    // assert user is redirected to '/'
  await t
    .expect(Selector('H1').withText('Login').exists).notOk()
    .expect(Selector('H1').withText('Dashboard').exists).ok()

})

test('should throw an error if the email is invalid', async t => {

  // register user with duplicate user name
  await t
    .navigateTo(`${TEST_URL}/login`)
    .typeText('input[name="email"]', `${email}2`)
    .typeText('input[name="password"]', password)
    .click(Selector('input[type="submit"]'))

  // assert user registration failed
  await t
    .expect(Selector('H1').withText('Login').exists).ok()
    .expect(Selector('H1').withText('Dashboard').exists).notOk()
    .expect(Selector('code').withText(
      'Invalid credentials.').exists).ok()
})

test('should throw an error if the password is invalid', async t => {

  // register user with duplicate user name
  await t
    .navigateTo(`${TEST_URL}/login`)
    .typeText('input[name="email"]', email)
    .typeText('input[name="password"]', `${password}2`)
    .click(Selector('input[type="submit"]'))

  // assert user registration failed
  await t
    .expect(Selector('H1').withText('Login').exists).ok()
    .expect(Selector('H1').withText('Dashboard').exists).notOk()
    .expect(Selector('code').withText(
      'Invalid credentials.').exists).ok()
})
