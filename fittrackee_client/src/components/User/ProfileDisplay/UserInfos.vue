<template>
  <div id="user-infos" class="description-list">
    <Modal
      v-if="displayModal"
      :title="$t('common.CONFIRMATION')"
      message="admin.CONFIRM_USER_ACCOUNT_DELETION"
      :strongMessage="user.username"
      @confirmAction="deleteUserAccount(user.username)"
      @cancelAction="updateDisplayModal(false)"
    />
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
    <div class="profile-buttons" v-if="fromAdmin">
      <button
        class="danger"
        v-if="authUser.username !== user.username"
        @click.prevent="updateDisplayModal(true)"
      >
        {{ $t('admin.DELETE_USER') }}
      </button>
      <button @click="$router.go(-1)">{{ $t('buttons.BACK') }}</button>
    </div>
    <div class="profile-buttons" v-else>
      <button @click="$router.push('/profile/edit')">
        {{ $t('user.PROFILE.EDIT') }}
      </button>
      <button @click="$router.push('/')">{{ $t('common.HOME') }}</button>
    </div>
  </div>
</template>

<script lang="ts">
  import { format } from 'date-fns'
  import {
    ComputedRef,
    PropType,
    Ref,
    computed,
    defineComponent,
    ref,
  } from 'vue'

  import { AUTH_USER_STORE } from '@/store/constants'
  import { IUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'

  export default defineComponent({
    name: 'UserInfos',
    props: {
      user: {
        type: Object as PropType<IUserProfile>,
        required: true,
      },
      fromAdmin: {
        type: Boolean,
        default: false,
      },
    },
    setup(props) {
      const store = useStore()
      const authUser: ComputedRef<IUserProfile> = computed(
        () => store.getters[AUTH_USER_STORE.GETTERS.AUTH_USER_PROFILE]
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
      let displayModal: Ref<boolean> = ref(false)

      function updateDisplayModal(value: boolean) {
        displayModal.value = value
      }
      function deleteUserAccount(username: string) {
        store.dispatch(AUTH_USER_STORE.ACTIONS.DELETE_ACCOUNT, { username })
      }

      return {
        authUser,
        birthDate,
        displayModal,
        registrationDate,
        deleteUserAccount,
        updateDisplayModal,
      }
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
