<template>
  <div class="error-message" :class="{ 'no-margin': noMargin }">
    <ul v-if="Array.isArray(message)">
      <li v-for="(subMessage, index) in message" :key="index">
        {{ $t(subMessage) }}
      </li>
    </ul>
    <ul
      v-else-if="typeof message === 'object' && 'erroredWorkouts' in message"
      class="files-error"
    >
      {{
        $t('error.ERRORS_ENCOUNTERED')
      }}
      <li>
        {{ $t('workouts.CREATED_WORKOUTS', message.createdWorkouts) }}:
        {{ message.createdWorkouts }}
      </li>

      <li>
        {{
          $t(
            'user.PROFILE.ARCHIVE_UPLOADS.ERRORED_FILES',
            Object.keys(message.erroredWorkouts).length
          )
        }}:
        <ul class="errored-files">
          <li
            v-for="[key, value] of Object.entries(message.erroredWorkouts)"
            :key="key"
          >
            - {{ key }}: {{ $t(`api.ERROR.${value}`) }}
          </li>
        </ul>
      </li>
    </ul>
    <div v-else-if="typeof message === 'string'">
      {{ $t(message).replace('api.ERROR.', '') }}
    </div>
    <div v-else-if="'equipmentId' in message">
      {{
        $t(`equipments.ERRORS.${message.status}`, {
          equipmentId: message.equipmentId,
          equipmentLabel: message.equipmentLabel,
        })
      }}
    </div>
  </div>
</template>

<script setup lang="ts">
  import { toRefs } from 'vue'

  import type { IEquipmentError } from '@/types/equipments'
  import type { IWorkoutFilesError } from '@/types/workouts'

  interface Props {
    message: string | string[] | IEquipmentError | IWorkoutFilesError
    noMargin?: boolean
  }
  const props = withDefaults(defineProps<Props>(), { noMargin: false })
  const { message } = toRefs(props)
</script>

<style scoped lang="scss">
  @use '~@/scss/vars.scss' as *;
  .error-message {
    background: var(--error-background-color);
    color: var(--error-color);

    border-radius: 4px;

    margin: $default-margin;
    padding: $default-padding;

    &.no-margin {
      margin: $default-margin 0;
    }

    .files-error,
    .errored-files {
      list-style-type: none;
    }
    .files-error {
      font-weight: bold;
      margin: 0;
      padding: $default-padding;
      li {
        font-weight: normal;
      }
    }
    .errored-files {
      max-height: 190px;
      overflow-y: auto;
    }
  }
</style>
