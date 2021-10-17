<template>
  <div id="user-infos">
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
      <button @click="$router.push('/profile/edit')">
        {{ t('user.PROFILE.EDIT') }}
      </button>
      <button @click="$router.push('/')">{{ t('common.HOME') }}</button>
    </div>
  </div>
</template>

<script lang="ts">
  import { format } from 'date-fns'
  import { PropType, computed, defineComponent } from 'vue'
  import { useI18n } from 'vue-i18n'

  import { IAuthUserProfile } from '@/types/user'

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
      return { birthDate, registrationDate, t }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base.scss';
  #user-infos {
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
</style>
