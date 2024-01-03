<template>
  <div id="admin-menu" class="center-card">
    <Card>
      <template #title>{{ $t('admin.ADMINISTRATION') }}</template>
      <template #content>
        <AppStatsCards :appStatistics="appStatistics" />
        <div class="admin-menu description-list">
          <dl>
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
                      appConfig.is_registration_enabled ? 'ENABLED' : 'DISABLED'
                    }`
                  )
                }}
              </span>
              <span class="federation-status">
                {{
                  $t(
                    `admin.FEDERATION_${
                      appConfig.federation_enabled ? 'ENABLED' : 'DISABLED'
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
              <router-link id="adminLink" to="/admin/reports">
                {{ $t('admin.APP_MODERATION.TITLE') }}
              </router-link>
            </dt>
            <dd>
              {{ $t('admin.APP_MODERATION.DESCRIPTION') }}
            </dd>
            <dt>
              <router-link to="/admin/sports">
                {{ capitalize($t('workouts.SPORT', 0)) }}
              </router-link>
            </dt>
            <dd>
              {{ $t('admin.ENABLE_DISABLE_SPORTS') }}
            </dd>
            <dt>
              <router-link to="/admin/users">
                {{ capitalize($t('user.USER', 0)) }}
              </router-link>
            </dt>
            <dd>
              {{ $t('admin.ADMIN_RIGHTS_DELETE_USER_ACCOUNT') }}
            </dd>
          </dl>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
  import { capitalize, computed, onMounted } from 'vue'
  import type { ComputedRef } from 'vue'

  import AppStatsCards from '@/components/Administration/AppStatsCards.vue'
  import Card from '@/components/Common/Card.vue'
  import { ROOT_STORE } from '@/store/constants'
  import type { IAppStatistics, TAppConfig } from '@/types/application'
  import { useStore } from '@/use/useStore'

  const store = useStore()

  const appConfig: ComputedRef<TAppConfig> = computed(
    () => store.getters[ROOT_STORE.GETTERS.APP_CONFIG]
  )
  const appStatistics: ComputedRef<IAppStatistics> = computed(
    () => store.getters[ROOT_STORE.GETTERS.APP_STATS]
  )

  onMounted(() => {
    const applicationLink = document.getElementById('adminLink')
    if (applicationLink) {
      applicationLink.focus()
    }
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';

  #admin-menu {
    display: flex;
    &.center-card {
      width: 100%;
    }

    ::v-deep(.card) {
      flex-grow: 1;

      .admin-menu {
        padding: 0 $default-padding;

        dd {
          margin-bottom: $default-margin * 3;
        }
        .application-config-details {
          display: flex;
          flex-direction: column;
          .email-sending-status,
          .federation-status,
          .registration-status {
            font-weight: bold;
          }
        }
      }
    }
  }
</style>
