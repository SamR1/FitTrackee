<template>
  <div id="workout-note">
    <Card>
      <template #title>{{ capitalize($t('workouts.NOTES')) }}</template>
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
  import { capitalize, toRefs, withDefaults } from 'vue'

  import { linkifyAndClean } from '@/utils/inputs'

  interface Props {
    notes?: string | null
  }
  const props = withDefaults(defineProps<Props>(), {
    notes: () => null,
  })

  const { notes } = toRefs(props)
</script>

<style lang="scss" scoped>
  #workout-note {
    ::v-deep(.card-content) {
      white-space: pre-wrap;
    }
  }
</style>
