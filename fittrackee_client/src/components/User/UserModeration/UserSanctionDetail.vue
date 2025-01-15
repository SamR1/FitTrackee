<template>
  <div id="user-sanction">
    <div v-if="authUserLoading && !appealText">
      <Loader />
    </div>
    <div v-else-if="userSanction.id">
      <h1>
        {{
          $t(`user.PROFILE.SANCTIONS.${userSanction.action_type}`, {
            date: formatDate(
              userSanction.created_at,
              authUser.timezone,
              authUser.date_format
            ),
          })
        }}
      </h1>
      <template v-if="'comment' in userSanction">
        <CommentForUser
          v-if="userSanction.comment"
          :display-object-name="true"
          :comment="userSanction.comment"
        />
        <template v-else>
          <div class="deleted-object-type">
            {{ $t('workouts.COMMENTS.COMMENT') }}:
          </div>
          <div class="deleted-object">
            {{ $t('admin.DELETED_COMMENT') }}
          </div>
        </template>
      </template>
      <template v-else-if="'workout' in userSanction">
        <WorkoutForUser
          v-if="userSanction.workout"
          :action="userSanction"
          :display-appeal="false"
          :display-object-name="true"
          :workout="userSanction.workout"
        />
        <template v-else>
          <div class="deleted-object-type">{{ $t('workouts.WORKOUT') }}:</div>
          <div class="deleted-object">
            {{ $t('admin.DELETED_WORKOUT') }}
          </div>
        </template>
      </template>
      <ActionAppeal
        :report-action="userSanction"
        :success="authUserSuccess"
        :loading="authUserLoading"
        :can-appeal="!hideAppeal"
        @submitForm="submitAppeal"
      />
    </div>
    <div v-else>
      <div class="no-warning">
        {{ $t('user.NO_WARNING_FOUND') }}
      </div>
    </div>
    <div class="buttons">
      <button @click="$router.push('/profile/moderation')">
        {{ $t('buttons.BACK') }}
      </button>
      <template v-if="!authUser.suspended_at">
        <button @click="$router.push('/')">
          {{ $t('common.HOME') }}
        </button>
        <button @click="$router.push('/notifications')">
          {{ $t('notifications.NOTIFICATIONS', 0) }}
        </button>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { computed, ref, onMounted, onUnmounted, toRefs } from 'vue'
  import type { ComputedRef, Ref } from 'vue'
  import { useRoute } from 'vue-router'

  import CommentForUser from '@/components/Comment/CommentForUser.vue'
  import ActionAppeal from '@/components/Common/ActionAppeal.vue'
  import WorkoutForUser from '@/components/Workout/WorkoutForUser.vue'
  import useAuthUser from '@/composables/useAuthUser'
  import { AUTH_USER_STORE } from '@/store/constants'
  import type { IAuthUserProfile, IUserReportAction } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { formatDate } from '@/utils/dates'

  interface Props {
    authUser: IAuthUserProfile
  }
  const props = defineProps<Props>()
  const { authUser } = toRefs(props)

  const store = useStore()
  const route = useRoute()

  const { authUserLoading, authUserSuccess } = useAuthUser()

  const appealText: Ref<string> = ref('')

  const userSanction: ComputedRef<IUserReportAction> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.USER_SANCTION]
  )
  const hideAppeal: ComputedRef<boolean> = computed(
    () =>
      authUser.value.suspended_at !== null ||
      userSanction.value.action_type === 'user_suspension' ||
      ('comment' in userSanction.value &&
        userSanction.value.comment === null) ||
      ('workout' in userSanction.value && userSanction.value.workout === null)
  )

  function loadUserSanction() {
    store.dispatch(
      AUTH_USER_STORE.ACTIONS.GET_USER_SANCTION,
      route.params.action_id as string
    )
  }
  function submitAppeal(text: string) {
    appealText.value = text
    store.dispatch(AUTH_USER_STORE.ACTIONS.APPEAL, {
      actionId: userSanction.value.id,
      actionType: 'user_warning',
      text,
    })
  }

  onMounted(() => loadUserSanction())
  onUnmounted(() => {
    store.commit(AUTH_USER_STORE.MUTATIONS.UPDATE_IS_SUCCESS, false)
    store.commit(
      AUTH_USER_STORE.MUTATIONS.SET_USER_SANCTION,
      {} as IUserReportAction
    )
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';

  #user-sanction {
    padding: $default-padding 0;
    h1 {
      font-size: 1.05em;
      font-weight: bold;
    }
    .no-warning {
      margin: $default-padding 0;
    }

    ::v-deep(.notification-object) {
      margin-top: $default-padding;
    }

    .buttons {
      display: flex;
      gap: $default-padding;
      button {
        text-transform: capitalize;
      }
    }
    .deleted-object-type {
      font-weight: bold;
      text-transform: capitalize;
    }
    .deleted-object {
      font-style: italic;
      text-transform: lowercase;
    }
  }
</style>
