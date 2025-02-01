<template>
  <div class="about-text">
    <div>
      <p class="error-message" v-html="$t('about.FITTRACKEE_DESCRIPTION')" />
      <p>
        <i class="fa fa-book fa-padding" aria-hidden="true"></i>
        <a
          class="documentation-link"
          :href="documentationLink"
          target="_blank"
          rel="noopener noreferrer"
        >
          {{ capitalize($t('common.DOCUMENTATION')) }}
        </a>
      </p>
      <p>
        <i class="fa fa-github fa-padding" aria-hidden="true"></i>
        <a
          href="https://github.com/SamR1/FitTrackee"
          target="_blank"
          rel="noopener noreferrer"
        >
          {{ $t('about.SOURCE_CODE') }}
        </a>
      </p>
      <p>
        <i class="fa fa-balance-scale fa-padding" aria-hidden="true"></i>
        <i18n-t keypath="about.FITTRACKEE_LICENSE">
          <a
            href="https://choosealicense.com/licenses/agpl-3.0/"
            target="_blank"
            rel="noopener noreferrer"
            >AGPLv3</a
          >
        </i18n-t>
      </p>
      <div v-if="appConfig.admin_contact">
        <i class="fa fa-envelope-o fa-padding" aria-hidden="true"></i>
        <a :href="`mailto:${appConfig.admin_contact}`">
          {{ $t('about.CONTACT_ADMIN') }}
        </a>
      </div>
      <div v-if="weatherProvider && weatherProvider.name">
        {{ $t('about.WEATHER_DATA_FROM') }}
        <a :href="weatherProvider.url" target="_blank" rel="nofollow noopener">
          {{ weatherProvider.name }}
        </a>
      </div>
      <template v-if="appConfig.about">
        <p class="about-instance">{{ $t('about.ABOUT_THIS_INSTANCE') }}</p>
        <div v-html="convertToMarkdown(appConfig.about)" />
      </template>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { computed, capitalize } from 'vue'
  import type { ComputedRef } from 'vue'

  import useApp from '@/composables/useApp'
  import { convertToMarkdown } from '@/utils/inputs'

  const { appConfig, appLanguage } = useApp()

  const weatherProvider: ComputedRef<Record<string, string>> = computed(() =>
    get_weather_provider()
  )
  const documentationLink: ComputedRef<string> = computed(() =>
    get_documentation_link()
  )

  function get_weather_provider() {
    const weatherProvider: Record<string, string> = {}
    if (appConfig.value.weatherProvider === 'visualcrossing') {
      weatherProvider['name'] = 'Visual Crossing'
      weatherProvider['url'] = 'https://www.visualcrossing.com'
    }
    return weatherProvider
  }

  function get_documentation_link() {
    let link = 'https://docs.fittrackee.org/'
    if (appLanguage.value === 'fr') {
      link += 'fr/'
    }
    return link
  }
</script>

<style lang="scss" scoped>
  @use '~@/scss/vars.scss' as *;

  .about-text {
    margin-top: 200px;
    margin-right: 100px;
    padding-bottom: 40px;
    @media screen and (max-width: $small-limit) {
      margin-top: 0;
      margin-right: 0;
      padding-bottom: 0;
    }
    .fa-padding {
      padding-right: $default-padding;
    }
    .about-instance {
      font-weight: bold;
      margin-top: $default-margin * 3;
    }
  }
</style>
