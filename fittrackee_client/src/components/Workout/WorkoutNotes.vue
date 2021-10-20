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

<script lang="ts">
  import { defineComponent } from 'vue'

  import Card from '@/components/Common/Card.vue'

  export default defineComponent({
    name: 'WorkoutNotes',
    components: {
      Card,
    },
    props: {
      notes: {
        type: String,
        required: false,
      },
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base.scss';
  #workout-note {
    ::v-deep(.card-content) {
      font-style: italic;
    }
  }
</style>
