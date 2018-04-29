import { Selector } from 'testcafe'

import { TEST_URL } from './utils'

// database must be initialiazed
const adminEmail = 'admin@example.com'
const adminPassword = 'mpwoadmin'


// eslint-disable-next-line no-undef
fixture('/admin/sports').page(`${TEST_URL}/admin/sports`)

test('admin should be able to access sports administration page', async t => {
  // admin login
  await t
    .navigateTo(`${TEST_URL}/login`)
    .typeText('input[name="email"]', adminEmail)
    .typeText('input[name="password"]', adminPassword)
    .click(Selector('input[type="submit"]'))

  await t
    .navigateTo(`${TEST_URL}/admin/sports`)
    .expect(Selector('H1').withText('Administration - Sports').exists).ok()
    .expect(Selector('.sport-items').withText('Hiking').exists).ok()

})
