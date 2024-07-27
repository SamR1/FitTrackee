<template>
  <div v-if="loading && !appealText">
    <Loader />
  </div>
  <div v-else-if="userWarning.id">
    <div>{{ $t('notifications.YOU_RECEIVED_A_WARNING') }}.</div>
    <template v-if="userWarning.comment">
      <CommentForUser
        :action="userWarning"
        :display-appeal="false"
        :display-object-name="true"
        :comment="userWarning.comment"
      />
    </template>
    <template v-else-if="userWarning.workout">
      <WorkoutForUser
        :action="userWarning"
        :display-appeal="false"
        :display-object-name="true"
        :workout="userWarning.workout"
      />
    </template>
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
  <div v-else>
    <div class="no-warning">
      {{ $t('user.NO_WARNING_FOUND') }}
    </div>
    <button @click="$router.push('/profile')">
      {{ $t('user.PROFILE.BACK_TO_PROFILE') }}
    </button>
  </div>
</template>

<script setup lang="ts">
  import { computed, ref, onMounted, onUnmounted } from 'vue'
  import type { ComputedRef, Ref } from 'vue'
  import { useRoute } from 'vue-router'

  import ActionAppeal from '@/components/Common/ActionAppeal.vue'
  import CommentForUser from '@/components/Common/CommentForUser.vue'
  import WorkoutForUser from '@/components/Common/WorkoutForUser.vue'
  import { AUTH_USER_STORE, ROOT_STORE } from '@/store/constants'
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
    store.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    store.commit(AUTH_USER_STORE.MUTATIONS.UPDATE_IS_SUCCESS, false)
    store.commit(
      AUTH_USER_STORE.MUTATIONS.SET_USER_WARNING,
      {} as IUserAdminAction
    )
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';

  .no-warning {
    margin: $default-padding 0;
  }

  ::v-deep(.notification-object) {
    margin-top: $default-padding;
  }
</style>
