<template>
  <div class="policy-message">
    <span>
      <i18n-t
        :keypath="`user.${isPrivacyUpdated ? 'LAST_' : ''}PRIVACY_POLICY_TO_VALIDATE`"
      >
        <router-link to="/profile/edit/privacy-policy" class="policy-link">
          {{ $t('user.REVIEW') }}
        </router-link>
      </i18n-t>
    </span>
  </div>
</template>

<script lang="ts" setup>
  import { toRefs } from 'vue'

  interface Props {
    isPrivacyUpdated: boolean
  }
  const props = defineProps<Props>()

  const { isPrivacyUpdated } = toRefs(props)
</script>

<style scoped lang="scss">
  @use '~@/scss/vars.scss' as *;

  .policy-message {
    background: var(--alert-background-color);
    color: var(--alert-color);
    border-radius: $border-radius;
    padding: $default-padding $default-padding * 2;

    .policy-link {
      color: var(--policy-link-color);
      text-decoration: underline;
    }
  }
</style>
