<script setup lang="ts">
  import { computed, ComputedRef, onBeforeMount } from 'vue'
  import { useRoute } from 'vue-router'

  import Comment from '@/components/Comment/Comment.vue'
  import { AUTH_USER_STORE, REPORTS_STORE } from '@/store/constants'
  import { IReportForAdmin } from '@/types/reports'
  import { IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'

  const store = useStore()
  const route = useRoute()

  const authUser: ComputedRef<IAuthUserProfile> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.AUTH_USER_PROFILE]
  )
  const report: ComputedRef<IReportForAdmin> = computed(
    () => store.getters[REPORTS_STORE.GETTERS.REPORT]
  )

  function loadReport() {
    store.dispatch(REPORTS_STORE.ACTIONS.GET_REPORT, route.params.reportId)
  }

  onBeforeMount(async () => loadReport())
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
        <Card class="report-detail-card">
          <template #title>
            {{ $t('admin.ACTION', 0) }}
          </template>
          <template #content>
            <div class="actions-buttons">
              <button>
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
      </template>
    </Card>
  </div>
</template>

<style scoped lang="scss">
  @import '~@/scss/vars.scss';

  #admin-report {
    .report-detail-card {
      margin: $default-margin 0 $default-margin * 2;
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
