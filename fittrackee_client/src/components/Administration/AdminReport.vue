<script setup lang="ts">
  import { Locale, formatDistance } from 'date-fns'
  import { computed, onBeforeMount, ref, watch } from 'vue'
  import type { ComputedRef, Ref } from 'vue'
  import { useRoute, useRouter } from 'vue-router'

  import Comment from '@/components/Comment/Comment.vue'
  import NotFound from '@/components/Common/NotFound.vue'
  import UserCard from '@/components/User/UserCard.vue'
  import Username from '@/components/User/Username.vue'
  import UserPicture from '@/components/User/UserPicture.vue'
  import WorkoutCard from '@/components/Workout/WorkoutCard.vue'
  import {
    AUTH_USER_STORE,
    REPORTS_STORE,
    ROOT_STORE,
    SPORTS_STORE,
  } from '@/store/constants'
  import { ICustomTextareaData } from '@/types/forms'
  import { IReportForAdmin } from '@/types/reports'
  import { ISport } from '@/types/sports'
  import { IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { formatDate, getDateFormat } from '@/utils/dates'

  const store = useStore()
  const route = useRoute()
  const router = useRouter()

  const locale: ComputedRef<Locale> = computed(
    () => store.getters[ROOT_STORE.GETTERS.LOCALE]
  )
  const errorMessages: ComputedRef<string | string[] | null> = computed(
    () => store.getters[ROOT_STORE.GETTERS.ERROR_MESSAGES]
  )
  const authUser: ComputedRef<IAuthUserProfile> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.AUTH_USER_PROFILE]
  )
  const report: ComputedRef<IReportForAdmin> = computed(
    () => store.getters[REPORTS_STORE.GETTERS.REPORT]
  )
  const sports: ComputedRef<ISport[]> = computed(
    () => store.getters[SPORTS_STORE.GETTERS.SPORTS]
  )
  const appLanguage: ComputedRef<string> = computed(
    () => store.getters[ROOT_STORE.GETTERS.LANGUAGE]
  )
  const dateFormat: ComputedRef<string> = computed(() =>
    getDateFormat(authUser.value.date_format, appLanguage.value)
  )
  const reportCommentText: Ref<string> = ref('')
  const displayReportCommentTextarea: Ref<boolean> = ref(false)
  const currentAction: Ref<string> = ref('')

  function loadReport() {
    store.dispatch(REPORTS_STORE.ACTIONS.GET_REPORT, +route.params.reportId)
  }
  function displayTextArea(action = '') {
    currentAction.value = action
    displayReportCommentTextarea.value = true
  }
  function updateCommentText(textareaData: ICustomTextareaData) {
    reportCommentText.value = textareaData.value
  }
  function onCancel() {
    displayReportCommentTextarea.value = false
    reportCommentText.value = ''
    currentAction.value = ''
    store.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
  }
  function updateReport() {
    store.dispatch(REPORTS_STORE.ACTIONS.UPDATE_REPORT, {
      reportId: report.value.id,
      comment: reportCommentText.value,
      resolved: currentAction.value === 'MARK_AS_RESOLVED',
    })
  }
  function getButtonLabel() {
    switch (currentAction.value) {
      case 'MARK_AS_RESOLVED':
        return `admin.APP_MODERATION.ACTIONS.${currentAction.value}`
      default:
        return 'buttons.SUBMIT'
    }
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

  onBeforeMount(async () => loadReport())

  watch(
    () => report.value.comments,
    () => {
      displayReportCommentTextarea.value = false
      reportCommentText.value = ''
    }
  )
</script>

<template>
  <div
    id="admin-report"
    class="admin-card"
    v-if="report && report.reported_user"
  >
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
                <Comment
                  v-if="report.reported_comment"
                  :auth-user="authUser"
                  :comment="report.reported_comment"
                  :comments-loading="null"
                  :for-admin="true"
                />
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
                <UserCard
                  v-if="report.object_type === 'user'"
                  :authUser="authUser"
                  :user="report.reported_user"
                  :hideRelationship="true"
                />
              </template>
            </Card>
            <Card class="report-detail-card">
              <template #title>
                {{ $t('admin.APP_MODERATION.REPORT_NOTE') }}
                <router-link
                  v-if="report.reported_by"
                  class="link-with-image"
                  :to="`/admin/users/${report.reported_by.username}`"
                >
                  {{ report.reported_by.username }}
                </router-link>
                ({{ $t('admin.APP_MODERATION.REPORTER') }})
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
              <div class="report-comment-user">
                <UserPicture :user="report.reported_by" />
                <Username :user="report.reported_by" />
              </div>
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

        <Card class="report-comments">
          <template #title>
            {{ $t('admin.APP_MODERATION.NOTES_AND_ACTIONS') }}
          </template>
          <template #content>
            <div
              class="report-comment"
              v-for="comment in report.comments"
              :key="comment.id"
            >
              <div class="report-comment-info">
                <div class="report-comment-user">
                  <UserPicture :user="comment.user" />
                  <Username :user="comment.user" />
                </div>
                <div
                  class="report-comment-date"
                  :title="getDate(comment.created_at)"
                >
                  {{
                    formatDistance(new Date(comment.created_at), new Date(), {
                      addSuffix: true,
                      locale,
                    })
                  }}
                </div>
              </div>
              <div class="report-comment-comment">{{ comment.comment }}</div>
            </div>
            <div v-if="report.comments.length === 0" class="no-notes">
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
              <form @submit.prevent="updateReport">
                <CustomTextArea
                  class="report-comment-textarea"
                  name="report-comment"
                  :required="true"
                  :placeholder="
                    $t('admin.APP_MODERATION.REPORT_COMMENT_PLACEHOLDER')
                  "
                  @updateValue="updateCommentText"
                />
                <div class="comment-buttons">
                  <button class="confirm" type="submit">
                    {{ $t(getButtonLabel()) }}
                  </button>
                  <button class="cancel" @click.prevent="onCancel">
                    {{ $t('buttons.CANCEL') }}
                  </button>
                </div>
                <ErrorMessage :message="errorMessages" v-if="errorMessages" />
              </form>
            </div>
            <div v-else class="actions-buttons">
              <button @click="displayTextArea">
                {{ $t('admin.APP_MODERATION.ACTIONS.ADD_COMMENT') }}
              </button>
              <button>
                {{ $t('admin.APP_MODERATION.ACTIONS.SEND_EMAIL') }}
              </button>
              <button class="danger">
                {{ $t('admin.APP_MODERATION.ACTIONS.DELETE_CONTENT') }}
              </button>
              <button class="danger">
                {{ $t('admin.APP_MODERATION.ACTIONS.DISABLE_ACCOUNT') }}
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
  <div class="container" v-else>
    <NotFound target="REPORT" />
  </div>
</template>

<style scoped lang="scss">
  @import '~@/scss/vars.scss';

  #admin-report {
    .report-comment-user {
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
    .report-comments {
      margin: $default-margin 0 $default-margin * 2;
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

    .report-comments {
      .report-comment {
        display: flex;
        flex-direction: column;
        padding-bottom: $default-padding;

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
          padding: $default-padding 0;
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
