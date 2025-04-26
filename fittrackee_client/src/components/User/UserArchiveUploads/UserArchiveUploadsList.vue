<template>
  <div id="upload-tasks-list">
    <h1>{{ capitalize($t('user.PROFILE.TABS.ARCHIVE-UPLOADS')) }}</h1>
    <div v-if="loading">
      <Loader />
    </div>
    <div id="user-upload-tasks" v-else-if="uploadTasks.length > 0">
      <ul class="last-upload-tasks">
        <li v-for="task in uploadTasks" :key="task.id">
          <div class="task-title">
            <router-link
              :to="`/profile/archive-uploads/${task.id}`"
              :title="task.original_file_name"
            >
              {{ task.original_file_name }}
            </router-link>
            <span>
              ({{
                $t('user.PROFILE.ARCHIVE_UPLOADS.FILES_COUNT', {
                  count: task.files_count,
                })
              }})
            </span>
            <span>
              {{
                formatDate(
                  task.created_at,
                  displayOptions.timezone,
                  displayOptions.dateFormat
                )
              }}
            </span>
            <span
              class="info-box task-status"
              :class="{
                success: task.status === 'successful',
                errored: task.status === 'errored',
              }"
            >
              {{ $t(`user.TASKS.STATUS.${task.status}`) }}
              <span v-if="task.status === 'in_progress'">
                ({{ task.progress }}%)
              </span>
            </span>
          </div>
        </li>
      </ul>
      <Pagination
        :pagination="pagination"
        path="/profile/archive-uploads"
        :query="query"
      />
    </div>
    <div v-else>
      <p class="no-upload-tasks">{{ $t('user.PROFILE.NO_ARCHIVE_UPLOADS') }}</p>
    </div>
    <ErrorMessage
      v-if="errorMessages"
      :message="errorMessages"
      :no-margin="true"
    />
    <div>
      <button @click="$router.push('/')">{{ $t('common.HOME') }}</button>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { capitalize, computed, onBeforeMount, watch } from 'vue'
  import type { ComputedRef } from 'vue'
  import { useRoute } from 'vue-router'
  import type { LocationQuery } from 'vue-router'

  import Loader from '@/components/Common/Loader.vue'
  import Pagination from '@/components/Common/Pagination.vue'
  import useApp from '@/composables/useApp.ts'
  import { AUTH_USER_STORE } from '@/store/constants'
  import type { IPagination } from '@/types/api'
  import type { IArchiveUploadTask } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { defaultPage, getNumberQueryValue } from '@/utils/api'
  import { formatDate } from '@/utils/dates'

  const store = useStore()
  const route = useRoute()

  const { displayOptions, errorMessages } = useApp()

  let query: { page?: number } = getTasksQuery(route.query)

  const uploadTasks: ComputedRef<IArchiveUploadTask[]> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.ARCHIVE_UPLOAD_TASKS]
  )
  const pagination: ComputedRef<IPagination> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.ARCHIVE_UPLOAD_TASKS_PAGINATION]
  )
  const loading: ComputedRef<boolean> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.ARCHIVE_UPLOAD_TASKS_LOADING]
  )

  function getTasksQuery(newQuery: LocationQuery): { page?: number } {
    const tasksQuery: { page?: number } = {}
    if (newQuery.page) {
      tasksQuery.page = getNumberQueryValue(newQuery.page, defaultPage)
    }
    return tasksQuery
  }
  function loadArchiveUploadTasks(payload: { page?: number }) {
    store.dispatch(AUTH_USER_STORE.ACTIONS.GET_ARCHIVE_UPLOAD_TASKS, payload)
  }

  watch(
    () => route.query,
    async (newQuery) => {
      query = getTasksQuery(newQuery)
      loadArchiveUploadTasks(query)
    }
  )

  onBeforeMount(() => {
    loadArchiveUploadTasks(query)
  })
</script>

<style scoped lang="scss">
  @use '~@/scss/vars.scss' as *;

  #upload-tasks-list {
    padding: 0 0 $default-padding;
    h1 {
      font-size: 1.05em;
      font-weight: bold;
    }
    ul {
      list-style: square;
      li {
        margin-left: $default-margin;
        padding: $default-padding * 0.5;
        div {
          display: flex;
          flex-wrap: wrap;
          gap: $default-padding * 0.5;
        }
      }
    }
    .task-title {
      a {
        overflow: hidden;
        text-overflow: ellipsis;
      }
    }
    .task-status {
      margin: -2px 0 0 5px;
      padding: $default-padding * 0.5 $default-padding;
      &.success {
        background: var(--success-background-color);
        color: var(--success-color);
      }
      &.errored {
        background: var(--error-background-color);
        color: var(--error-color);
      }
    }
  }
</style>
