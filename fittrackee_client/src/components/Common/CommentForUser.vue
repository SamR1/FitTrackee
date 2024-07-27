<template>
  <div class="notification-object" v-if="displayObjectName">
    {{ $t('workouts.COMMENTS.COMMENT') }}:
  </div>
  <div class="box comment-box">
    <Comment
      :comment="comment"
      :authUser="authUser"
      :display-appeal="false"
      comments-loading="null"
      :for-notification="true"
    />
  </div>
  <div v-if="displayAppeal" class="appeal-action">
    <button
      v-if="!success && !displayAppealForm"
      class="transparent appeal-button"
      @click="displayAppealForm = true"
    >
      {{ $t('user.APPEAL') }}
    </button>
    <ActionAppeal
      v-if="displayAppealForm"
      :admin-action="action"
      :success="success === `comment_${comment.id}`"
      :loading="appealLoading === `comment_${comment.id}`"
      @submitForm="submitAppeal"
      @hideMessage="displayAppealForm = false"
    >
      <template #cancelButton>
        <button @click="cancelAppeal()">
          {{ $t('buttons.CANCEL') }}
        </button>
      </template>
    </ActionAppeal>
  </div>
</template>

<script setup lang="ts">
  import { computed, ref, toRefs } from 'vue'
  import type { Ref, ComputedRef } from 'vue'

  import Comment from '@/components/Comment/Comment.vue'
  import ActionAppeal from '@/components/Common/ActionAppeal.vue'
  import {
    AUTH_USER_STORE,
    ROOT_STORE,
    WORKOUTS_STORE,
  } from '@/store/constants'
  import type { IAuthUserProfile, IUserAdminAction } from '@/types/user'
  import type { IComment } from '@/types/workouts'
  import { useStore } from '@/use/useStore'

  interface Props {
    action: IUserAdminAction
    displayAppeal: boolean
    comment: IComment
    displayObjectName: boolean
  }
  const props = defineProps<Props>()
  const { comment, displayObjectName } = toRefs(props)

  const store = useStore()

  const authUser: ComputedRef<IAuthUserProfile> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.AUTH_USER_PROFILE]
  )
  const displayAppealForm: Ref<boolean> = ref(false)
  const success: ComputedRef<null | string> = computed(
    () => store.getters[WORKOUTS_STORE.GETTERS.SUCCESS]
  )
  const appealLoading: ComputedRef<null | string> = computed(
    () => store.getters[WORKOUTS_STORE.GETTERS.APPEAL_LOADING]
  )

  function submitAppeal(appealText: string) {
    store.dispatch(WORKOUTS_STORE.ACTIONS.MAKE_COMMENT_APPEAL, {
      objectId: comment.value.id,
      text: appealText,
    })
  }
  function cancelAppeal() {
    displayAppealForm.value = false
    store.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
  }
</script>

<style scoped lang="scss">
  @import '~@/scss/vars';

  .notification-object {
    font-weight: bold;
    text-transform: capitalize;
  }
  .appeal-action {
    .appeal {
      padding: 0 $default-padding;
    }

    .appeal-button {
      padding: 0 $default-padding;
      font-size: 0.9em;
    }
  }
</style>
