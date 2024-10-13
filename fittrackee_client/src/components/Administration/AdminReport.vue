<template>
  <div v-if="reportLoading" class="report-loading">
    <Loader />
  </div>
  <template v-else>
    <div id="admin-report" class="admin-card" v-if="report?.id">
      <Modal
        v-if="displayModal && report.reported_user"
        :title="$t('common.CONFIRMATION')"
        :message="`admin.CONFIRM_${currentAction}`"
        :strongMessage="report.reported_user.username"
        @confirmAction="confirmSuspension"
        @cancelAction="updateDisplayModal('')"
        @keydown.esc="updateDisplayModal('')"
      />
      <Card>
        <template #title>
          {{ $t('admin.APP_MODERATION.REPORT') }} #{{ report.id }}
          <span v-if="report.resolved" class="report-status">
            ({{ $t('admin.APP_MODERATION.RESOLVED.TRUE') }})
          </span>
        </template>
        <template #content>
          <div class="report-data">
            <div class="report-detail">
              <Card class="report-detail-card">
                <template #title>
                  {{ $t('admin.APP_MODERATION.REPORTED_CONTENT') }}
                </template>
                <template #content>
                  <template v-if="report.object_type === 'comment'">
                    <Comment
                      v-if="report.reported_comment"
                      :auth-user="authUser"
                      :comment="report.reported_comment"
                      :comments-loading="null"
                      :for-admin="true"
                    />
                    <span class="deleted-object" v-else>
                      {{ $t('admin.DELETED_COMMENT') }}
                    </span>
                    <span class="deleted-object" v-if="!report.reported_user">
                      ({{ $t('admin.DELETED_USER').toLocaleLowerCase() }})
                    </span>
                  </template>
                  <template v-if="report.object_type === 'workout'">
                    <WorkoutCard
                      v-if="report.reported_workout"
                      :workout="report.reported_workout"
                      :sport="
                        sports.filter(
                          (s) => s.id === report.reported_workout?.sport_id
                        )[0]
                      "
                      :user="report.reported_workout.user"
                      :useImperialUnits="authUser.imperial_units"
                      :dateFormat="dateFormat"
                      :timezone="authUser.timezone"
                      :key="report.reported_workout.id"
                    />
                    <span class="deleted-object" v-else>
                      {{ $t('admin.DELETED_WORKOUT') }}
                    </span>
                    <span class="deleted-object" v-if="!report.reported_user">
                      ({{ $t('admin.DELETED_USER').toLocaleLowerCase() }})
                    </span>
                  </template>
                  <template v-if="report.object_type === 'user'">
                    <UserCard
                      v-if="report.reported_user"
                      :authUser="authUser"
                      :user="report.reported_user"
                      :hideRelationship="true"
                    />
                    <span class="deleted-object" v-else>
                      {{ $t('admin.DELETED_USER') }}
                    </span>
                  </template>
                  <AlertMessage
                    v-else-if="report.reported_user?.suspended_at !== null"
                    message="user.ACCOUNT_SUSPENDED_AT"
                    :param="reportedUserSuspensionDate"
                  >
                    <template #additionalMessage v-if="displayReportLink">
                      <i18n-t keypath="common.SEE_REPORT">
                        <router-link
                          :to="`/admin/reports/${report.reported_user?.suspension_report_id}`"
                        >
                          {{ report.reported_user?.suspension_report_id }}
                        </router-link>
                      </i18n-t>
                    </template>
                  </AlertMessage>
                </template>
              </Card>
              <Card class="report-detail-card">
                <template #title>
                  {{ $t('admin.APP_MODERATION.REPORT_NOTE') }}
                  <template v-if="report.reported_by">
                    <router-link
                      class="link-with-image"
                      :to="`/admin/users/${report.reported_by.username}`"
                    >
                      {{ report.reported_by.username }}
                    </router-link>
                    ({{ $t('admin.APP_MODERATION.REPORTER') }})
                  </template>
                  <span v-else class="deleted-object">
                    {{ $t('admin.DELETED_USER').toLocaleLowerCase() }}
                  </span>
                </template>
                <template #content>
                  {{ report.note }}
                </template>
              </Card>
            </div>
            <dl class="report-info">
              <dt>{{ $t('admin.APP_MODERATION.ORDER_BY.CREATED_AT') }}:</dt>
              <dd>{{ getDate(report.created_at) }}</dd>
              <dt>{{ $t('admin.APP_MODERATION.REPORTED_BY') }}:</dt>
              <dd>
                <div class="report-comment-user" v-if="report.reported_by">
                  <UserPicture :user="report.reported_by" />
                  <Username :user="report.reported_by" />
                </div>
                <span class="deleted-object" v-else>
                  {{ $t('admin.DELETED_USER') }}
                </span>
              </dd>
              <dt>{{ $t('admin.APP_MODERATION.STATUS') }}:</dt>
              <dd>
                {{
                  $t(
                    `admin.APP_MODERATION.RESOLVED.${
                      report.resolved ? 'TRUE' : 'FALSE'
                    }`
                  )
                }}
              </dd>
              <dt v-if="report.resolved_at">
                {{ $t('admin.APP_MODERATION.RESOLVED_AT') }}:
              </dt>
              <dd v-if="report.resolved_at">
                <time>
                  {{ getDate(report.resolved_at) }}
                </time>
              </dd>
              <dt v-if="report.resolved_by">
                {{ $t('admin.APP_MODERATION.RESOLVED_BY') }}:
              </dt>
              <dd v-if="report.resolved_by">
                <div class="resolver-user">
                  <UserPicture :user="report.resolved_by" />
                  <Username :user="report.resolved_by" />
                </div>
              </dd>
              <dt v-if="report.updated_at">
                {{ $t('common.LAST_UPDATED_ON') }}:
              </dt>
              <dd v-if="report.updated_at">
                <time>
                  {{ getDate(report.updated_at) }}
                </time>
              </dd>
            </dl>
          </div>

          <Card class="report-action-and-comments">
            <template #title>
              {{ $t('admin.APP_MODERATION.NOTES_AND_ACTIONS') }}
            </template>
            <template #content>
              <div v-for="item in reportsItems" :key="item.id">
                <div
                  class="report-comment"
                  v-if="'comment' in item && !('action_type' in item)"
                >
                  <div class="report-comment-info">
                    <div class="report-comment-user">
                      <UserPicture :user="item.user" />
                      <Username :user="item.user" />
                    </div>
                    <div
                      class="report-comment-date"
                      :title="getDate(item.created_at)"
                    >
                      {{
                        formatDistance(new Date(item.created_at), new Date(), {
                          addSuffix: true,
                          locale,
                        })
                      }}
                    </div>
                  </div>
                  <div class="report-comment-comment">{{ item.comment }}</div>
                </div>
                <div class="report-action" v-if="'action_type' in item">
                  <div>
                    •
                    <i18n-t
                      :keypath="`admin.APP_MODERATION.REPORT_ACTIONS.${item.action_type}`"
                    >
                      <router-link
                        class="user-name"
                        v-if="item.action_type.startsWith('user_') && item.user"
                        :to="`/admin/users/${item.user.username}`"
                        :title="item.user.username"
                      >
                        {{ item.user.username }}
                      </router-link>
                      <router-link
                        class="user-name"
                        :to="`/admin/users/${item.admin_user.username}`"
                        :title="item.admin_user.username"
                      >
                        {{ item.admin_user.username }}
                      </router-link>
                      <span
                        class="report-action-date"
                        :title="getDate(item.created_at)"
                      >
                        {{
                          formatDistance(
                            new Date(item.created_at),
                            new Date(),
                            {
                              addSuffix: true,
                              locale,
                            }
                          )
                        }}
                      </span>
                    </i18n-t>
                    <button
                      v-if="item.appeal"
                      class="appeal-button small transparent"
                      @click="toggleAppeal(item.appeal.id)"
                    >
                      {{
                        $t(
                          `admin.APP_MODERATION.APPEAL.${displayedAppeals.includes(item.appeal.id) ? 'HIDE' : 'SEE'}`
                        )
                      }}
                    </button>
                  </div>
                  <div v-if="item.reason" class="report-action-note">
                    <span>{{ $t('admin.APP_MODERATION.REASON') }}:</span>
                    {{ item.reason }}
                  </div>
                  <ReportActionAppeal
                    v-if="
                      item.appeal && displayedAppeals.includes(item.appeal.id)
                    "
                    :appeal="item.appeal"
                    :auth-user="authUser"
                    @updateAppeal="updateAppeal"
                    @closeAppeal="toggleAppeal(item.appeal.id)"
                  />
                </div>
              </div>
              <div v-if="reportsItems.length == 0" class="no-notes">
                {{ $t('common.NO_NOTES') }}
              </div>
            </template>
          </Card>
          <Card class="report-detail-card">
            <template #title>
              {{ $t('admin.ACTION', 0) }}
            </template>
            <template #content>
              <div class="comment-textarea" v-if="displayReportCommentTextarea">
                <form @submit.prevent="submit">
                  <label for="report-comment">
                    {{ $t(`admin.APP_MODERATION.ACTIONS.${currentAction}`) }}
                  </label>
                  <CustomTextArea
                    class="report-comment-textarea"
                    name="report-comment"
                    :required="isNoteMandatory"
                    :placeholder="getTextAreaPlaceholder()"
                    :disabled="reportUpdateLoading"
                    @updateValue="updateCommentText"
                  />
                  <div class="comment-buttons">
                    <button
                      class="confirm"
                      type="submit"
                      :disabled="reportUpdateLoading"
                    >
                      {{ $t(getButtonLabel()) }}
                    </button>
                    <button
                      class="cancel"
                      @click.prevent="onCancel"
                      :disabled="reportUpdateLoading"
                    >
                      {{ $t('buttons.CANCEL') }}
                    </button>
                    <div class="action-loading">
                      <i
                        class="fa fa-spinner fa-pulse"
                        aria-hidden="true"
                        v-if="reportUpdateLoading"
                      />
                    </div>
                  </div>
                  <ErrorMessage :message="errorMessages" v-if="errorMessages" />
                </form>
              </div>
              <div v-else class="actions-buttons">
                <button @click="displayTextArea('ADD_COMMENT')">
                  {{ $t('admin.APP_MODERATION.ACTIONS.ADD_COMMENT') }}
                </button>
                <button
                  v-if="
                    !report.resolved &&
                    report.reported_user &&
                    !report.is_reported_user_warned
                  "
                  @click="displayTextArea('SEND_WARNING_EMAIL')"
                >
                  {{ $t('admin.APP_MODERATION.ACTIONS.SEND_WARNING_EMAIL') }}
                </button>
                <button
                  :class="{ danger: reportedContent.suspended_at === null }"
                  v-if="!report.resolved && reportedContent"
                  @click="
                    displayTextArea(
                      `${reportedContent.suspended_at === null ? '' : 'UN'}SUSPEND_CONTENT`
                    )
                  "
                >
                  {{
                    $t(
                      `admin.APP_MODERATION.ACTIONS.${
                        reportedContent.suspended_at === null ? '' : 'UN'
                      }SUSPEND_CONTENT`
                    )
                  }}
                </button>
                <button
                  v-if="!report.resolved && report.reported_user"
                  :class="{
                    danger: report.reported_user.suspended_at === null,
                  }"
                  @click="
                    displayTextArea(
                      `${report.reported_user.suspended_at ? 'UN' : ''}SUSPEND_ACCOUNT`
                    )
                  "
                >
                  {{
                    $t(
                      `admin.APP_MODERATION.ACTIONS.${
                        report.reported_user.suspended_at ? 'UN' : ''
                      }SUSPEND_ACCOUNT`
                    )
                  }}
                </button>
                <button
                  @click="
                    displayTextArea(
                      `MARK_AS_${report.resolved ? 'UN' : ''}RESOLVED`
                    )
                  "
                >
                  {{
                    $t(
                      `admin.APP_MODERATION.ACTIONS.MARK_AS_${
                        report.resolved ? 'UN' : ''
                      }RESOLVED`
                    )
                  }}
                </button>
              </div>
            </template>
          </Card>
          <button @click.prevent="goBack">
            {{ $t('buttons.BACK') }}
          </button>
        </template>
      </Card>
    </div>
    <div class="container" v-else-if="reportLoading"></div>
    <div class="container" v-else>
      <NotFound target="REPORT" />
    </div>
  </template>
