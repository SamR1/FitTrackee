<template>
  <div v-if="loading && !appealText">
    <Loader />
  </div>
  <div v-else>
    <ActionAppeal
      v-if="accountSuspension.id"
      :suspension="accountSuspension"
      :success="isSuccess"
      :loading="loading"
      @submitForm="submitAppeal"
    >
      <template #cancelButton>
        <button @click="$router.push('/profile')">
          {{ $t('user.PROFILE.BACK_TO_PROFILE') }}
        </button>
      </template>
    </ActionAppeal>
    <div v-else>{{ $t('user.ACTIVE_ACCOUNT') }}</div>
  </div>
</template>

<script setup lang="ts">
  import { computed, ref, onMounted, onUnmounted } from 'vue'
  import type { ComputedRef, Ref } from 'vue'

  import ActionAppeal from '@/components/Common/ActionAppeal.vue'
  import { AUTH_USER_STORE } from '@/store/constants'
  import type { ISuspension } from '@/types/user'
  import { useStore } from '@/use/useStore'

  const store = useStore()

  const loading = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.USER_LOADING]
  )
  const accountSuspension: ComputedRef<ISuspension> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.ACCOUNT_SUSPENSION]
  )
  const appealText: Ref<string> = ref('')
  const isSuccess: ComputedRef<boolean> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.IS_SUCCESS]
  )

  onMounted(() => loadUserSuspension())

  function loadUserSuspension() {
    store.dispatch(AUTH_USER_STORE.ACTIONS.GET_ACCOUNT_SUSPENSION)
  }
  function submitAppeal(text: string) {
    appealText.value = text
    store.dispatch(AUTH_USER_STORE.ACTIONS.APPEAL, text)
  }

  onUnmounted(() =>
    store.commit(AUTH_USER_STORE.MUTATIONS.UPDATE_IS_SUCCESS, false)
  )
</script>
