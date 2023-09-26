<script setup lang="ts">
  import { Locale, formatDistance } from 'date-fns'
  import { computed, onBeforeMount, ref, watch } from 'vue'
  import type { ComputedRef, Ref } from 'vue'
  import { useRoute } from 'vue-router'

  import Comment from '@/components/Comment/Comment.vue'
  import Username from '@/components/User/Username.vue'
  import UserPicture from '@/components/User/UserPicture.vue'
  import { AUTH_USER_STORE, REPORTS_STORE, ROOT_STORE } from '@/store/constants'
  import { IDisplayOptions } from '@/types/application'
  import { ICustomTextareaData } from '@/types/forms'
  import { IReportForAdmin } from '@/types/reports'
  import { IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { formatDate } from '@/utils/dates'

  const store = useStore()
  const route = useRoute()

  const locale: ComputedRef<Locale> = computed(
    () => store.getters[ROOT_STORE.GETTERS.LOCALE]
  )
  const displayOptions: ComputedRef<IDisplayOptions> = computed(
    () => store.getters[ROOT_STORE.GETTERS.DISPLAY_OPTIONS]
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
  const reportCommentText: Ref<string> = ref('')
  const displayReportCommentTextarea: Ref<boolean> = ref(false)

  function loadReport() {
    store.dispatch(REPORTS_STORE.ACTIONS.GET_REPORT, +route.params.reportId)
  }
  function displayTextArea() {
    displayReportCommentTextarea.value = true
  }
  function updateCommentText(textareaData: ICustomTextareaData) {
    reportCommentText.value = textareaData.value
  }
  function onCancel() {
    displayReportCommentTextarea.value = false
    reportCommentText.value = ''
    store.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
  }
  function submitReportComment() {
    store.dispatch(REPORTS_STORE.ACTIONS.SUBMIT_REPORT_COMMENT, {
      reportId: report.value.id,
      comment: reportCommentText.value,
    })
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
      </template>
      <template #content>
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
                  :title="
                    formatDate(
                      comment.created_at,
                      displayOptions.timezone,
                      displayOptions.dateFormat
                    )
                  "
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
            <div class="comment-textarea" v-if="displayReportCommentTextarea">
              <form @submit.prevent="submitReportComment">
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
                    {{ $t('buttons.SUBMIT') }}
                  </button>
                  <button class="cancel" @click.prevent="onCancel">
                    {{ $t('buttons.CANCEL') }}
                  </button>
                </div>
                <ErrorMessage :message="errorMessages" v-if="errorMessages" />
              </form>
            </div>
          </template>
        </Card>
        <Card class="report-detail-card">
          <template #title>
            {{ $t('admin.ACTION', 0) }}
          </template>
          <template #content>
            <div class="actions-buttons">
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
              <button>
                {{ $t('admin.APP_MODERATION.ACTIONS.MARK_AS_RESOLVED') }}
              </button>
            </div>
          </template>
        </Card>
        <button @click.prevent="$router.push('/admin/reports')">
          {{ $t('buttons.BACK') }}
        </button>
      </template>
    </Card>
  </div>
</template>

<style scoped lang="scss">
  @import '~@/scss/vars.scss';

  #admin-report {
    .report-detail-card,
    .report-comments {
      margin: $default-margin 0 $default-margin * 2;
    }

    .report-comments {
      .report-comment {
        display: flex;
        flex-direction: column;
        padding-bottom: $default-padding;

        .report-comment-info {
          display: flex;
          justify-content: space-between;

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
      .comment-textarea {
        .comment-buttons {
          display: flex;
          gap: $default-padding;
          padding-top: $default-padding;
        }
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
