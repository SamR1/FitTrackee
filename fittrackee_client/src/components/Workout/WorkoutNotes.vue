<template>
  <div id="workout-note">
    <Card>
      <template #title>{{ t('workouts.NOTES') }}</template>
      <template #content>
        {{ notes && notes !== '' ? notes : t('workouts.NO_NOTES') }}</template
      >
    </Card>
  </div>
</template>

<script lang="ts">
  import { defineComponent } from 'vue'
  import { useI18n } from 'vue-i18n'

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
    setup() {
      const { t } = useI18n()
      return { t }
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
