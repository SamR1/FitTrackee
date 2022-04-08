<template>
  <div id="admin-app" class="admin-card">
    <Card>
      <template #title>{{ $t('admin.APP_CONFIG.TITLE') }}</template>
      <template #content>
        <form class="admin-form" @submit.prevent="onSubmit">
          <div class="federation">
            <label for="federation_enabled">
              {{ $t('admin.APP_CONFIG.FEDERATION_ENABLED') }}:
            </label>
            <div class="federation-checkbox">
              <input
                v-if="edition"
                id="federation_enabled"
                name="federation_enabled"
                type="checkbox"
                v-model="appData.federation_enabled"
              />
              <i
                v-else
                :class="`fa fa${
                  appData.federation_enabled ? '-check' : ''
                }-square-o`"
                aria-hidden="true"
              />
            </div>
          </div>
          <label for="admin_contact">
            {{ $t('admin.APP_CONFIG.ADMIN_CONTACT') }}:
            <input
              class="no-contact"
              v-if="!edition && !appData.admin_contact"
              :value="$t('admin.APP_CONFIG.NO_CONTACT_EMAIL')"
              disabled
            />
            <input
              v-else
              id="admin_contact"
              name="admin_contact"
              type="email"
              v-model="appData.admin_contact"
              :disabled="!edition"
            />
          </label>
          <label for="max_users">
            {{ $t('admin.APP_CONFIG.MAX_USERS_LABEL') }}:
            <input
              id="max_users"
              name="max_users"
              type="number"
              min="0"
              v-model="appData.max_users"
              :disabled="!edition"
            />
          </label>
          <div class="user-limit-help">
            <span class="info-box">
              <i class="fa fa-info-circle" aria-hidden="true" />
              {{ $t('admin.APP_CONFIG.MAX_USERS_HELP') }}
            </span>
          </div>
          <label for="max_single_file_size">
            {{ $t('admin.APP_CONFIG.SINGLE_UPLOAD_MAX_SIZE_LABEL') }}:
            <input
              id="max_single_file_size"
              name="max_single_file_size"
              type="number"
              step="0.1"
              min="0"
              v-model="appData.max_single_file_size"
              :disabled="!edition"
            />
          </label>
          <label for="max_zip_file_size">
            {{ $t('admin.APP_CONFIG.ZIP_UPLOAD_MAX_SIZE_LABEL') }}:
            <input
              id="max_zip_file_size"
              name="max_zip_file_size"
              type="number"
              step="0.1"
              min="0"
              v-model="appData.max_zip_file_size"
              :disabled="!edition"
            />
          </label>
          <label for="gpx_limit_import">
            {{ $t('admin.APP_CONFIG.MAX_FILES_IN_ZIP_LABEL') }}:
            <input
              id="gpx_limit_import"
              name="gpx_limit_import"
              type="number"
              min="0"
              v-model="appData.gpx_limit_import"
              :disabled="!edition"
            />
          </label>
          <ErrorMessage :message="errorMessages" v-if="errorMessages" />
          <div class="form-buttons" v-if="edition">
            <button class="confirm" type="submit">
              {{ $t('buttons.SUBMIT') }}
            </button>
            <button class="cancel" @click.prevent="onCancel">
              {{ $t('buttons.CANCEL') }}
            </button>
          </div>
          <div class="form-buttons" v-else>
            <button
              class="confirm"
              @click.prevent="$router.push('/admin/application/edit')"
            >
              {{ $t('buttons.EDIT') }}
            </button>
            <button class="cancel" @click.prevent="$router.push('/admin')">
              {{ $t('admin.BACK_TO_ADMIN') }}
            </button>
          </div>
        </form>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
  import {
    ComputedRef,
    computed,
    reactive,
    withDefaults,
    onBeforeMount,
    toRefs,
  } from 'vue'
  import { useRouter } from 'vue-router'

  import { ROOT_STORE } from '@/store/constants'
  import { TAppConfig, TAppConfigForm } from '@/types/application'
  import { useStore } from '@/use/useStore'
  import { getFileSizeInMB } from '@/utils/files'

  interface Props {
    appConfig: TAppConfig
    edition?: boolean
  }
  const props = withDefaults(defineProps<Props>(), {
    edition: false,
  })
  const { edition } = toRefs(props)

  const store = useStore()
  const router = useRouter()

  const appData: TAppConfigForm = reactive({
    admin_contact: '',
    federation_enabled: false,
    max_users: 0,
    max_single_file_size: 0,
    max_zip_file_size: 0,
    gpx_limit_import: 0,
  })
  const errorMessages: ComputedRef<string | string[] | null> = computed(
    () => store.getters[ROOT_STORE.GETTERS.ERROR_MESSAGES]
  )

  onBeforeMount(() => {
    if (props.appConfig) {
      updateForm(props.appConfig)
    }
  })

  function updateForm(appConfig: TAppConfig) {
    Object.keys(appData).map((key) => {
      ['max_single_file_size', 'max_zip_file_size'].includes(key)
        ? // eslint-disable-next-line @typescript-eslint/ban-ts-comment
          // @ts-ignore
          (appData[key] = getFileSizeInMB(appConfig[key]))
        : // eslint-disable-next-line @typescript-eslint/ban-ts-comment
          // @ts-ignore
          (appData[key] = appConfig[key])
    })
  }
  function onCancel() {
    updateForm(props.appConfig)
    store.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    router.push('/admin/application')
  }
  function onSubmit() {
    const formData: TAppConfigForm = Object.assign({}, appData)
    formData.max_single_file_size *= 1048576
    formData.max_zip_file_size *= 1048576
    store.dispatch(ROOT_STORE.ACTIONS.UPDATE_APPLICATION_CONFIG, formData)
  }
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';

  .user-limit-help {
    display: flex;
    span {
      font-style: italic;
    }
    .fa-info-circle {
      margin-right: $default-margin;
    }
  }

  .federation {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: $default-margin 0;

    .federation-checkbox {
      width: 51%;
      margin-right: $default-margin * 5;

      input[type='checkbox'] {
        margin-left: -$default-padding;
      }

      @media screen and (max-width: $medium-limit) {
        margin-right: 0;
        input[type='checkbox'] {
          margin-left: -$default-padding;
        }
      }
    }
  }

  .no-contact {
    font-style: italic;
  }
</style>
