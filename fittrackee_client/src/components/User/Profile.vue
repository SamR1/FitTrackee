<template>
  <div id="user-profile">
    <div class="box user-header">
      <div class="user-picture">
        <img
          v-if="authUserPictureUrl !== ''"
          class="nav-profile-user-img"
          :alt="t('user.USER_PICTURE')"
          :src="authUserPictureUrl"
        />
        <div v-else class="no-picture">
          <i class="fa fa-user-circle-o" aria-hidden="true" />
        </div>
      </div>
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
    <div class="box user-infos">
      <dl>
        <dt>{{ t('user.PROFILE.REGISTRATION_DATE') }}:</dt>
        <dd>{{ registrationDate }}</dd>
      </dl>
      <dl>
        <dt>{{ t('user.PROFILE.FIRST_NAME') }}:</dt>
        <dd>{{ user.first_name }}</dd>
      </dl>
      <dl>
        <dt>{{ t('user.PROFILE.LAST_NAME') }}:</dt>
        <dd>{{ user.last_name }}</dd>
      </dl>
      <dl>
        <dt>{{ t('user.PROFILE.BIRTH_DATE') }}:</dt>
        <dd>{{ birthDate }}</dd>
      </dl>
      <dl>
        <dt>{{ t('user.PROFILE.LOCATION') }}:</dt>
        <dd>{{ user.location }}</dd>
      </dl>
      <dl>
        <dt>{{ t('user.PROFILE.BIO') }}:</dt>
        <dd class="user-bio">
          {{ user.bio }}
        </dd>
      </dl>
      <div class="profile-buttons">
        <button>{{ t('user.PROFILE.EDIT') }}</button>
        <button @click="$router.push('/')">{{ t('common.HOME') }}</button>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
  import { format } from 'date-fns'
  import { computed, ComputedRef, defineComponent, PropType } from 'vue'
  import { useI18n } from 'vue-i18n'

  import { IAuthUserProfile } from '@/types/user'
  import { getApiUrl } from '@/utils'

  export default defineComponent({
    name: 'Profile',
    components: {},
    props: {
      user: {
        type: Object as PropType<IAuthUserProfile>,
        required: true,
      },
    },
    setup(props) {
      const { t } = useI18n()
      const authUserPictureUrl: ComputedRef<string> = computed(() =>
        props.user.picture
          ? `${getApiUrl()}/users/${props.user.username}/picture?${Date.now()}`
          : ''
      )
      const registrationDate = computed(() =>
        props.user.created_at
          ? format(new Date(props.user.created_at), 'dd/MM/yyyy HH:mm')
          : ''
      )
      const birthDate = computed(() =>
        props.user.birth_date
          ? format(new Date(props.user.birth_date), 'dd/MM/yyyy')
          : ''
      )
      return { t, authUserPictureUrl, birthDate, registrationDate }
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

      .user-picture {
        display: flex;
        justify-content: center;
        align-items: center;
        min-width: 30%;
        img {
          border-radius: 50%;
          height: 90px;
          width: 90px;
        }
        .no-picture {
          color: var(--app-a-color);
          font-size: 5.5em;
        }
      }

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

    .user-infos {
      dl {
        overflow: hidden;
        width: 100%;
        padding: 0 $default-padding;
        dt {
          font-weight: bold;
          float: left;
          width: 25%;
        }
        dd {
          float: left;
        }
      }
      @media screen and (max-width: $x-small-limit) {
        dl {
          overflow: auto;
          width: initial;
          dt {
            font-weight: bold;
            float: none;
            width: initial;
          }
          dd {
            float: none;
          }
        }
      }

      .user-bio {
        white-space: pre-wrap;
      }
      .profile-buttons {
        display: flex;
        gap: $default-padding;
      }
    }
  }
</style>
