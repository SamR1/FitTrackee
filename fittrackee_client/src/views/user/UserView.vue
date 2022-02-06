<template>
  <div id="user" class="view" v-if="user.username">
    <UserHeader :authUser="authUser" :user="user" />
    <div class="box">
      <UserInfos :authUser="authUser" :user="user" />
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ComputedRef, computed, onBeforeMount, onBeforeUnmount } from 'vue'
  import { useRoute } from 'vue-router'

  import UserHeader from '@/components/User/ProfileDisplay/UserHeader.vue'
  import UserInfos from '@/components/User/ProfileDisplay/UserInfos.vue'
  import { AUTH_USER_STORE, USERS_STORE } from '@/store/constants'
  import { IAuthUserProfile, IUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'

  const route = useRoute()
  const store = useStore()

  const authUser: ComputedRef<IAuthUserProfile> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.AUTH_USER_PROFILE]
  )
  const user: ComputedRef<IUserProfile> = computed(
    () => store.getters[USERS_STORE.GETTERS.USER]
  )

  onBeforeMount(() => {
    if (route.params.username && typeof route.params.username === 'string') {
      store.dispatch(USERS_STORE.ACTIONS.GET_USER, route.params.username)
    }
  })

  onBeforeUnmount(() => {
    store.dispatch(USERS_STORE.ACTIONS.EMPTY_USER)
  })
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
