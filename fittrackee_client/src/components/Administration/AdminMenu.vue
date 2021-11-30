<template>
  <div id="admin-menu" class="center-card">
    <Card>
      <template #title>{{ $t('admin.ADMINISTRATION') }}</template>
      <template #content>
        <AppStatsCards :appStatistics="appStatistics" />
        <div class="admin-menu description-list">
          <dl>
            <dt>
              <router-link to="/admin/application">
                {{ $t('admin.APPLICATION') }}
              </router-link>
            </dt>
            <dd>
              {{ $t('admin.UPDATE_APPLICATION_DESCRIPTION') }}<br />
              <span class="registration-status">
                {{
                  $t(
                    `admin.REGISTRATION_${
                      appConfig.is_registration_enabled ? 'ENABLED' : 'DISABLED'
                    }`
                  )
                }}
              </span>
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
                {{ capitalize($t('admin.USER', 0)) }}
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
  import { capitalize, toRefs, withDefaults } from 'vue'

  import AppStatsCards from '@/components/Administration/AppStatsCards.vue'
  import Card from '@/components/Common/Card.vue'
  import { IAppStatistics, TAppConfig } from '@/types/application'

  interface Props {
    appConfig: TAppConfig
    appStatistics?: IAppStatistics
  }
  const props = withDefaults(defineProps<Props>(), {
    appStatistics: () => ({} as IAppStatistics),
  })

  const { appConfig, appStatistics } = toRefs(props)
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
        .registration-status {
          font-weight: bold;
        }
      }
    }
  }
</style>
