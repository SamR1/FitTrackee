import { Selector } from 'testcafe'

const TEST_URL = process.env.TEST_URL


fixture('/').page(`${TEST_URL}/`)

test('users should be able to view the \'/\' page', async t => {

  await t
    .navigateTo(TEST_URL)
    .expect(Selector('A').withText('Dashboard').exists).ok()

})
