<template>
  <div class="relationships">
    <div v-if="relationships.length > 0">
      <div class="user-relationships">
        <UserCard
          v-for="user in relationships"
          :key="user.username"
          :authUser="authUser"
          :user="user"
          from="relationship"
        />
      </div>
      <Pagination
        :path="`/profile/${relationship}`"
        :pagination="pagination"
        :query="{}"
      />
    </div>
    <p v-else class="no-relationships">
      {{ $t(`user.RELATIONSHIPS.NO_${relationship.toUpperCase()}`) }}
    </p>
    <div class="profile-buttons">
      <button
        @click="
          $route.path.startsWith('/profile')
            ? $router.push('/profile')
            : $router.push(`/users/${user.username}`)
        "
      >
        {{ $t('user.PROFILE.BACK_TO_PROFILE') }}
      </button>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { computed, onBeforeMount, watch, onUnmounted, toRefs } from 'vue'
  import type { ComputedRef } from 'vue'
  import { useRoute } from 'vue-router'
  import type { LocationQuery } from 'vue-router'

  import Pagination from '@/components/Common/Pagination.vue'
  import UserCard from '@/components/User/UserCard.vue'
  import useAuthUser from '@/composables/useAuthUser'
  import { USERS_STORE } from '@/store/constants'
  import type { IPagination } from '@/types/api'
  import type {
    IUserProfile,
    IUserRelationshipsPayload,
    TRelationships,
  } from '@/types/user'
  import { useStore } from '@/use/useStore'

  interface Props {
    user: IUserProfile
    relationship: TRelationships
  }
  const props = defineProps<Props>()
  const { relationship, user } = toRefs(props)

  const store = useStore()
  const route = useRoute()

  const { authUser } = useAuthUser()

  const payload: ComputedRef<IUserRelationshipsPayload> = computed(() => {
    return {
      username: user.value.username,
      relationship: relationship.value,
      page: 1,
    }
  })
  const relationships: ComputedRef<IUserProfile[]> = computed(
    () => store.getters[USERS_STORE.GETTERS.USER_RELATIONSHIPS]
  )
  const pagination: ComputedRef<IPagination> = computed(
    () => store.getters[USERS_STORE.GETTERS.USERS_PAGINATION]
  )

  function loadRelationships(payload: IUserRelationshipsPayload) {
    store.dispatch(USERS_STORE.ACTIONS.GET_RELATIONSHIPS, payload)
  }

  watch(
    () => route.path,
    (newPath: string) => {
      payload.value.page = pagination.value.page
      payload.value.relationship = newPath.includes('following')
        ? 'following'
        : 'followers'
      loadRelationships(payload.value)
    }
  )
  watch(
    () => route.query,
    (newQuery: LocationQuery, oldQuery: LocationQuery) => {
      if (newQuery.page !== oldQuery.page) {
        payload.value.page = newQuery.page ? +newQuery.page : 1
        loadRelationships(payload.value)
      }
    }
  )
  watch(
    () => user.value.following,
    () => {
      loadRelationships(payload.value)
    }
  )
  watch(
    () => user.value.followers,
    () => {
      loadRelationships(payload.value)
    }
  )

  onBeforeMount(() => loadRelationships(payload.value))
  onUnmounted(() => {
    store.dispatch(USERS_STORE.ACTIONS.EMPTY_RELATIONSHIPS)
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';

  .relationships {
    min-height: 40px;
    .user-relationships {
      display: flex;
      justify-content: space-between;
      flex-wrap: wrap;

      ::v-deep(.box) {
        width: 43%;
        @media screen and (max-width: $small-limit) {
          width: 100%;
        }
      }
    }
    .no-relationships {
      padding: 0 $default-padding * 0.5;
    }
  }
</style>