</template>

<script setup lang="ts">
  import { formatDistance, compareAsc } from 'date-fns'
  import { computed, onBeforeMount, onUnmounted, ref, watch } from 'vue'
  import type { ComputedRef, Ref } from 'vue'
  import { useI18n } from 'vue-i18n'
  import { useRoute, useRouter } from 'vue-router'

  import ReportActionAppeal from '@/components/Administration/AdminReportActionAppeal.vue'
  import Comment from '@/components/Comment/Comment.vue'
  import Loader from '@/components/Common/Loader.vue'
  import NotFound from '@/components/Common/NotFound.vue'
  import UserCard from '@/components/User/UserCard.vue'
  import Username from '@/components/User/Username.vue'
  import UserPicture from '@/components/User/UserPicture.vue'
  import WorkoutCard from '@/components/Workout/WorkoutCard.vue'
  import useApp from '@/composables/useApp'
  import useAuthUser from '@/composables/useAuthUser'
  import useSports from '@/composables/useSports'
  import { REPORTS_STORE, ROOT_STORE, USERS_STORE } from '@/store/constants'
  import type { ICustomTextareaData } from '@/types/forms'
  import type {
    IReportAction,
    IReportComment,
    IReportCommentPayload,
    IReportForAdmin,
    TReportAction,
    IReportActionPayload,
  } from '@/types/reports'
  import type { IComment, IWorkout } from '@/types/workouts'
  import { useStore } from '@/use/useStore'
  import { formatDate } from '@/utils/dates'

  interface AppealEventData {
    approved: boolean
    appealId: string
    reason: string
  }

  const route = useRoute()
  const router = useRouter()
  const store = useStore()

  const { t } = useI18n()

  const { errorMessages, locale } = useApp()
  const { authUser, authUserSuccess, dateFormat } = useAuthUser()
  const { sports } = useSports()

  const reportCommentText: Ref<string> = ref('')
  const currentAction: Ref<TReportAction | null> = ref(null)
  const displayModal: Ref<string> = ref('')
  const displayedAppeals: Ref<string[]> = ref([])

  const report: ComputedRef<IReportForAdmin> = computed(
    () => store.getters[REPORTS_STORE.GETTERS.REPORT]
  )
  const reportedContent: ComputedRef<IComment | IWorkout | null> = computed(
    () => report.value.reported_comment || report.value.reported_workout
  )
  const reportLoading: ComputedRef<boolean> = computed(
    () => store.getters[REPORTS_STORE.GETTERS.REPORT_LOADING]
  )
  const reportUpdateLoading: ComputedRef<boolean> = computed(
    () => store.getters[REPORTS_STORE.GETTERS.REPORT_UPDATE_LOADING]
  )
  const displayReportCommentTextarea: Ref<boolean> = ref(false)
  const reportsItems: ComputedRef<(IReportAction | IReportComment)[]> =
    computed(() => getActionsAndComments())
  const isNoteMandatory: ComputedRef<boolean> = computed(
    () =>
      currentAction.value !== null &&
      ['ADD_COMMENT', 'MARK_AS_RESOLVED', 'MARK_AS_UNRESOLVED'].includes(
        currentAction.value
      )
  )
  const reportedUserSuspensionDate: ComputedRef<string | null> = computed(() =>
    report.value.reported_user?.suspended_at
      ? formatDate(
          report.value.reported_user?.suspended_at,
          authUser.value.timezone,
          authUser.value.date_format
        )
      : null
  )
  const displayReportLink: ComputedRef<boolean> = computed(
    () =>
      route.params.reportId !=
      report.value.reported_user?.suspension_report_id?.toString()
  )

  function loadReport() {
    store.dispatch(REPORTS_STORE.ACTIONS.GET_REPORT, {
      reportId: +route.params.reportId,
      loader: 'REPORT',
    })
  }
  function displayTextArea(action: TReportAction | null = null) {
    resetErrorAndForms()
    currentAction.value = action
    displayReportCommentTextarea.value = true
  }
  function updateCommentText(textareaData: ICustomTextareaData) {
    reportCommentText.value = textareaData.value
  }
  function onCancel() {
    displayReportCommentTextarea.value = false
    reportCommentText.value = ''
    currentAction.value = null
    store.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
  }
  function updateReport() {
    const payload: IReportCommentPayload = {
      reportId: report.value.id,
      comment: reportCommentText.value,
    }
    if (
      currentAction.value &&
      ['MARK_AS_RESOLVED', 'MARK_AS_UNRESOLVED'].includes(currentAction.value)
    ) {
      payload.resolved = currentAction.value === 'MARK_AS_RESOLVED'
    }
    store.dispatch(REPORTS_STORE.ACTIONS.UPDATE_REPORT, payload)
  }
  function submit() {
    switch (currentAction.value) {
      case 'SEND_WARNING_EMAIL':
        sendWarningEmail()
        break
      case 'SUSPEND_ACCOUNT':
      case 'SUSPEND_CONTENT':
        updateDisplayModal('suspension')
        break
      case 'UNSUSPEND_ACCOUNT':
        updateUserSuspendedAt()
        break
      case 'UNSUSPEND_CONTENT':
        updateContentSuspendedAt()
        break
      default:
        return updateReport()
    }
  }
  function getButtonLabel() {
    switch (currentAction.value) {
      case 'MARK_AS_RESOLVED':
        return `admin.APP_MODERATION.ACTIONS.${currentAction.value}`
      default:
        return 'buttons.SUBMIT'
    }
  }
  function updateUserSuspendedAt() {
    if (report.value.reported_user && currentAction.value) {
      const actionType = `user_${currentAction.value === 'SUSPEND_ACCOUNT' ? '' : 'un'}suspension`
      const payload: IReportActionPayload = {
        action_type: actionType,
        report_id: report.value.id,
        username: report.value.reported_user.username,
      }
      if (reportCommentText.value) {
        payload.reason = reportCommentText.value
      }
      store.dispatch(REPORTS_STORE.ACTIONS.SUBMIT_ADMIN_ACTION, payload)
    }
  }
  function updateContentSuspendedAt() {
    if (reportedContent.value && currentAction.value) {
      const actionType =
        `${report.value.reported_comment ? 'comment' : 'workout'}_` +
        `${currentAction.value?.startsWith('SUSPEND') ? '' : 'un'}suspension`
      const payload: IReportActionPayload = {
        action_type: actionType,
        report_id: report.value.id,
      }
      if (report.value.reported_comment) {
        payload.comment_id = report.value.reported_comment.id
      } else if (report.value.reported_workout) {
        payload.workout_id = report.value.reported_workout.id
      }

      if (reportCommentText.value) {
        payload.reason = reportCommentText.value
      }
      store.dispatch(REPORTS_STORE.ACTIONS.SUBMIT_ADMIN_ACTION, payload)
    }
  }
  function confirmSuspension() {
    updateDisplayModal('')
    if (currentAction.value === 'SUSPEND_CONTENT') {
      updateContentSuspendedAt()
    } else {
      updateUserSuspendedAt()
    }
  }
  function updateDisplayModal(value: string) {
    displayModal.value = value
    if (value !== '') {
      store.commit(USERS_STORE.MUTATIONS.UPDATE_IS_SUCCESS, false)
    }
  }
  function sendWarningEmail() {
    const payload: IReportActionPayload = {
      action_type: 'user_warning',
      report_id: report.value.id,
      username: report.value.reported_user?.username,
    }
    if (reportCommentText.value) {
      payload.reason = reportCommentText.value
    }
    store.dispatch(REPORTS_STORE.ACTIONS.SUBMIT_ADMIN_ACTION, payload)
  }
  function goBack() {
    router.go(-1)
    store.commit(REPORTS_STORE.MUTATIONS.EMPTY_REPORT)
  }
  function getDate(dateToFormat: string) {
    return formatDate(
      dateToFormat,
      authUser.value.timezone,
      authUser.value.date_format
    )
  }
  function sortCreatedAt(
    a: IReportAction | IReportComment,
    b: IReportAction | IReportComment
  ): number {
    return compareAsc(new Date(a.created_at), new Date(b.created_at))
  }
  function getActionsAndComments(): (IReportAction | IReportComment)[] {
    if (!report.value.report_actions && !report.value.comments) {
      return []
    }
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore
    return [...report.value.report_actions, ...report.value.comments].sort(
      sortCreatedAt
    )
  }
  function toggleAppeal(appealId: string) {
    if (displayedAppeals.value.includes(appealId)) {
      displayedAppeals.value.splice(displayedAppeals.value.indexOf(appealId), 1)
      store.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    } else {
      displayedAppeals.value.push(appealId)
    }
  }
  function updateAppeal(data: AppealEventData) {
    store.dispatch(REPORTS_STORE.ACTIONS.PROCESS_APPEAL, {
      ...data,
      reportId: report.value.id,
    })
  }
  function getTextAreaPlaceholder() {
    const placeholder_action = currentAction.value?.includes('SUSPEND')
      ? currentAction.value?.split('_')[0]
      : currentAction.value
    const placeholder = t(
      `admin.APP_MODERATION.TEXTAREA_PLACEHOLDER.${placeholder_action}`
    )
    let information = ''
    if (placeholder_action) {
      information = [
        'ADD_COMMENT',
        'MARK_AS_RESOLVED',
        'MARK_AS_UNRESOLVED',
      ].includes(placeholder_action)
        ? ''
        : ` ${t(
            'admin.APP_MODERATION.TEXTAREA_PLACEHOLDER.INFORMATION_VISIBLE_TO_USER'
          )}`
    }
    return `${placeholder}${information}`
  }
  function resetErrorAndForms() {
    store.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    displayedAppeals.value = []
  }

  watch(
    () => report.value.comments,
    () => {
      displayReportCommentTextarea.value = false
      reportCommentText.value = ''
    }
  )
  watch(
    () => route.params.reportId,
    () => {
      loadReport()
    }
  )
  watch(
    () => authUserSuccess.value,
    (newIsSuccess) => {
      if (newIsSuccess) {
        updateDisplayModal('')
      }
    }
  )

  onBeforeMount(async () => loadReport())
  onUnmounted(() =>
    store.commit(USERS_STORE.MUTATIONS.UPDATE_IS_SUCCESS, false)
  )
