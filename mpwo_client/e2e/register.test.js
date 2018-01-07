import { Selector } from 'testcafe'

import { TEST_URL } from './utils'

const randomstring = require('randomstring')

let username = randomstring.generate(8)
const email = `${username}@test.com`
const password = 'lentghOk'


// eslint-disable-next-line no-undef
fixture('/register').page(`${TEST_URL}/register`)

test('should display the registration form', async t => {
  await t
    .navigateTo(`${TEST_URL}/register`)
    .expect(Selector('H1').withText('Register').exists).ok()
    .expect(Selector('form').exists).ok()
    .expect(Selector('input[name="username"]').exists).ok()
    .expect(Selector('input[name="email"]').exists).ok()
    .expect(Selector('input[name="password"]').exists).ok()
    .expect(Selector('input[name="passwordConf"]').exists).ok()
})

test('should allow a user to register', async t => {

  // register user
  await t
    .navigateTo(`${TEST_URL}/register`)
    .expect(Selector('H1').withText('Register').exists).ok()
    .typeText('input[name="username"]', username)
    .typeText('input[name="email"]', email)
    .typeText('input[name="password"]', password)
    .typeText('input[name="passwordConf"]', password)
    .click(Selector('input[type="submit"]'))

  // assert user is redirected to '/'
  await t
    .expect(Selector('H1').withText('Dashboard').exists).ok()
    .expect(Selector('H1').withText('Register').exists).notOk()
})

test('should throw an error if the username is taken', async t => {

  // register user with duplicate user name
  await t
    .navigateTo(`${TEST_URL}/register`)
    .typeText('input[name="username"]', username)
    .typeText('input[name="email"]', `${email}2`)
    .typeText('input[name="password"]', password)
    .typeText('input[name="passwordConf"]', password)
    .click(Selector('input[type="submit"]'))

  // assert user registration failed
  await t
    .expect(Selector('H1').withText('Register').exists).ok()
    .expect(Selector('H1').withText('Dashboard').exists).notOk()
    .expect(Selector('code').withText(
      'Sorry. That user already exists.').exists).ok()
})

username = randomstring.generate(8)

test('should throw an error if the email is taken', async t => {

  // register user with duplicate email
  await t
    .navigateTo(`${TEST_URL}/register`)
    .typeText('input[name="username"]', `${username}2`)
    .typeText('input[name="email"]', email)
    .typeText('input[name="password"]', password)
    .typeText('input[name="passwordConf"]', password)
    .click(Selector('input[type="submit"]'))

  // assert user registration failed
  await t
    .expect(Selector('H1').withText('Register').exists).ok()
    .expect(Selector('H1').withText('Dashboard').exists).notOk()
    .expect(Selector('code').withText(
      'Sorry. That user already exists.').exists).ok()
})

test('should throw an error if the username is too short', async t => {

  const shortUsername = 'a'

  // register user with duplicate email
  await t
    .navigateTo(`${TEST_URL}/register`)
    .typeText('input[name="username"]', `${shortUsername}`)
    .typeText('input[name="email"]', email)
    .typeText('input[name="password"]', password)
    .typeText('input[name="passwordConf"]', password)
    .click(Selector('input[type="submit"]'))

  // assert user registration failed
  await t
    .expect(Selector('H1').withText('Register').exists).ok()
    .expect(Selector('H1').withText('Dashboard').exists).notOk()
    .expect(Selector('code').withText(
      'Username: 3 to 12 characters required.').exists).ok()
})

test('should throw an error if the user is too long', async t => {

  const longUsername = randomstring.generate(20)

  // register user with duplicate email
  await t
    .navigateTo(`${TEST_URL}/register`)
    .typeText('input[name="username"]', `${longUsername}`)
    .typeText('input[name="email"]', email)
    .typeText('input[name="password"]', password)
    .typeText('input[name="passwordConf"]', password)
    .click(Selector('input[type="submit"]'))

  // assert user registration failed
  await t
    .expect(Selector('H1').withText('Register').exists).ok()
    .expect(Selector('H1').withText('Dashboard').exists).notOk()
    .expect(Selector('code').withText(
      'Username: 3 to 12 characters required.').exists).ok()
})

test('should throw an error if the email is invalid', async t => {

  const invalidEmail = `${username}@test`

  // register user with duplicate email
  await t
    .navigateTo(`${TEST_URL}/register`)
    .typeText('input[name="username"]', username)
    .typeText('input[name="email"]', invalidEmail)
    .typeText('input[name="password"]', password)
    .typeText('input[name="passwordConf"]', password)
    .click(Selector('input[type="submit"]'))

  // assert user registration failed
  await t
    .expect(Selector('H1').withText('Register').exists).ok()
    .expect(Selector('H1').withText('Dashboard').exists).notOk()
    .expect(Selector('code').withText(
      'Valid email must be provided.').exists).ok()
})

test('should throw an error if passwords don\'t match', async t => {

  // register user with duplicate email
  await t
    .navigateTo(`${TEST_URL}/register`)
    .typeText('input[name="username"]', username)
    .typeText('input[name="email"]', email)
    .typeText('input[name="password"]', password)
    .typeText('input[name="passwordConf"]', `${password}2`)
    .click(Selector('input[type="submit"]'))

  // assert user registration failed
  await t
    .expect(Selector('H1').withText('Register').exists).ok()
    .expect(Selector('H1').withText('Dashboard').exists).notOk()
    .expect(Selector('code').withText(
      'Password and password confirmation don\'t match.').exists).ok()
})

test('should throw an error if the password is too short', async t => {

  const invalidPassword = '1234567'

  // register user with duplicate email
  await t
    .navigateTo(`${TEST_URL}/register`)
    .typeText('input[name="username"]', username)
    .typeText('input[name="email"]', email)
    .typeText('input[name="password"]', invalidPassword)
    .typeText('input[name="passwordConf"]', invalidPassword)
    .click(Selector('input[type="submit"]'))

  // assert user registration failed
  await t
    .expect(Selector('H1').withText('Register').exists).ok()
    .expect(Selector('H1').withText('Dashboard').exists).notOk()
    .expect(Selector('code').withText(
      'Password: 8 characters required.').exists).ok()
})
