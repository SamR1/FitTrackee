<template>
  <div id="archive-upload">
    <Modal
      v-if="displayedModal"
      :title="$t('common.CONFIRMATION')"
      :message="
        $t(
          `user.PROFILE.ARCHIVE_UPLOADS.CONFIRM_TASK_${isDeletion ? 'DELETION' : 'ABORT'}`
        )
      "
      @confirmAction="doAction"
      @cancelAction="displayedModal = false"
      @keydown.esc="displayedModal = false"
    />
    <div v-if="loading">
      <Loader />
    </div>
    <div v-else-if="uploadTask.id" class="description-list">
      <dl>
        <dt>{{ $t('common.CREATION_DATE') }}:</dt>
        <dd>{{ uploadTask.created_at }}</dd>
      </dl>
      <dl v-if="uploadTask.original_file_name" class="file-name">
        <dt>{{ $t('user.PROFILE.ARCHIVE_UPLOADS.ARCHIVE') }}:</dt>
        <dd :title="uploadTask.original_file_name">
          {{ uploadTask.original_file_name }}
        </dd>
      </dl>
      <dl>
        <dt>{{ $t('common.FILES') }}:</dt>
        <dd>{{ uploadTask.files_count }}</dd>
      </dl>
      <dl v-if="sport">
        <dt>{{ capitalize($t('workouts.SPORT', 1)) }}:</dt>
        <dd>
          <SportBadge
            :sport="sport"
            :from="`?fromArchiveUploadId=${uploadTask.id}`"
          />
        </dd>
      </dl>
      <dl>
        <dt>{{ $t('user.PROFILE.ARCHIVE_UPLOADS.STATUS.LABEL') }}:</dt>
        <dd>
          {{ $t(`user.PROFILE.ARCHIVE_UPLOADS.STATUS.${uploadTask.status}`) }}
        </dd>
      </dl>
      <dl v-if="uploadTask.status === 'in_progress'">
        <dt>{{ $t('user.PROFILE.ARCHIVE_UPLOADS.PROGRESS') }}:</dt>
        <dd>{{ uploadTask.progress }}%</dd>
      </dl>
      <dl v-if="['aborted', 'errored'].includes(uploadTask.status)">
        <dt>{{ $t('user.PROFILE.ARCHIVE_UPLOADS.CREATED_WORKOUTS') }}:</dt>
        <dd>{{ uploadTask.new_workouts_count }}</dd>
      </dl>
      <dl
        v-if="
          uploadTask.status == 'errored' && uploadTask.errored_files.archive
        "
      >
        <dt>{{ $t('user.PROFILE.ARCHIVE_UPLOADS.ERRORED_FILES') }}:</dt>
        <dd>
          {{ $t('user.PROFILE.ARCHIVE_UPLOADS.ARCHIVE') }}:
          {{ getFileError(uploadTask.errored_files.archive) }}
        </dd>
      </dl>
      <dl
        v-if="
          ['aborted', 'errored'].includes(uploadTask.status) &&
          Object.keys(uploadTask.errored_files.files).length
        "
      >
        <dt>
          {{
            $t(
              'user.PROFILE.ARCHIVE_UPLOADS.ERRORED_FILES',
              Object.keys(uploadTask.errored_files.files).length
            )
          }}:
        </dt>
        <dd>
          <ul class="errored-files">
            <li
              v-for="[file, error] of Object.entries(
                uploadTask.errored_files.files
              )"
              :key="file"
            >
              {{ file }}: {{ getFileError(error) }}
            </li>
          </ul>
        </dd>
      </dl>
    </div>
    <div v-else>
      <div class="no-uploads">
        {{ $t('user.PROFILE.ARCHIVE_UPLOADS.NOT_FOUND') }}
      </div>
    </div>
    <ErrorMessage :message="errorMessages" v-if="errorMessages" />
    <div class="buttons">
      <button
        v-if="['queued', 'in_progress'].includes(uploadTask.status)"
        @click="loadUploadTask()"
      >
        {{ $t('buttons.REFRESH') }}
      </button>
      <button
        v-if="['queued', 'in_progress'].includes(uploadTask.status)"
        class="danger"
        @click="displayModal(false)"
      >
        {{ $t('buttons.ABORT') }}
      </button>
      <button
        v-if="['aborted', 'errored', 'successful'].includes(uploadTask.status)"
        class="danger"
        @click="displayModal(true)"
      >
        {{ $t('buttons.DELETE') }}
      </button>
      <button @click="$router.push('/profile/archive-uploads')">
        {{ $t('buttons.BACK') }}
      </button>
      <button @click="$router.push('/')">
        {{ $t('common.HOME') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { capitalize, computed, onMounted, onUnmounted, ref } from 'vue'
  import type { Ref, ComputedRef } from 'vue'
  import { useI18n } from 'vue-i18n'
  import { useRoute } from 'vue-router'

  import SportBadge from '@/components/Common/SportBadge.vue'
  import useApp from '@/composables/useApp.ts'
  import useSports from '@/composables/useSports.ts'
  import { AUTH_USER_STORE, ROOT_STORE } from '@/store/constants'
  import type { ITranslatedSport } from '@/types/sports.ts'
  import type { IArchiveUploadTask } from '@/types/user'
  import { useStore } from '@/use/useStore'

  const store = useStore()
  const route = useRoute()
  const { t, te } = useI18n()

  const { errorMessages } = useApp()
  const { translatedSports } = useSports()

  const displayedModal: Ref<boolean> = ref(false)
  const isDeletion: Ref<boolean> = ref(false)

  const uploadTask: ComputedRef<IArchiveUploadTask> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.ARCHIVE_UPLOAD_TASK]
  )
  const loading: ComputedRef<boolean> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.ARCHIVE_UPLOAD_TASKS_LOADING]
  )
  const sport: ComputedRef<ITranslatedSport | undefined> = computed(() =>
    uploadTask.value.sport_id
      ? translatedSports.value.find((s) => s.id === uploadTask.value.sport_id)
      : undefined
  )

  function loadUploadTask() {
    store.dispatch(
      AUTH_USER_STORE.ACTIONS.GET_ARCHIVE_UPLOAD_TASK,
      route.params.task_id as string
    )
  }
  function getFileError(error: string): string {
    if (te(`user.PROFILE.ARCHIVE_UPLOADS.ERRORS.${error}`)) {
      return t(`user.PROFILE.ARCHIVE_UPLOADS.ERRORS.${error}`)
    }
    return error
  }
  function displayModal(deletion: boolean) {
    store.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    displayedModal.value = true
    isDeletion.value = deletion
  }
  function doAction() {
    const action = isDeletion.value
      ? 'DELETE_ARCHIVE_UPLOAD_TASK'
      : 'ABORT_ARCHIVE_UPLOAD_TASK'
    store.dispatch(
      AUTH_USER_STORE.ACTIONS[action],
      route.params.task_id as string
    )
    displayedModal.value = false
  }

  onMounted(() => loadUploadTask())
  onUnmounted(() => {
    store.commit(
      AUTH_USER_STORE.MUTATIONS.SET_ARCHIVE_UPLOAD_TASK,
      {} as IArchiveUploadTask
    )
  })
</script>

<style lang="scss" scoped>
  @use '~@/scss/vars.scss' as *;

  #archive-upload {
    padding: $default-padding 0;
    h1 {
      font-size: 1.05em;
      font-weight: bold;
    }
    .file-name {
      dd {
        overflow: hidden;
        text-overflow: ellipsis;
      }
    }
    .no-uploads {
      margin: $default-padding 0;
    }
    .errored-files {
      padding-left: 10px;
    }
    .buttons {
      display: flex;
      gap: $default-padding;
    }
  }
</style>
