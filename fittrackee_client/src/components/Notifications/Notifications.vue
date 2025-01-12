<template>
  <div id="notifications" v-if="authUser.username">
    <div class="no-notifications box" v-if="notifications.length === 0">
      {{ $t('notifications.NO_NOTIFICATIONS') }}
    </div>
    <template v-else>
      <button class="mark-all-action" @click="markAllAsRead">
        {{ $t('notifications.MARK_ALL_AS_READ') }}
      </button>
      <NotificationDetail
        v-for="notification in notifications"
        :key="notification.id"
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
    <div class="preferences-link">
      <router-link to="/profile/edit/notifications">
        {{ $t('user.PROFILE.EDIT_NOTIFICATION_PREFERENCES') }}
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { computed, reactive, onUnmounted, watch, onBeforeMount } from 'vue'
  import type { ComputedRef, Reactive } from 'vue'
  import { useRoute } from 'vue-router'
  import type { LocationQuery } from 'vue-router'

  import Pagination from '@/components/Common/Pagination.vue'
  import NotificationDetail from '@/components/Notifications/NotificationDetail.vue'
  import useAuthUser from '@/composables/useAuthUser'
  import { NOTIFICATIONS_STORE } from '@/store/constants'
  import type { IPagination } from '@/types/api'
  import type {
    INotification,
    INotificationsPayload,
    TNotificationType,
    INotificationPayload,
  } from '@/types/notifications'
  import { useStore } from '@/use/useStore'

  const store = useStore()
  const route = useRoute()

  const { authUser, isAuthUserSuspended } = useAuthUser()

  let query: Reactive<INotificationsPayload> = reactive(
    getNotificationsQuery(route.query)
  )

  const notifications: ComputedRef<INotification[]> = computed(
    () => store.getters[NOTIFICATIONS_STORE.GETTERS.NOTIFICATIONS]
  )
  const pagination: ComputedRef<IPagination> = computed(
    () => store.getters[NOTIFICATIONS_STORE.GETTERS.PAGINATION]
  )

  function getNotificationsQuery(
    newQuery: LocationQuery
  ): INotificationsPayload {
    const payload: INotificationsPayload = {}
    if ('page' in newQuery && newQuery.page) {
      payload.page = +newQuery.page
    }
    if ('type' in newQuery && newQuery.type) {
      payload.type = newQuery.type as TNotificationType
    }
    if ('status' in newQuery && newQuery.status === 'unread') {
      payload.status = 'unread'
    }
    return payload
  }
  function reload() {
    setTimeout(() => {
      loadNotifications(query)
    }, 500)
  }
  function loadNotifications(queryParams: INotificationsPayload) {
    if (!isAuthUserSuspended.value) {
      store.dispatch(NOTIFICATIONS_STORE.ACTIONS.GET_NOTIFICATIONS, queryParams)
    }
  }
  function updateNotificationReadStatus(payload: INotificationPayload) {
    store.dispatch(NOTIFICATIONS_STORE.ACTIONS.UPDATE_STATUS, {
      ...payload,
      currentQuery: query,
    })
  }
  function markAllAsRead() {
    store.dispatch(NOTIFICATIONS_STORE.ACTIONS.MARK_ALL_AS_READ, query)
  }

  watch(
    () => route.query,
    (newQuery: LocationQuery) => {
      query = getNotificationsQuery(newQuery)
      loadNotifications(query)
    }
  )

  watch(
    () => isAuthUserSuspended.value,
    (isSuspended: boolean) => {
      if (!isSuspended) {
        loadNotifications(query)
      }
    }
  )

  onBeforeMount(() => loadNotifications(query))
  onUnmounted(() => {
    store.commit(NOTIFICATIONS_STORE.MUTATIONS.EMPTY_NOTIFICATIONS)
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';
  #notifications {
    .no-notifications {
      padding: $default-padding;
      text-align: center;
    }
    .mark-all-action {
      border: none;
      box-shadow: none;
      font-style: italic;
      font-weight: initial;
      margin-top: $default-margin;
      padding-top: 0;
      &:hover {
        background-color: initial;
        color: var(--app-color);
      }
    }
  }
  .preferences-link {
    font-size: 0.9em;
    font-style: italic;
    margin-left: $default-margin;
  }
</style>
