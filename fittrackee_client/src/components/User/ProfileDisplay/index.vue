<template>
  <div id="user-profile">
    <div class="box user-header">
      <UserPicture :user="user" />
      <div class="user-details">
        <div class="user-name">{{ user.username }}</div>
        <div class="user-stats">
          <div class="user-stat">
            <span class="stat-number">{{ user.nb_workouts }}</span>
            <span class="stat-label">
              {{ t('workouts.WORKOUT', user.nb_workouts) }}
            </span>
          </div>
          <div class="user-stat">
            <span class="stat-number">{{
              Number(user.total_distance).toFixed(0)
            }}</span>
            <span class="stat-label">km</span>
          </div>
          <div class="user-stat hide-small">
            <span class="stat-number">{{ user.nb_sports }}</span>
            <span class="stat-label">
              {{ t('workouts.SPORT', user.nb_sports) }}
            </span>
          </div>
        </div>
      </div>
    </div>
    <div class="box">
      <UserProfileTabs :tabs="tabs" :selectedTab="tab" :edition="false" />
      <UserInfos :user="user" v-if="tab === 'PROFILE'" />
      <UserPreferences :user="user" v-if="tab === 'PREFERENCES'" />
    </div>
  </div>
</template>

<script lang="ts">
  import { ComputedRef, PropType, computed, defineComponent } from 'vue'
  import { useI18n } from 'vue-i18n'

  import UserInfos from '@/components/User/ProfileDisplay/UserInfos.vue'
  import UserPreferences from '@/components/User/ProfileDisplay/UserPreferences.vue'
  import UserPicture from '@/components/User/UserPicture.vue'
  import UserProfileTabs from '@/components/User/UserProfileTabs.vue'
  import { IAuthUserProfile } from '@/types/user'
  import { getApiUrl } from '@/utils'

  export default defineComponent({
    name: 'ProfileDisplay',
    components: {
      UserInfos,
      UserPicture,
      UserPreferences,
      UserProfileTabs,
    },
    props: {
      user: {
        type: Object as PropType<IAuthUserProfile>,
        required: true,
      },
      tab: {
        type: String,
        required: true,
      },
    },
    setup(props) {
      const { t } = useI18n()
      const tabs = ['PROFILE', 'PREFERENCES']
      const authUserPictureUrl: ComputedRef<string> = computed(() =>
        props.user.picture
          ? `${getApiUrl()}/users/${props.user.username}/picture?${Date.now()}`
          : ''
      )
      return { authUserPictureUrl, t, tabs }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base.scss';

  #user-profile {
    margin: auto;
    width: 700px;
    @media screen and (max-width: $medium-limit) {
      width: 100%;
      margin: 0 auto 50px auto;
    }

    .user-header {
      display: flex;
      align-items: stretch;

      .user-details {
        flex-grow: 1;
        padding: $default-padding;
        display: flex;
        flex-direction: column;
        align-items: center;

        .user-name {
          font-size: 2em;
          height: 60%;
        }

        .user-stats {
          display: flex;
          gap: $default-padding * 4;
          .user-stat {
            display: flex;
            flex-direction: column;
            align-items: center;
            padding-top: $default-padding;
            .stat-number,
            .stat-label {
              padding: 0 $default-padding * 0.5;
            }
            .stat-number {
              font-weight: bold;
              font-size: 1.5em;
            }
          }
        }

        @media screen and (max-width: $x-small-limit) {
          .user-name {
            font-size: 1.5em;
          }

          .user-stats {
            gap: $default-padding * 2;
            .user-stat {
              .stat-number {
                font-weight: bold;
                font-size: 1.2em;
              }

              &.hide-small {
                display: none;
              }
            }
          }
        }
      }
    }
  }
</style>