</script>

<style scoped lang="scss">
  @import '~@/scss/vars.scss';

  .report-loading {
    margin-top: 200px;
    width: 100%;
  }

  #admin-report {
    width: 100%;
    .report-comment-user,
    .resolver-user {
      display: flex;
      gap: $default-padding * 0.5;
      ::v-deep(.user-picture) {
        min-width: min-content;
        align-items: flex-start;
        img {
          height: 25px;
          width: 25px;
        }
        .no-picture {
          font-size: 1.5em;
        }
      }
    }

    .report-detail-card,
    .report-action-and-comments {
      margin: $default-margin 0 $default-margin * 2;
      @media screen and (max-width: $small-limit) {
        ::v-deep(.card-content) {
          padding: $default-padding;
        }
      }
    }

    .report-data {
      display: flex;
      flex-wrap: wrap;

      .report-detail {
        display: flex;
        flex-direction: column;
        flex-grow: 3;
      }
      .report-info {
        display: flex;
        flex-direction: column;
        flex-grow: 1;
        padding: 0 $default-padding;

        dt {
          font-weight: bold;
          text-transform: lowercase;
        }
      }

      @media screen and (max-width: $small-limit) {
        flex-direction: column-reverse;

        .report-info {
          padding: 0 !important;
        }
      }
    }

    .report-status {
      text-transform: lowercase;
    }

    .report-action-and-comments {
      ::v-deep(.card-content) {
        display: flex;
        flex-direction: column;
        gap: $default-padding * 1.2;

        .report-comment {
          display: flex;
          flex-direction: column;

          .report-comment-info {
            display: flex;
            justify-content: space-between;

            .report-comment-date {
              font-size: 0.85em;
              font-style: italic;
              white-space: nowrap;
            }
          }

          .report-comment-comment {
            padding-top: $default-padding;
          }
        }
      }

      .report-action {
        color: var(--app-color-light);
        font-style: italic;
        font-size: 0.9em;
        margin-left: $default-padding;

        .report-action-note {
          margin: 0 0 0 $default-margin;
          font-size: 0.95em;
          span {
            font-weight: bold;
          }
        }

        .appeal-button {
          margin-left: 3px;
        }
      }

      .no-notes {
        font-style: italic;
      }
    }

    .comment-textarea {
      padding: $default-padding * 0.5 0 $default-padding;
      .comment-buttons {
        display: flex;
        gap: $default-padding;
        padding-top: $default-padding;
      }
    }
    .actions-buttons {
      display: flex;
      flex-wrap: wrap;
      gap: $default-padding;
      @media screen and (max-width: $small-limit) {
        justify-content: center;
      }
    }
  }
</style>
