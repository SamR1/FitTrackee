<template>
  <div id="workout-note">
    <Card>
      <template #title>{{ $t('workouts.NOTES') }}</template>
      <template #content>
        {{ notes && notes !== '' ? notes : $t('workouts.NO_NOTES') }}</template
      >
    </Card>
  </div>
</template>

<script setup lang="ts">
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
  @import '~@/scss/base.scss';
  #workout-note {
    ::v-deep(.card-content) {
      font-style: italic;
    }
  }
</style>
