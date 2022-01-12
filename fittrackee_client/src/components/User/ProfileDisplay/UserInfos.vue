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
    <div
      class="profile-buttons"
      v-if="authUser && authUser.admin && $route.query.from === 'admin'"
    >
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
      <button
        v-if="
          $route.path === '/profile' ||
          (authUser && authUser.username === user.username)
        "
        @click="$router.push('/profile/edit')"
      >
        {{ $t('user.PROFILE.EDIT') }}
      </button>
      <UserRelationshipActions
        v-if="authUser?.username"
        :authUser="authUser"
        :user="user"
        from="userInfos"
      />
      <div>
        <button
          @click="
            $route.query.from === 'users' ? $router.go(-1) : $router.push('/')
          "
        >
          {{
            $t($route.query.from === 'users' ? 'buttons.BACK' : 'common.HOME')
          }}
        </button>
      </div>
    </div>

    <ErrorMessage :message="errorMessages" v-if="errorMessages" />
  </div>
</template>

<script setup lang="ts">
  import { format } from 'date-fns'
  import { Ref, computed, ref, toRefs, ComputedRef } from 'vue'

  import UserRelationshipActions from '@/components/User/UserRelationshipActions.vue'
  import { ROOT_STORE, USERS_STORE } from '@/store/constants'
  import { IAuthUserProfile, IUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'

  interface Props {
    user: IUserProfile
    authUser?: IAuthUserProfile
  }
  const props = defineProps<Props>()

  const store = useStore()

  const { authUser, user } = toRefs(props)
  const errorMessages: ComputedRef<string | string[] | null> = computed(
    () => store.getters[ROOT_STORE.GETTERS.ERROR_MESSAGES]
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
    store.dispatch(USERS_STORE.ACTIONS.DELETE_USER_ACCOUNT, { username })
  }
</script>

<style lang="scss" scoped>
  #user-infos {
    .user-bio {
      white-space: pre-wrap;
    }
  }
</style>
