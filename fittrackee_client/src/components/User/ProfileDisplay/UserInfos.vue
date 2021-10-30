<template>
  <div id="user-infos" class="description-list">
    <dl>
      <dt>{{ $t('user.PROFILE.REGISTRATION_DATE') }}:</dt>
      <dd>{{ registrationDate }}</dd>
      <dt>{{ $t('user.PROFILE.FIRST_NAME') }}:</dt>
      <dd>{{ user.first_name }}</dd>
      <dt>{{ $t('user.PROFILE.LAST_NAME') }}:</dt>
      <dd>{{ user.last_name }}</dd>
      <dt>{{ $t('user.PROFILE.BIRTH_DATE') }}:</dt>
      <dd>{{ birthDate }}</dd>
      <dt>{{ $t('user.PROFILE.LOCATION') }}:</dt>
      <dd>{{ user.location }}</dd>
      <dt>{{ $t('user.PROFILE.BIO') }}:</dt>
      <dd class="user-bio">
        {{ user.bio }}
      </dd>
    </dl>
    <div class="profile-buttons">
      <button @click="$router.push('/profile/edit')">
        {{ $t('user.PROFILE.EDIT') }}
      </button>
      <button @click="$router.push('/')">{{ $t('common.HOME') }}</button>
    </div>
  </div>
</template>

<script lang="ts">
  import { format } from 'date-fns'
  import { PropType, computed, defineComponent } from 'vue'

  import { IUserProfile } from '@/types/user'

  export default defineComponent({
    name: 'UserInfos',
    props: {
      user: {
        type: Object as PropType<IUserProfile>,
        required: true,
      },
    },
    setup(props) {
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
      return { birthDate, registrationDate }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base.scss';
  #user-infos {
    .user-bio {
      white-space: pre-wrap;
    }
    .profile-buttons {
      display: flex;
      gap: $default-padding;
    }
  }
</style>
