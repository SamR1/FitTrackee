<template>
  <div id="workout-note">
    <Card>
      <template #title>{{ $t('workouts.NOTES') }}</template>
      <template #content>
        <span v-html="notes !== '' ? $sanitize(linkifyHtml(notes, { target: '_blank' })) : $t('workouts.NO_NOTES')" />
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import linkifyHtml from 'linkify-html'
import { toRefs, withDefaults } from 'vue'

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
    font-style: italic;
    white-space: pre-wrap;
  }
}
</style>
