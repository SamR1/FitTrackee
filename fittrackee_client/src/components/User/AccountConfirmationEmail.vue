<template>
  <div id="account-confirmation-email" class="center-card with-margin">
    <div class="email-sent" v-if="action === 'email-sent'">
      <EmailSent />
      <div class="email-sent-message">
        {{ $t('user.ACCOUNT_CONFIRMATION_SENT') }}
      </div>
    </div>
    <div v-else>
      <Card>
        <template #title>{{ $t('user.RESENT_ACCOUNT_CONFIRMATION') }}</template>
        <template #content>
          <UserAuthForm :action="action" />
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { toRefs } from 'vue'

  import EmailSent from '@/components/Common/Images/EmailSent.vue'
  import UserAuthForm from '@/components/User/UserAuthForm.vue'

  interface Props {
    action: string
  }
  const props = defineProps<Props>()

  const { action } = toRefs(props)
</script>

<style scoped lang="scss">
  @import '~@/scss/vars.scss';

  #account-confirmation-email {
    display: flex;
    flex-direction: column;

    .email-sent {
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
      .email-sent-message {
        font-size: 1.1em;
        text-align: center;

        @media screen and (max-width: $medium-limit) {
          font-size: 1em;
        }
      }
    }
    ::v-deep(.card) {
      .card-content {
        #user-auth-form {
          margin-top: 0;
          #user-form {
            width: 100%;
          }
        }
      }
    }
  }
</style>
