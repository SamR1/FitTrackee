import { describe, expect, it } from 'vitest'

import { TUserRole } from '../../../src/types/user'

import { getNotificationTypes } from '@/utils/notifications'

describe('getNotificationTypes', () => {
  it('it returns notification type when user has no administration rights', () => {
    const roles: TUserRole[] = ['user', 'moderator']

    roles.forEach((role) => {
      expect(getNotificationTypes(role)).toStrictEqual([
        'follow',
        'follow_request',
        'follow_request_approved',
        'workout_like',
        'workout_comment',
        'comment_reply',
        'comment_like',
        'mention',
      ])
    })
  })
  it('it returns notification type when user has administration rights', () => {
    const roles: TUserRole[] = ['admin', 'owner']

    roles.forEach((role) => {
      expect(getNotificationTypes(role)).toStrictEqual([
        'follow',
        'follow_request',
        'follow_request_approved',
        'workout_like',
        'workout_comment',
        'comment_reply',
        'comment_like',
        'mention',
        'account_creation',
      ])
    })
  })
})
