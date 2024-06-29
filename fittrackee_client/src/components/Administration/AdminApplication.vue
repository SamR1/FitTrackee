<template>
  <div id="admin-app" class="admin-card">
    <Card>
      <template #title>{{ $t('admin.APP_CONFIG.TITLE') }}</template>
      <template #content>
        <form class="admin-form" @submit.prevent="onSubmit">
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
          <div class="admin-help">
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
          <label for="stats_workouts_limit">
            {{ $t('admin.APP_CONFIG.STATS_WORKOUTS_LIMIT_LABEL') }}:
            <input
              id="stats_workouts_limit"
              name="stats_workouts_limit"
              type="number"
              min="0"
              v-model="appData.stats_workouts_limit"
              :disabled="!edition"
            />
          </label>
          <div class="admin-help">
            <span class="info-box">
              <i class="fa fa-info-circle" aria-hidden="true" />
              {{ $t('admin.APP_CONFIG.STATS_WORKOUTS_LIMIT_HELP') }}
            </span>
          </div>
          <label class="about-label" for="about">
            {{ $t('admin.ABOUT.TEXT') }}:
          </label>
          <span class="textarea-description">
            {{ $t('admin.ABOUT.DESCRIPTION') }}
          </span>
          <textarea
            v-if="edition"
            id="about"
            name="about"
            rows="10"
            v-model="appData.about"
          />
          <div
            v-else
            v-html="
              snarkdown(
                linkifyAndClean(
                  appData.about ? appData.about : $t('admin.NO_TEXT_ENTERED')
                )
              )
            "
            class="textarea-content"
          />
          <label class="privacy-policy-label" for="privacy_policy">
            {{ capitalize($t('privacy_policy.TITLE')) }}:
          </label>
          <span class="textarea-description">
            {{ $t('admin.PRIVACY_POLICY_DESCRIPTION') }}
          </span>
          <textarea
            v-if="edition"
            id="privacy_policy"
            name="privacy_policy"
            rows="20"
            v-model="appData.privacy_policy"
          />
          <div
            v-else
            v-html="
              snarkdown(
                linkifyAndClean(
                  appData.privacy_policy
                    ? appData.privacy_policy
                    : $t('admin.NO_TEXT_ENTERED')
                )
              )
            "
            class="textarea-content"
          />
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
  import snarkdown from 'snarkdown'
  import { capitalize, computed, reactive, onBeforeMount, toRefs } from 'vue'
  import type { ComputedRef } from 'vue'
  import { useRouter } from 'vue-router'

  import { ROOT_STORE } from '@/store/constants'
  import type { TAppConfig, TAppConfigForm } from '@/types/application'
  import type { IEquipmentError } from '@/types/equipments'
  import { useStore } from '@/use/useStore'
  import { getFileSizeInMB } from '@/utils/files'
  import { linkifyAndClean } from '@/utils/inputs'

  interface Props {
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
    max_users: 0,
    max_single_file_size: 0,
    max_zip_file_size: 0,
    gpx_limit_import: 0,
    about: '',
    privacy_policy: '',
    stats_workouts_limit: 0,
  })
  const errorMessages: ComputedRef<string | string[] | IEquipmentError | null> =
    computed(() => store.getters[ROOT_STORE.GETTERS.ERROR_MESSAGES])

  const appConfig: ComputedRef<TAppConfig> = computed(
    () => store.getters[ROOT_STORE.GETTERS.APP_CONFIG]
  )
  onBeforeMount(() => {
    if (appConfig.value) {
      updateForm(appConfig.value)
    }
  })

  function updateForm(appConfig: TAppConfig) {
    Object.keys(appData).map((key) => {
      ;['max_single_file_size', 'max_zip_file_size'].includes(key)
        ? // eslint-disable-next-line @typescript-eslint/ban-ts-comment
          // @ts-ignore
          (appData[key] = getFileSizeInMB(appConfig[key]))
        : ['about', 'privacy_policy'].includes(key)
          ? // eslint-disable-next-line @typescript-eslint/ban-ts-comment
            // @ts-ignore
            (appData[key] = appConfig[key] !== null ? appConfig[key] : '')
          : // eslint-disable-next-line @typescript-eslint/ban-ts-comment
            // @ts-ignore
            (appData[key] = appConfig[key])
    })
  }
  function onCancel() {
    updateForm(appConfig.value)
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

  #admin-app {
    .admin-help {
      display: flex;
      span {
        font-style: italic;
      }
      .fa-info-circle {
        margin-right: $default-margin;
      }
    }
    .no-contact {
      font-style: italic;
    }

    textarea {
      margin-bottom: $default-padding;
    }
    .textarea-description {
      font-style: italic;
    }
    .textarea-content {
      margin-bottom: $default-margin;
      padding: $default-padding;
    }
  }

  .no-contact {
    font-style: italic;
  }
</style>
