<template>
  <div class="relationships">
    <div v-if="user.is_remote" class="remote-user">
      <i18n-t keypath="user.USER_FROM_REMOTE_INSTANCE_ORIGINAL_LINK">
        <a :href="user.profile_link" target="_blank">
          {{ $t('common.HERE') }}
        </a>
        <i18n-t keypath="user.ONLY_USERS_FROM_THIS_INSTANCE_ARE_DISPLAYED">
          {{
            $t(
              `user.RELATIONSHIPS.${relationship
                .toUpperCase()
                .replace('S', '')}`,
              0
            )
          }}
        </i18n-t>
      </i18n-t>
    </div>
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
            : $router.push(`/users/${getUserName(user)}`)
        "
      >
        {{ $t('user.PROFILE.BACK_TO_PROFILE') }}
      </button>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import {
    ComputedRef,
    computed,
    onBeforeMount,
    watch,
    onUnmounted,
    toRefs,
  } from 'vue'
  import { LocationQuery, useRoute } from 'vue-router'

  import Pagination from '@/components/Common/Pagination.vue'
  import UserCard from '@/components/User/UserCard.vue'
  import { AUTH_USER_STORE, USERS_STORE } from '@/store/constants'
  import { IPagination } from '@/types/api'
  import {
    IAuthUserProfile,
    IUserProfile,
    IUserRelationshipsPayload,
    TRelationships,
  } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { getUserName } from '@/utils/user'

  interface Props {
    user: IUserProfile
    relationship: TRelationships
  }
  const props = defineProps<Props>()

  const store = useStore()
  const route = useRoute()

  const { relationship, user } = toRefs(props)
  const payload: IUserRelationshipsPayload = {
    username: getUserName(user.value),
    relationship: relationship.value,
    page: 1,
  }
  const authUser: ComputedRef<IAuthUserProfile> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.AUTH_USER_PROFILE]
  )
  const relationships: ComputedRef<IUserProfile[]> = computed(
    () => store.getters[USERS_STORE.GETTERS.USER_RELATIONSHIPS]
  )
  const pagination: ComputedRef<IPagination> = computed(
    () => store.getters[USERS_STORE.GETTERS.USERS_PAGINATION]
  )

  onBeforeMount(() => loadRelationships(payload))

  function loadRelationships(payload: IUserRelationshipsPayload) {
    store.dispatch(USERS_STORE.ACTIONS.GET_RELATIONSHIPS, payload)
  }

  onUnmounted(() => {
    store.dispatch(USERS_STORE.ACTIONS.EMPTY_RELATIONSHIPS)
  })

  watch(
    () => route.path,
    (newPath: string) => {
      payload.page = pagination.value.page
      payload.relationship = newPath.includes('following')
        ? 'following'
        : 'followers'
      loadRelationships(payload)
    }
  )
  watch(
    () => route.query,
    (newQuery: LocationQuery, oldQuery: LocationQuery) => {
      if (newQuery.page !== oldQuery.page) {
        payload.page = newQuery.page ? +newQuery.page : 1
        loadRelationships(payload)
      }
    }
  )
  watch(
    () => user.value.following,
    () => {
      loadRelationships(payload)
    }
  )
  watch(
    () => user.value.followers,
    () => {
      loadRelationships(payload)
    }
  )
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
        width: 40%;
        @media screen and (max-width: $small-limit) {
          width: 100%;
        }
      }
    }
    .no-relationships {
      padding: 0 $default-padding * 0.5;
    }
    .remote-user {
      padding: $default-padding * 0.5;

      a {
        text-decoration: underline;
      }
    }
  }
</style>
