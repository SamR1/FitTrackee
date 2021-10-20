<template>
  <div class="no-workouts box">
    <div>
      {{ $t('workouts.NO_WORKOUTS') }}
      <router-link to="/workouts/add">
        {{ $t('workouts.UPLOAD_FIRST_WORKOUT') }}
      </router-link>
    </div>
  </div>
</template>

<script lang="ts">
  import { defineComponent } from 'vue'

  export default defineComponent({
    name: 'NoWorkouts',
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base.scss';
  .no-workouts {
    display: flex;
    justify-content: center;
  }
</style>
