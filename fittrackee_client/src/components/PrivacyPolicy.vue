<template>
  <div class="privacy-policy-text">
    <h1>
      {{ capitalize($t('privacy_policy.TITLE')) }}
    </h1>
    <p class="last-update">
      {{ $t('privacy_policy.LAST_UPDATE') }}:
      <time>{{ privatePolicyDate }}</time>
    </p>
    <template v-if="appConfig.privacy_policy">
      <div v-html="snarkdown(linkifyAndClean(appConfig.privacy_policy))" />
    </template>
    <template v-else>
      <template v-for="paragraph in paragraphs" :key="paragraph">
        <h2>
          {{ $t(`privacy_policy.CONTENT.${paragraph}.TITLE`) }}
        </h2>
        <p
          v-html="snarkdown($t(`privacy_policy.CONTENT.${paragraph}.CONTENT`))"
        />
      </template>
    </template>
  </div>
</template>

<script lang="ts" setup>
  import snarkdown from 'snarkdown'
  import { capitalize, computed } from 'vue'
  import type { ComputedRef } from 'vue'

  import useApp from '@/composables/useApp'
  import useAuthUser from '@/composables/useAuthUser'
  import { formatDate } from '@/utils/dates'
  import { linkifyAndClean } from '@/utils/inputs'

  const { appConfig } = useApp()
  const { dateFormat, timezone } = useAuthUser()

  const fittrackeePrivatePolicyDate = 'Sun, 26 Feb 2023 17:00:00 GMT'
  const paragraphs = [
    'DATA_COLLECTED',
    'INFORMATION_USAGE',
    'INFORMATION_PROTECTION',
    'INFORMATION_DISCLOSURE',
    'SITE_USAGE_BY_CHILDREN',
    'YOUR_CONSENT',
    'ACCOUNT_DELETION',
    'CHANGES_TO_OUR_PRIVACY_POLICY',
  ]

  const privatePolicyDate: ComputedRef<string> = computed(() => getPolicyDate())

  function getPolicyDate() {
    return formatDate(
      appConfig.value.privacy_policy && appConfig.value.privacy_policy_date
        ? `${appConfig.value.privacy_policy_date}`
        : fittrackeePrivatePolicyDate,
      timezone.value,
      dateFormat.value,
      false
    )
  }
</script>

<style lang="scss" scoped>
  @import '~@/scss/base.scss';

  .privacy-policy-text {
    margin: 10px 50px 20px;
    padding: $default-padding;
    width: 100%;

    @media screen and (max-width: $small-limit) {
      margin: 0;
    }
  }
</style>
