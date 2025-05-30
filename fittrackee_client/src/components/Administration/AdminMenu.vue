<template>
  <div id="admin-menu" class="center-card">
    <Card>
      <template #title>{{ $t('admin.ADMINISTRATION') }}</template>
      <template #content>
        <AppStatsCards :appStatistics="appStatistics" />
        <div class="admin-menu description-list">
          <dl>
            <template v-if="authUserHasAdminRights">
              <dt>
                <router-link id="adminLink" to="/admin/application">
                  {{ $t('admin.APPLICATION') }}
                </router-link>
              </dt>
              <dd class="application-config-details">
                {{ $t('admin.UPDATE_APPLICATION_DESCRIPTION') }}
                <span class="registration-status">
                  {{
                    $t(
                      `admin.REGISTRATION_${
                        appConfig.is_registration_enabled
                          ? 'ENABLED'
                          : 'DISABLED'
                      }`
                    )
                  }}
                </span>
                <span
                  class="email-sending-status"
                  v-if="!appConfig.is_email_sending_enabled"
                >
                  <i class="fa fa-exclamation-triangle" aria-hidden="true" />
                  {{ $t('admin.EMAIL_SENDING_DISABLED') }}
                </span>
              </dd>
              <dt>
                <router-link to="/admin/equipment-types">
                  {{ capitalize($t('equipments.EQUIPMENT_TYPE', 0)) }}
                </router-link>
              </dt>
              <dd>
                {{ $t('admin.ENABLE_DISABLE_EQUIPMENT_TYPES') }}
              </dd>
            </template>
            <dt>
              <router-link id="adminLink" to="/admin/reports">
                {{ $t('admin.APP_MODERATION.TITLE') }}
              </router-link>
            </dt>
            <dd class="application-config-details">
              {{ $t('admin.APP_MODERATION.DESCRIPTION') }}
              <router-link
                to="/admin/reports?resolved=false"
                v-if="unresolvedReportsStatus"
              >
                {{ $t('admin.APP_MODERATION.UNRESOLVED_REPORTS_EXIST') }}
              </router-link>
            </dd>
            <template v-if="authUserHasAdminRights">
              <dt>
                <router-link to="/admin/sports">
                  {{ capitalize($t('workouts.SPORT', 0)) }}
                </router-link>
              </dt>
              <dd>
                {{ $t('admin.ENABLE_DISABLE_SPORTS') }}
              </dd>
              <dt>
                <router-link to="/admin/queued-tasks">
                  {{ capitalize($t('admin.USERS_QUEUED_TASKS.LABEL', 0)) }}
                </router-link>
              </dt>
              <dd>
                <div>{{ $t('admin.USERS_QUEUED_TASKS.DESCRIPTION') }}</div>
                <router-link to="/admin/queued-tasks" v-if="queuedTasksExist">
                  {{ $t('admin.APP_MODERATION.USERS_QUEUED_TASKS_EXIST') }}
                </router-link>
              </dd>
              <dt>
                <router-link to="/admin/users">
                  {{ capitalize($t('user.USER', 0)) }}
                </router-link>
              </dt>
              <dd>
                {{ $t('admin.ADMIN_RIGHTS_DELETE_USER_ACCOUNT') }}
              </dd>
            </template>
          </dl>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
  import { capitalize, computed, onBeforeMount, onMounted } from 'vue'
  import type { ComputedRef } from 'vue'

  import AppStatsCards from '@/components/Administration/AppStatsCards.vue'
  import Card from '@/components/Common/Card.vue'
  import useApp from '@/composables/useApp'
  import useAuthUser from '@/composables/useAuthUser'
  import { REPORTS_STORE, ROOT_STORE, USERS_STORE } from '@/store/constants'
  import type { IAppStatistics, TQueuedTasksCounts } from '@/types/application'
  import { useStore } from '@/use/useStore'

  const store = useStore()

  const { appConfig } = useApp()
  const { authUserHasAdminRights } = useAuthUser()

  const appStatistics: ComputedRef<IAppStatistics> = computed(
    () => store.getters[ROOT_STORE.GETTERS.APP_STATS]
  )
  const unresolvedReportsStatus: ComputedRef<boolean> = computed(
    () => store.getters[REPORTS_STORE.GETTERS.UNRESOLVED_REPORTS_STATUS]
  )
  const queuedTasksCounts: ComputedRef<TQueuedTasksCounts> = computed(
    () => store.getters[USERS_STORE.GETTERS.USERS_QUEUED_TASKS_COUNTS]
  )
  const queuedTasksExist: ComputedRef<boolean> = computed(
    () =>
      queuedTasksCounts.value.user_data_export > 0 ||
      queuedTasksCounts.value.workouts_archive_upload > 0
  )

  onBeforeMount(() => {
    store.dispatch(REPORTS_STORE.ACTIONS.GET_UNRESOLVED_REPORTS_STATUS)
    store.dispatch(USERS_STORE.ACTIONS.GET_USERS_QUEUED_TASKS_COUNT)
  })
  onMounted(() => {
    const applicationLink = document.getElementById('adminLink')
    if (applicationLink) {
      applicationLink.focus()
    }
  })
</script>

<style lang="scss" scoped>
  @use '~@/scss/vars.scss' as *;

  #admin-menu {
    display: flex;
    &.center-card {
      width: 100%;
    }

    ::v-deep(.card) {
      flex-grow: 1;

      .card-content {
        @media screen and (max-width: $x-small-limit) {
          padding: $default-padding;

          .stat-card {
            .stat-content {
              @media screen and (max-width: $x-small-limit) {
                padding: $default-padding;

                .stat-icon {
                  .fa {
                    @media screen and (max-width: $x-small-limit) {
                      font-size: 1.2em;
                    }
                  }
                }
              }
            }
          }
        }
      }

      .admin-menu {
        padding: 0 $default-padding;

        dd {
          margin-bottom: $default-margin * 3;
        }
        .application-config-details {
          display: flex;
          flex-direction: column;
          .email-sending-status,
          .registration-status {
            font-weight: bold;
          }
        }
      }
    }
  }
</style>
