<template>
  <div id="password-action-done" class="center-card with-margin">
    <EmailSent v-if="action === 'request-sent'" />
    <Password v-else />
    <div class="password-message">
      <span v-if="action === 'request-sent'"
        >{{ $t('user.PASSWORD_SENT_EMAIL_TEXT') }}
      </span>
      <i18n-t v-else keypath="user.PASSWORD_UPDATED">
        <router-link to="/login">
          {{ $t('common.HERE') }}
        </router-link>
      </i18n-t>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { toRefs } from 'vue'

  import EmailSent from '@/components/Common/Images/EmailSent.vue'
  import Password from '@/components/Common/Images/Password.vue'

  interface Props {
    action: string
  }
  const props = defineProps<Props>()

  const { action } = toRefs(props)
</script>

<style scoped lang="scss">
  @import '~@/scss/vars.scss';

  #password-action-done {
    display: flex;
    flex-direction: column;
    align-items: center;

    svg {
      stroke: none;
      fill-rule: nonzero;
      fill: var(--app-color);
      filter: var(--svg-filter);
      width: 100px;
    }

    .password-message {
      font-size: 1.1em;
      text-align: center;

      @media screen and (max-width: $medium-limit) {
        font-size: 1em;
      }
    }
  }
</style>
