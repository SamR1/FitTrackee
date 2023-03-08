<template>
  <div class="privacy-policy-message">
    <span>
      <i18n-t keypath="user.LAST_PRIVACY_POLICY_TO_VALIDATE">
        <router-link to="/profile/edit/privacy-policy">
          {{ $t('user.REVIEW') }}
        </router-link>
      </i18n-t>
    </span>
  </div>
</template>

<script setup lang="ts">

</script>

<style scoped lang="scss">
  @import '~@/scss/vars.scss';
  .privacy-policy-message {
    background: var(--alert-background-color);
    color: var(--alert-color);
    border-radius: $border-radius;
    padding: $default-padding $default-padding*2;
  }
</style>
