<template>
  <div id="user" class="view" v-if="user.username">
    <UserHeader :authUser="authUser" :user="user" />
    <div class="box">
      <router-view
        v-if="$route.path.includes('follow')"
        :authUser="authUser"
        :user="user"
      />
      <UserInfos
        v-else
        :authUser="authUser"
        :user="user"
        :from-admin="fromAdmin"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
  import { computed, onBeforeMount, onBeforeUnmount, toRefs, watch } from 'vue'
  import type { ComputedRef } from 'vue'
  import type { LocationQuery } from 'vue-router'
  import { useRoute } from 'vue-router'

  import UserHeader from '@/components/User/ProfileDisplay/UserHeader.vue'
  import UserInfos from '@/components/User/ProfileDisplay/UserInfos.vue'
  import { AUTH_USER_STORE, USERS_STORE } from '@/store/constants'
  import type { IAuthUserProfile, IUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'

  interface Props {
    fromAdmin: boolean
  }
  const props = defineProps<Props>()
  const { fromAdmin } = toRefs(props)

  const route = useRoute()
  const store = useStore()

  const authUser: ComputedRef<IAuthUserProfile> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.AUTH_USER_PROFILE]
  )
  const user: ComputedRef<IUserProfile> = computed(
    () => store.getters[USERS_STORE.GETTERS.USER]
  )

  onBeforeMount(() => {
    getUser(route.params)
  })

  function getUser(params: LocationQuery) {
    if (params.username && typeof params.username === 'string') {
      store.dispatch(USERS_STORE.ACTIONS.GET_USER, params.username)
      store.dispatch(USERS_STORE.ACTIONS.EMPTY_RELATIONSHIPS)
    }
  }

  onBeforeUnmount(() => {
    store.dispatch(USERS_STORE.ACTIONS.EMPTY_USER)
    store.dispatch(USERS_STORE.ACTIONS.EMPTY_RELATIONSHIPS)
  })

  watch(
    () => route.params,
    (newParam: LocationQuery) => {
      getUser(newParam)
    }
  )
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';

  #user {
    margin: auto;
    width: 700px;
    @media screen and (max-width: $medium-limit) {
      width: 100%;
      margin: 0 auto 50px auto;
    }
  }
</style>
