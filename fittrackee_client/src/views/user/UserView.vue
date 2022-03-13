<template>
  <div id="user" class="view" v-if="user.username">
    <UserHeader :user="user" />
    <div class="box">
      <UserInfos :user="user" :from-admin="fromAdmin" />
    </div>
  </div>
</template>

<script setup lang="ts">
  import {
    ComputedRef,
    computed,
    onBeforeMount,
    onBeforeUnmount,
    toRefs,
  } from 'vue'
  import { useRoute } from 'vue-router'

  import UserHeader from '@/components/User/ProfileDisplay/UserHeader.vue'
  import UserInfos from '@/components/User/ProfileDisplay/UserInfos.vue'
  import { USERS_STORE } from '@/store/constants'
  import { IUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'

  interface Props {
    fromAdmin: boolean
  }
  const props = defineProps<Props>()
  const { fromAdmin } = toRefs(props)

  const route = useRoute()
  const store = useStore()

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
