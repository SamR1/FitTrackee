import { Selector } from 'testcafe'

import { TEST_URL } from './utils'


// eslint-disable-next-line no-undef
fixture('/').page(`${TEST_URL}/`)

test('users should be able to view the \'/\' page', async t => {

  await t
    .navigateTo(TEST_URL)
    .expect(Selector('A').withText('Dashboard').exists).ok()

})
