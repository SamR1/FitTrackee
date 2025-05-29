<template>
  <div id="admin-tasks" class="admin-card">
    <Card>
      <template #title>{{ $t('admin.USERS_QUEUED_TASKS.LABEL') }}</template>
      <template #content>
        <div class="responsive-table queues-table">
          <table>
            <thead>
              <tr>
                <th class="task-type">
                  {{ $t('admin.USERS_QUEUED_TASKS.TASK_TYPES.LABEL') }}
                </th>
                <th>
                  {{ $t('admin.USERS_QUEUED_TASKS.LABEL') }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="taskType in taskTypes" :key="taskType">
                <td class="task-type">
                  <span class="cell-heading">
                    {{ $t('admin.USERS_QUEUED_TASKS.TASK_TYPES.LABEL') }}
                  </span>
                  <router-link :to="`/admin/queued-tasks/${taskType}`">
                    {{ $t(`admin.USERS_QUEUED_TASKS.TASK_TYPES.${taskType}`) }}
                  </router-link>
                </td>
                <td>
                  <span class="cell-heading">
                    {{ $t('admin.USERS_QUEUED_TASKS.LABEL') }}
                  </span>
                  {{ counts[taskType] }}
                </td>
              </tr>
            </tbody>
          </table>
          <ErrorMessage :message="errorMessages" v-if="errorMessages" />
          <button @click.prevent="$router.push('/admin')">
            {{ $t('admin.BACK_TO_ADMIN') }}
          </button>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
  import { onBeforeMount, computed, onUnmounted } from 'vue'
  import type { ComputedRef } from 'vue'

  import useApp from '@/composables/useApp'
  import { USERS_STORE } from '@/store/constants'
  import type { TQueuedTasksCounts, TTaskType } from '@/types/application.ts'
  import { useStore } from '@/use/useStore'

  const store = useStore()

  const { errorMessages } = useApp()

  const taskTypes: TTaskType[] = ['user_data_export', 'workouts_archive_upload']
  const counts: ComputedRef<TQueuedTasksCounts> = computed(
    () => store.getters[USERS_STORE.GETTERS.USERS_QUEUED_TASKS_COUNTS]
  )

  function loadQueues() {
    store.dispatch(USERS_STORE.ACTIONS.GET_USERS_QUEUED_TASKS_COUNT)
  }

  onBeforeMount(() => loadQueues())
  onUnmounted(() =>
    store.commit(USERS_STORE.MUTATIONS.UPDATE_USERS_QUEUED_TASKS_COUNTS, {
      user_data_export: 0,
      workouts_archive_upload: 0,
    })
  )
</script>

<style lang="scss" scoped>
  @use '~@/scss/vars.scss' as *;
  #admin-tasks {
    .queues-table {
      table {
        width: 60%;
        margin-bottom: $default-margin * 2;
      }
      td {
        text-align: center;
      }
      .task-type {
        text-align: left;
      }

      @media screen and (max-width: $medium-limit) {
        table {
          width: 100%;
        }
      }
      @media screen and (max-width: $small-limit) {
        .task-type {
          text-align: center;
        }
      }
    }
  }
</style>
