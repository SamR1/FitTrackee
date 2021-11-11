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

<style lang="scss" scoped>
  @import '~@/scss/base.scss';
  .no-workouts {
    display: flex;
    justify-content: center;
  }
</style>
