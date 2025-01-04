<template>
  <div class="users-list">
    <div v-if="items.length > 0">
      <div v-for="user in items" :key="user.username" class="box user-item">
        <div class="item">
          <UserPicture :user="user" />
          <div class="user-name">
            <router-link :to="`/users/${user.username}?from=users`">
              {{ user.username }}
            </router-link>
          </div>
          <div v-if="user.blocked" class="blocked-user">
            <button @click="updateBlock(user.username, false)">
              {{ $t('buttons.UNBLOCK') }}
            </button>
          </div>
          <div v-else class="follow-requests-list-actions">
            <button @click="updateFollowRequest(user.username, 'accept')">
              <i class="fa fa-check" aria-hidden="true" />
              {{ $t('buttons.ACCEPT') }}
            </button>
            <button
              @click="updateFollowRequest(user.username, 'reject')"
              class="danger"
            >
              <i class="fa fa-times" aria-hidden="true" />
              {{ $t('buttons.REJECT') }}
            </button>
          </div>
        </div>
        <ErrorMessage
          v-if="errorMessages && updatedUser && updatedUser === user.username"
          :message="errorMessages"
          :no-margin="true"
        />
      </div>
    </div>
    <p v-else class="no-users-list">
      {{
        $t(
          itemType === 'follow-requests'
            ? 'user.RELATIONSHIPS.NO_FOLLOW_REQUESTS'
            : 'user.NO_USERS_FOUND'
        )
      }}
    </p>
    <Pagination
      v-if="pagination.total > 0"
      :path="`/profile/${itemType}`"
      :pagination="pagination"
      :query="{}"
    />
    <ErrorMessage
      v-if="errorMessages"
      :message="errorMessages"
      :no-margin="true"
    />
    <div class="profile-buttons">
      <button @click="$router.push('/')">{{ $t('common.HOME') }}</button>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { computed, onBeforeMount, onUnmounted, ref, toRefs, watch } from 'vue'
  import type { Ref, ComputedRef } from 'vue'
  import { useRoute } from 'vue-router'
  import type { LocationQuery } from 'vue-router'

  import Pagination from '@/components/Common/Pagination.vue'
  import UserPicture from '@/components/User/UserPicture.vue'
  import useApp from '@/composables/useApp.ts'
  import { AUTH_USER_STORE, USERS_STORE } from '@/store/constants'
  import type { IPagePayload, IPagination } from '@/types/api'
  import type {
    IUserProfile,
    TFollowRequestAction,
    IUserRelationshipActionPayload,
  } from '@/types/user'
  import { useStore } from '@/use/useStore'

  interface Props {
    itemType: string
  }
  const props = defineProps<Props>()
  const { itemType } = toRefs(props)

  const route = useRoute()
  const store = useStore()

  const { errorMessages } = useApp()

  const payload: IPagePayload = {
    page: 1,
  }

  const updatedUser: Ref<string | null> = ref(null)

  const items: ComputedRef<IUserProfile[]> = computed(
    () =>
      store.getters[
        AUTH_USER_STORE.GETTERS[
          itemType.value === 'follow-requests'
            ? 'FOLLOW_REQUESTS'
            : 'BLOCKED_USERS'
        ]
      ]
  )
  const pagination: ComputedRef<IPagination> = computed(
    () => store.getters[USERS_STORE.GETTERS.USERS_PAGINATION]
  )

  function loadItems(payload: IPagePayload) {
    store.dispatch(
      AUTH_USER_STORE.ACTIONS[
        itemType.value === 'follow-requests'
          ? 'GET_FOLLOW_REQUESTS'
          : 'GET_BLOCKED_USERS'
      ],
      payload
    )
  }
  function updateFollowRequest(username: string, action: TFollowRequestAction) {
    storeUser(username)
    store.dispatch(AUTH_USER_STORE.ACTIONS.UPDATE_FOLLOW_REQUESTS, {
      username,
      action,
      getFollowRequests: true,
    })
  }
  function updateBlock(username: string, block: boolean) {
    storeUser(username)
    const payload: IUserRelationshipActionPayload = {
      username,
      action: `${block ? '' : 'un'}block`,
      from: itemType.value,
      payload: getQuery(route.query),
    }
    store.dispatch(USERS_STORE.ACTIONS.UPDATE_RELATIONSHIP, payload)
  }
  function getQuery(query: LocationQuery): IPagePayload {
    payload.page = query.page ? +query.page : 1
    return payload
  }
  function storeUser(username: string) {
    updatedUser.value = username
  }

  watch(
    () => route.query,
    (newQuery: LocationQuery) => {
      if (route.path === '/profile/follow-requests') {
        store.dispatch(
          AUTH_USER_STORE.ACTIONS.GET_FOLLOW_REQUESTS,
          getQuery(newQuery)
        )
      }
      if (route.path === '/profile/blocked-users') {
        store.dispatch(
          AUTH_USER_STORE.ACTIONS.GET_BLOCKED_USERS,
          getQuery(newQuery)
        )
      }
    }
  )

  onBeforeMount(() => loadItems(getQuery(route.query)))
  onUnmounted(() => {
    store.commit(
      AUTH_USER_STORE.MUTATIONS[
        itemType.value === 'follow-requests'
          ? 'UPDATE_FOLLOW_REQUESTS'
          : 'UPDATE_BLOCKED_USERS'
      ],
      []
    )
  })
</script>

<style scoped lang="scss">
  @import '~@/scss/vars.scss';

  .users-list {
    .user-item {
      display: flex;
      flex-direction: column;
      .item {
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

        .blocked-user,
        .follow-requests-list-actions {
          button {
            text-transform: capitalize;
          }
        }

        .blocked-user {
          display: flex;
          flex-direction: column;
          justify-content: center;
        }

        .follow-requests-list-actions {
          display: flex;
          flex-direction: column;
          gap: $default-padding;

          button {
            display: flex;
            gap: $default-padding;

            .fa {
              line-height: 20px;
            }
          }
        }
      }

      @media screen and (max-width: $small-limit) {
        .item {
          ::v-deep(.user-picture) {
            margin-right: $default-margin;
            min-width: 40px;

            img {
              height: 48px;
              width: 48px;
            }

            .no-picture {
              font-size: 3em;
            }
          }

          .follow-request {
            .user-name {
              padding-left: $default-padding;
            }
          }
        }
      }
    }
  }
</style>
