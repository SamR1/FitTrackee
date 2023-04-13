<template>
  <div class="follow-requests">
    <div v-if="followRequests.length > 0">
      <div
        v-for="user in followRequests"
        :key="user.username"
        class="box follow-request"
      >
        <UserPicture :user="user" />
        <div class="user-name">
          <router-link :to="`/users/${user.username}?from=users`">
            {{ user.username }}
          </router-link>
        </div>
        <div class="follow-requests-actions">
          <button @click="updateFollowRequest(user.username, 'accept')">
            <i class="fa fa-check" aria-hidden="true" />
          </button>
          <button
            @click="updateFollowRequest(user.username, 'reject')"
            class="danger"
          >
            <i class="fa fa-times" aria-hidden="true" />
          </button>
        </div>
      </div>
      <Pagination
        path="/profile/follow-requests"
        :pagination="pagination"
        :query="{}"
      />
    </div>
    <p v-else class="no-follow-requests">
      {{ $t('user.RELATIONSHIPS.NO_FOLLOW_REQUESTS') }}
    </p>
    <div class="profile-buttons">
      <button @click="$router.push('/')">{{ $t('common.HOME') }}</button>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { computed, ComputedRef, onBeforeMount, onUnmounted, watch } from 'vue'
  import { LocationQuery, useRoute } from 'vue-router'

  import Pagination from '@/components/Common/Pagination.vue'
  import UserPicture from '@/components/User/UserPicture.vue'
  import { AUTH_USER_STORE, USERS_STORE } from '@/store/constants'
  import { IPagination } from '@/types/api'
  import {
    IUserProfile,
    IFollowRequestsPayload,
    TFollowRequestAction,
  } from '@/types/user'
  import { useStore } from '@/use/useStore'

  const route = useRoute()
  const store = useStore()
  const payload: IFollowRequestsPayload = {
    page: 1,
  }
  const followRequests: ComputedRef<IUserProfile[]> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.FOLLOW_REQUESTS]
  )
  const pagination: ComputedRef<IPagination> = computed(
    () => store.getters[USERS_STORE.GETTERS.USERS_PAGINATION]
  )

  onBeforeMount(() => loadFollowRequests(getQuery(route.query)))

  function loadFollowRequests(payload: IFollowRequestsPayload) {
    store.dispatch(AUTH_USER_STORE.ACTIONS.GET_FOLLOW_REQUESTS, payload)
  }
  function updateFollowRequest(username: string, action: TFollowRequestAction) {
    store.dispatch(AUTH_USER_STORE.ACTIONS.UPDATE_FOLLOW_REQUESTS, {
      username,
      action,
    })
  }
  function getQuery(query: LocationQuery): IFollowRequestsPayload {
    payload.page = query.page ? +query.page : 1
    return payload
  }

  onUnmounted(() =>
    store.commit(AUTH_USER_STORE.MUTATIONS.UPDATE_FOLLOW_REQUESTS, [])
  )

  watch(
    () => route.query,
    (newQuery: LocationQuery) => {
      if (route.path === '/profile/follow-requests') {
        store.dispatch(
          AUTH_USER_STORE.ACTIONS.GET_FOLLOW_REQUESTS,
          getQuery(newQuery)
        )
      }
    }
  )
</script>

<style scoped lang="scss">
  @import '~@/scss/vars.scss';

  .follow-requests {
    .follow-request {
      display: flex;
      ::v-deep(.user-picture) {
        min-width: 15%;
        img {
          height: 60px;
          width: 60px;
        }
        .no-picture {
          font-size: 3.8em;
        }
      }

      .user-name {
        display: flex;
        flex-direction: column;
        justify-content: center;
        flex-grow: 2;
      }

      .follow-requests-actions {
        display: flex;
        flex-direction: column;
        gap: $default-padding;

        button {
          width: 60px;
        }
      }
    }

    @media screen and (max-width: $small-limit) {
      .follow-request {
        flex-direction: column;
        .user-name {
          padding-bottom: $default-padding;
        }
        .follow-requests-actions {
          flex-direction: row;
          button {
            flex-grow: 1;
          }
        }
      }
    }
  }
</style>
