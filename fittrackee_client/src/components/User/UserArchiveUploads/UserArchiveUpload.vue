<template>
  <div id="archive-upload">
    <div v-if="loading">
      <Loader />
    </div>
    <div v-else-if="uploadTask.id" class="description-list">
      <dl>
        <dt>{{ $t('common.CREATION_DATE') }}:</dt>
        <dd>{{ uploadTask.created_at }}</dd>
      </dl>
      <dl>
        <dt>{{ $t('common.FILES') }}:</dt>
        <dd>{{ uploadTask.files_count }}</dd>
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
      <dl v-if="uploadTask.status.match('error')">
        <dt>{{ $t('user.PROFILE.ARCHIVE_UPLOADS.ERRORED_FILES') }}:</dt>
        <dd>
          <ul class="errored-files">
            <li
              v-for="[file, error] of Object.entries(uploadTask.errored_files)"
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
    <div class="buttons">
      <button @click="loadUploadTask()">
        {{ $t('buttons.REFRESH') }}
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
  import { computed, onMounted, onUnmounted } from 'vue'
  import type { ComputedRef } from 'vue'
  import { useI18n } from 'vue-i18n'
  import { useRoute } from 'vue-router'

  import { AUTH_USER_STORE } from '@/store/constants'
  import type { IArchiveUploadTask } from '@/types/user'
  import { useStore } from '@/use/useStore'

  const store = useStore()
  const route = useRoute()
  const { t, te } = useI18n()

  const uploadTask: ComputedRef<IArchiveUploadTask> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.ARCHIVE_UPLOAD_TASK]
  )
  const loading: ComputedRef<boolean> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.ARCHIVE_UPLOAD_TASKS_LOADING]
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
    .no-uploads {
      margin: $default-padding 0;
    }
    .errored-files {
      padding-left: 10px;
    }
    .buttons {
      display: flex;
      gap: $default-padding;
      button {
        text-transform: capitalize;
      }
    }
  }
</style>
