<template>
  <div class="no-workouts box">
    <div>
      {{ t('workouts.NO_WORKOUTS') }}
      <router-link to="/workouts/add">
        {{ t('workouts.UPLOAD_FIRST_WORKOUT') }}
      </router-link>
    </div>
  </div>
</template>

<script lang="ts">
  import { defineComponent } from 'vue'
  import { useI18n } from 'vue-i18n'

  export default defineComponent({
    name: 'NoWorkouts',
    setup() {
      const { t } = useI18n()
      return { t }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base.scss';
  .no-workouts {
    display: flex;
    justify-content: center;
  }
</style>
