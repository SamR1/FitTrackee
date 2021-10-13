<template>
  <div id="user-profile-edition">
    <Modal
      v-if="displayModal"
      :title="t('common.CONFIRMATION')"
      :message="t('user.CONFIRM_ACCOUNT_DELETION')"
      @confirmAction="deleteAccount(user.username)"
      @cancelAction="updateDisplayModal(false)"
    />
    <Card>
      <template #title>{{ t('user.PROFILE.EDITION') }}</template>
      <template #content>
        <div class="profile-form form-box">
          <ErrorMessage :message="errorMessages" v-if="errorMessages" />
          <form @submit.prevent="updateProfile">
            <label class="form-items" for="email">
              {{ t('user.EMAIL') }}
              <input id="email" :value="user.email" disabled />
            </label>
            <label class="form-items" for="registrationDate">
              {{ t('user.PROFILE.REGISTRATION_DATE') }}
              <input id="registrationDate" :value="registrationDate" disabled />
            </label>
            <label class="form-items" for="password">
              {{ t('user.PASSWORD') }}
              <input
                id="password"
                type="password"
                v-model="userForm.password"
                :disabled="loading"
              />
            </label>
            <label class="form-items" for="passwordConfirmation">
              {{ t('user.PASSWORD_CONFIRMATION') }}
              <input
                id="passwordConfirmation"
                type="password"
                v-model="userForm.password_conf"
                :disabled="loading"
              />
            </label>
            <hr />
            <label class="form-items" for="first_name">
              {{ t('user.PROFILE.FIRST_NAME') }}
              <input
                id="first_name"
                v-model="userForm.first_name"
                :disabled="loading"
              />
            </label>
            <label class="form-items" for="last_name">
              {{ t('user.PROFILE.LAST_NAME') }}
              <input id="last_name" v-model="userForm.last_name" />
            </label>
            <label class="form-items" for="birth_date">
              {{ t('user.PROFILE.BIRTH_DATE') }}
              <input
                id="birth_date"
                type="date"
                class="birth-date"
                v-model="userForm.birth_date"
                :disabled="loading"
              />
            </label>
            <label class="form-items" for="location">
              {{ t('user.PROFILE.LOCATION') }}
              <input
                id="location"
                v-model="userForm.location"
                :disabled="loading"
              />
            </label>
            <label class="form-items">
              {{ t('user.PROFILE.BIO') }}
              <CustomTextArea
                name="bio"
                :charLimit="200"
                :input="userForm.bio"
                :disabled="loading"
                @updateValue="updateBio"
              />
            </label>
            <label class="form-items">
              {{ t('user.PROFILE.LANGUAGE') }}
              <select
                id="language"
                v-model="userForm.language"
                :disabled="loading"
              >
                <option
                  v-for="lang in availableLanguages"
                  :value="lang.value"
                  :key="lang.value"
                >
                  {{ lang.label }}
                </option>
              </select>
            </label>
            <label class="form-items" for="timezone">
              {{ t('user.PROFILE.TIMEZONE') }}
              <input
                id="timezone"
                v-model="userForm.timezone"
                :disabled="loading"
              />
            </label>
            <label class="form-items">
              {{ t('user.PROFILE.FIRST_DAY_OF_WEEK') }}
              <select id="weekm" v-model="userForm.weekm" :disabled="loading">
                <option
                  v-for="start in weekStart"
                  :value="start.value"
                  :key="start.value"
                >
                  {{ t(`user.PROFILE.${start.label}`) }}
                </option>
              </select>
            </label>
            <div class="form-buttons">
              <button class="confirm" type="submit">
                {{ t('buttons.SUBMIT') }}
              </button>
              <button class="danger" @click.prevent="updateDisplayModal(true)">
                {{ t('buttons.DELETE_MY_ACCOUNT') }}
              </button>
              <button class="cancel" @click.prevent="$router.go(-1)">
                {{ t('buttons.CANCEL') }}
              </button>
            </div>
          </form>
        </div>
      </template>
    </Card>
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
    reactive,
    ref,
    onMounted,
  } from 'vue'
  import { useI18n } from 'vue-i18n'

  import Card from '@/components/Common/Card.vue'
  import CustomTextArea from '@/components/Common/CustomTextArea.vue'
  import ErrorMessage from '@/components/Common/ErrorMessage.vue'
  import Modal from '@/components/Common/Modal.vue'
  import { ROOT_STORE, USER_STORE } from '@/store/constants'
  import { IAuthUserProfile, IUserPayload } from '@/types/user'
  import { useStore } from '@/use/useStore'

  export default defineComponent({
    name: 'ProfileEdition',
    components: {
      Card,
      CustomTextArea,
      ErrorMessage,
      Modal,
    },
    props: {
      user: {
        type: Object as PropType<IAuthUserProfile>,
        required: true,
      },
    },
    setup(props) {
      const { t, availableLocales } = useI18n()
      const store = useStore()
      const userForm: IUserPayload = reactive({
        password: '',
        password_conf: '',
        first_name: '',
        last_name: '',
        birth_date: '',
        location: '',
        bio: '',
        language: '',
        timezone: 'Europe/Paris',
        weekm: false,
      })
      const availableLanguages = availableLocales.map((l) => {
        return { label: l.toUpperCase(), value: l }
      })
      const weekStart = [
        {
          label: 'MONDAY',
          value: true,
        },
        {
          label: 'SUNDAY',
          value: false,
        },
      ]
      const registrationDate = computed(() =>
        props.user.created_at
          ? format(new Date(props.user.created_at), 'dd/MM/yyyy HH:mm')
          : ''
      )
      const loading = computed(
        () => store.getters[USER_STORE.GETTERS.USER_LOADING]
      )
      const errorMessages: ComputedRef<string | string[] | null> = computed(
        () => store.getters[ROOT_STORE.GETTERS.ERROR_MESSAGES]
      )
      let displayModal: Ref<boolean> = ref(false)

      onMounted(() => {
        if (props.user) {
          updateUserForm(props.user)
        }
      })

      function updateUserForm(user: IAuthUserProfile) {
        userForm.first_name = user.first_name ? user.first_name : ''
        userForm.last_name = user.last_name ? user.last_name : ''
        userForm.birth_date = user.birth_date
          ? format(new Date(user.birth_date), 'yyyy-MM-dd')
          : ''
        userForm.location = user.location ? user.location : ''
        userForm.bio = user.bio ? user.bio : ''
        userForm.language = user.language ? user.language : 'en'
        userForm.timezone = user.timezone ? user.timezone : 'Europe/Paris'
        userForm.weekm = user.weekm ? user.weekm : false
      }
      function updateBio(value: string) {
        userForm.bio = value
      }
      function updateProfile() {
        store.dispatch(USER_STORE.ACTIONS.UPDATE_USER_PROFILE, userForm)
      }
      function updateDisplayModal(value: boolean) {
        displayModal.value = value
      }
      function deleteAccount(username: string) {
        store.dispatch(USER_STORE.ACTIONS.DELETE_ACCOUNT, { username })
      }

      return {
        availableLanguages,
        displayModal,
        errorMessages,
        loading,
        registrationDate,
        t,
        userForm,
        weekStart,
        deleteAccount,
        updateBio,
        updateDisplayModal,
        updateProfile,
      }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base.scss';

  #user-profile-edition {
    margin: auto;
    width: 700px;
    @media screen and (max-width: $medium-limit) {
      width: 100%;
      margin: 0 auto 50px auto;
    }

    .profile-form {
      display: flex;
      flex-direction: column;

      hr {
        border-color: var(--card-border-color);
        border-width: 1px 0 0 0;
      }

      .form-items {
        display: flex;
        flex-direction: column;

        input {
          margin: $default-padding * 0.5 0;
        }

        select {
          height: 35px;
          padding: $default-padding * 0.5 0;
        }
        ::v-deep(.custom-textarea) {
          textarea {
            padding: $default-padding * 0.5;
          }
        }

        .form-item {
          display: flex;
          flex-direction: column;
          padding: $default-padding;
        }
        .birth-date {
          height: 20px;
        }
      }

      .form-buttons {
        display: flex;
        padding: $default-padding 0;
        gap: $default-padding;
      }
    }
  }
</style>
