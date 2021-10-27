<template>
  <div id="admin-app" class="admin-card">
    <Card>
      <template #title>{{ $t('admin.APP_CONFIG.TITLE') }}</template>
      <template #content>
        <form class="admin-form" @submit.prevent="onSubmit">
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

<script lang="ts">
  import {
    ComputedRef,
    PropType,
    computed,
    defineComponent,
    reactive,
    onBeforeMount,
  } from 'vue'
  import { useRouter } from 'vue-router'

  import { ROOT_STORE } from '@/store/constants'
  import { TAppConfig, TAppConfigForm } from '@/types/application'
  import { useStore } from '@/use/useStore'
  import { getFileSizeInMB } from '@/utils/files'

  export default defineComponent({
    name: 'AdminApplication',
    props: {
      appConfig: {
        type: Object as PropType<TAppConfig>,
        required: true,
      },
      edition: {
        type: Boolean,
        default: false,
      },
    },
    setup(props) {
      const store = useStore()
      const router = useRouter()
      const appData: TAppConfigForm = reactive({
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
          ;['max_single_file_size', 'max_zip_file_size'].includes(key)
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

      return { appData, errorMessages, onCancel, onSubmit }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base.scss';

  .user-limit-help {
    display: flex;
    span {
      font-style: italic;
    }
    .fa-info-circle {
      margin-right: $default-margin;
    }
  }
</style>
