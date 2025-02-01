<template>
  <router-link
    v-if="user.username"
    class="user-name"
    :to="{
      name: $route.path.startsWith('/admin') ? 'UserFromAdmin' : 'User',
      params: { username: user.username },
    }"
    :title="user.username"
  >
    {{ user.username }}
  </router-link>
</template>

<script setup lang="ts">
  import { toRefs } from 'vue'

  import type { IUserLightProfile, IUserProfile } from '@/types/user'

  interface Props {
    user: IUserProfile | IUserLightProfile
  }
  const props = defineProps<Props>()
  const { user } = toRefs(props)
</script>

<style scoped lang="scss">
  @use '~@/scss/vars.scss' as *;

  .user-name {
    padding-left: 5px;
    max-width: 300px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    text-decoration: none;
    @media screen and (max-width: $small-limit) {
      max-width: fit-content;
    }
    @media screen and (max-width: $x-small-limit) {
      max-width: 170px;
    }
  }
</style>
