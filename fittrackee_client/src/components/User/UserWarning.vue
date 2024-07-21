<template>
  <div v-if="loading && !appealText">
    <Loader />
  </div>
  <div v-else>
    <ActionAppeal
      :admin-action="userWarning"
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
  </div>
</template>

<script setup lang="ts">
  import { computed, ref, onMounted, onUnmounted } from 'vue'
  import type { ComputedRef, Ref } from 'vue'
  import { useRoute } from 'vue-router'

  import ActionAppeal from '@/components/Common/ActionAppeal.vue'
  import { AUTH_USER_STORE } from '@/store/constants'
  import type { IUserAdminAction } from '@/types/user'
  import { useStore } from '@/use/useStore'

  const store = useStore()
  const route = useRoute()

  const loading = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.USER_LOADING]
  )
  const userWarning: ComputedRef<IUserAdminAction> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.USER_WARNING]
  )
  const appealText: Ref<string> = ref('')
  const isSuccess: ComputedRef<boolean> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.IS_SUCCESS]
  )

  onMounted(() => loadUserWarning())

  function loadUserWarning() {
    store.dispatch(
      AUTH_USER_STORE.ACTIONS.GET_USER_WARNING,
      route.params.action_id as string
    )
  }
  function submitAppeal(text: string) {
    appealText.value = text
    store.dispatch(AUTH_USER_STORE.ACTIONS.APPEAL, {
      actionId: userWarning.value.id,
      actionType: 'user_warning',
      text,
    })
  }

  onUnmounted(() => {
    store.commit(AUTH_USER_STORE.MUTATIONS.UPDATE_IS_SUCCESS, false)
    store.commit(
      AUTH_USER_STORE.MUTATIONS.SET_USER_WARNING,
      {} as IUserAdminAction
    )
  })
</script>
