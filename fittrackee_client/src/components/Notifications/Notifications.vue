<template>
  <div id="notifications" v-if="authUser.username">
    <div class="no-notifications box" v-if="notifications.length === 0">
      {{ $t('notifications.NO_NOTIFICATIONS') }}
    </div>
    <template v-else>
      <NotificationDetail
        v-for="notification in notifications"
        :key="notification"
        :auth-user="authUser"
        :notification="notification"
        @reload="reload"
        @updateReadStatus="updateNotificationReadStatus"
      />
      <Pagination
        v-if="pagination.page"
        path="/notifications"
        :pagination="pagination"
        :query="query"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
  import { ComputedRef, computed, reactive, onBeforeMount, watch } from 'vue'
  import { LocationQuery, useRoute } from 'vue-router'

  import Pagination from '@/components/Common/Pagination.vue'
  import NotificationDetail from '@/components/Notifications/NotificationDetail.vue'
  import { AUTH_USER_STORE, NOTIFICATIONS_STORE } from '@/store/constants'
  import { INotification, INotificationsPayload } from '@/types/notifications'
  import { IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'

  const store = useStore()
  const route = useRoute()

  const authUser: ComputedRef<IAuthUserProfile> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.AUTH_USER_PROFILE]
  )
  const notifications: ComputedRef<INotification[]> = computed(
    () => store.getters[NOTIFICATIONS_STORE.GETTERS.NOTIFICATIONS]
  )
  const pagination: ComputedRef<INotification[]> = computed(
    () => store.getters[NOTIFICATIONS_STORE.GETTERS.PAGINATION]
  )
  let query: INotificationsPayload = reactive(
    getNotificationsQuery(route.query)
  )

  onBeforeMount(() => loadNotifications(query))

  function getNotificationsQuery(
    newQuery: LocationQuery
  ): INotificationsPayload {
    const payload: INotificationsPayload = {}
    if ('page' in newQuery) {
      payload.page = +newQuery.page
    }
    if ('type' in newQuery) {
      payload.type = newQuery.type
    }
    if ('unread' in newQuery) {
      payload.read_status =
        newQuery.unread === null || newQuery.unread === ''
          ? false
          : !newQuery.unread
    }
    return payload
  }

  function reload() {
    setTimeout(() => {
      loadNotifications(query)
    }, 500)
  }
  function loadNotifications(queryParams: INotificationsPayload) {
    store.dispatch(NOTIFICATIONS_STORE.ACTIONS.GET_NOTIFICATIONS, queryParams)
  }
  function updateNotificationReadStatus(payload) {
    store.dispatch(NOTIFICATIONS_STORE.ACTIONS.UPDATE_STATUS, {
      ...payload,
      currentQuery: query,
    })
  }

  watch(
    () => route.query,
    (newQuery: LocationQuery) => {
      query = getNotificationsQuery(newQuery)
      loadNotifications(query)
    }
  )
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';
  #notifications {
    .no-notifications {
      padding: $default-padding;
      text-align: center;
    }
  }
</style>
