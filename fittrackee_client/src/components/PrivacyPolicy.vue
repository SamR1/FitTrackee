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
      <div v-html="convertToMarkdown(appConfig.privacy_policy)" />
    </template>
    <template v-else>
      <template v-for="paragraph in paragraphs" :key="paragraph">
        <h2>
          {{ $t(`privacy_policy.CONTENT.${paragraph}.TITLE`) }}
        </h2>
        <p
          v-html="
            convertToMarkdown($t(`privacy_policy.CONTENT.${paragraph}.CONTENT`))
          "
        />
      </template>
    </template>
  </div>
</template>

<script lang="ts" setup>
  import { capitalize, computed } from 'vue'
  import type { ComputedRef } from 'vue'

  import useApp from '@/composables/useApp'
  import useAuthUser from '@/composables/useAuthUser'
  import { formatDate } from '@/utils/dates'
  import { convertToMarkdown } from '@/utils/inputs'

  const { appConfig } = useApp()
  const { dateFormat, timezone } = useAuthUser()

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
      appConfig.value.privacy_policy_date,
      timezone.value,
      dateFormat.value,
      false
    )
  }
</script>

<style lang="scss" scoped>
  @use '~@/scss/vars.scss' as *;
  @use '~@/scss/base.scss' as *;

  .privacy-policy-text {
    margin: 10px 50px 20px;
    padding: $default-padding;
    width: 100%;

    @media screen and (max-width: $small-limit) {
      margin: 0;
    }
  }
</style>
