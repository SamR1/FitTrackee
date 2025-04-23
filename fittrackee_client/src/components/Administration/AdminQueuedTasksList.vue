<template>
  <div id="admin-queued-tasks-list" class="admin-card" v-if="taskType">
    <Card>
      <template #title>
        {{ $t(`admin.QUEUED_TASKS.TASK_TYPES.${taskType}`) }}
      </template>
      <template #content>
        <template v-if="queuedTasks.length > 0">
          <div class="top">
            <div>
              <span class="total">{{ $t('common.TOTAL') }} </span>:
              {{ pagination.total }}
            </div>
            <button
              v-if="queuedTasks.length > 2"
              class="top-button"
              @click.prevent="$router.push('/admin/queued-tasks')"
            >
              {{ $t('buttons.BACK') }}
            </button>
          </div>

          <div class="tasks-help">
            <div class="info-box">
              <i class="fa fa-info-circle" aria-hidden="true" />
              {{ $t('admin.QUEUED_TASKS.LIST_DESCRIPTION') }}
            </div>
          </div>

          <div class="responsive-table queue-table">
            <table>
              <thead>
                <tr>
                  <th class="id">#</th>
                  <th class="user">
                    {{ capitalize($t('user.USER')) }}
                  </th>
                  <th>
                    {{ $t('common.CREATION_DATE') }}
                  </th>
                  <th>
                    <span v-if="taskType === 'workouts_archive_upload'">
                      {{ $t('user.PROFILE.ARCHIVE_UPLOADS.ARCHIVE') }}
                    </span>
                  </th>
                  <th v-if="taskType === 'workouts_archive_upload'">
                    {{ $t('common.FILES') }}
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="task in queuedTasks" :key="task.id">
                  <td class="id">
                    <span class="cell-heading"> # </span>
                    {{ task.id }}
                  </td>
                  <td class="user">
                    <span class="cell-heading">
                      {{ $t('user.USER') }}
                    </span>
                    <div class="task-user">
                      <UserPicture :user="task.user" />
                      <Username :user="task.user" />
                    </div>
                  </td>
                  <td>
                    <span class="cell-heading">
                      {{ $t('common.CREATION_DATE') }}
                    </span>
                    {{ formatTaskDate(task.created_at) }}
                  </td>
                  <td v-if="taskType === 'workouts_archive_upload'">
                    <span class="cell-heading">
                      {{ $t('user.PROFILE.ARCHIVE_UPLOADS.ARCHIVE') }}
                    </span>
                    {{
                      task.file_size === null
                        ? ''
                        : getReadableFileSizeAsText(task.file_size)
                    }}
                  </td>
                  <td v-if="taskType === 'workouts_archive_upload'">
                    <span class="cell-heading">
                      {{ $t('common.FILES') }}
                    </span>
                    {{ task.files_count }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <Pagination
            :pagination="pagination"
            :path="`/admin/queued-tasks/${taskType}`"
            :query="query"
          />
        </template>
        <div v-else class="no-queued-tasks">
          {{ $t('admin.QUEUED_TASKS.NO_QUEUED_TASKS') }}
        </div>

        <ErrorMessage :message="errorMessages" v-if="errorMessages" />

        <div class="buttons">
          <button
            @click.prevent="
              $router.push(
                `/admin/queued-tasks/${
                  taskType === 'workouts_archive_upload'
                    ? 'user_data_export'
                    : 'workouts_archive_upload'
                }`
              )
            "
          >
            {{ $t('admin.QUEUED_TASKS.VIEW_OTHER_TASKS') }}
          </button>
          <button @click.prevent="$router.push('/admin/queued-tasks')">
            {{ $t('buttons.BACK') }}
          </button>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
  import { computed, capitalize, onBeforeMount, watch, onUnmounted } from 'vue'
  import type { ComputedRef } from 'vue'
  import { type LocationQuery, useRoute } from 'vue-router'

  import Pagination from '@/components/Common/Pagination.vue'
  import Username from '@/components/User/Username.vue'
  import UserPicture from '@/components/User/UserPicture.vue'
  import useApp from '@/composables/useApp.ts'
  import { ROOT_STORE } from '@/store/constants'
  import type { IPagination } from '@/types/api.ts'
  import type { IQueuedTask, TTaskType } from '@/types/application.ts'
  import { useStore } from '@/use/useStore'
  import { defaultPage, getNumberQueryValue } from '@/utils/api.ts'
  import { formatDate } from '@/utils/dates.ts'
  import { getReadableFileSizeAsText } from '@/utils/files.ts'

  const route = useRoute()
  const store = useStore()

  const { displayOptions, errorMessages } = useApp()

  let query: { page?: number } = getTasksQuery(route.query)
  const taskType = computed(() => route.params.taskType as TTaskType)
  const queuedTasks: ComputedRef<IQueuedTask[]> = computed(
    () => store.getters[ROOT_STORE.GETTERS.QUEUED_TASKS]
  )
  const pagination: ComputedRef<IPagination> = computed(
    () => store.getters[ROOT_STORE.GETTERS.QUEUED_TASKS_PAGINATION]
  )

  function getTasksQuery(newQuery: LocationQuery): { page?: number } {
    const tasksQuery: { page?: number } = {}
    if (newQuery.page) {
      tasksQuery.page = getNumberQueryValue(newQuery.page, defaultPage)
    }
    return tasksQuery
  }
  function loadQueuedTasks(query: { page?: number }) {
    store.dispatch(ROOT_STORE.ACTIONS.GET_QUEUED_TASKS_LIST, {
      page: query.page,
      taskType: taskType.value,
    })
  }
  function formatTaskDate(taskDate: string) {
    return taskDate
      ? formatDate(
          taskDate,
          displayOptions.value.timezone,
          displayOptions.value.dateFormat,
          {
            withTime: true,
            language: null,
            withSeconds: true,
          }
        )
      : ''
  }

  watch(
    () => route.query,
    (newQuery: LocationQuery) => loadQueuedTasks(getTasksQuery(newQuery))
  )

  onBeforeMount(() => loadQueuedTasks(query))
  onUnmounted(() => store.commit(ROOT_STORE.MUTATIONS.UPDATE_QUEUED_TASKS, []))
</script>

<style lang="scss" scoped>
  @use '~@/scss/vars.scss' as *;
  #admin-queued-tasks-list {
    .top {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: $default-margin * 1.5;
      .top-button {
        display: none;
        @media screen and (max-width: $small-limit) {
          display: block;
        }
      }
      .total {
        font-weight: bold;
      }
    }
    .tasks-help {
      margin: $default-margin 0;
      .info-box {
        width: fit-content;
      }
    }
    table {
      margin: $default-margin * 2 0;
      td {
        text-align: center;
      }
      .id,
      .user {
        text-align: left;
        width: 170px;
      }

      @media screen and (max-width: $small-limit) {
        .id,
        .user {
          width: 45%;
          text-align: center;
        }
        .user {
          display: flex;
          justify-content: center;
        }
      }
      @media screen and (max-width: $x-small-limit) {
        .id,
        .user {
          width: 100%;
        }
      }
    }
    .task-user {
      display: flex;
      align-items: center;
      gap: $default-padding * 0.5;
      ::v-deep(.user-picture) {
        min-width: min-content;
        align-items: flex-start;
        img {
          height: 25px;
          width: 25px;
        }
        .no-picture {
          font-size: 1.5em;
        }
      }
    }

    .no-queued-tasks {
      font-style: italic;
      margin: $default-margin 0 $default-margin * 1.5;
    }

    .buttons {
      display: flex;
      gap: $default-padding;
      flex-wrap: wrap;
      margin-bottom: $default-margin;
    }
  }
</style>
