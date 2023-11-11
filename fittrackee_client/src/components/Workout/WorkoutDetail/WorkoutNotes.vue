<template>
  <div id="workout-note">
    <Card>
      <template #title>{{ $t('workouts.NOTES') }}</template>
      <template #content>
        <span
          v-html="
            notes && notes !== ''
              ? linkifyAndClean(notes)
              : $t('workouts.NO_NOTES')
          "
        />
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
  import { toRefs } from 'vue'

  import { linkifyAndClean } from '@/utils/inputs'

  interface Props {
    notes?: string | null
  }
  const props = withDefaults(defineProps<Props>(), {
    notes: () => '',
  })

  const { notes } = toRefs(props)
</script>

<style lang="scss" scoped>
  #workout-note {
    ::v-deep(.card-content) {
      font-style: italic;
      white-space: pre-wrap;
    }
  }
</style>
