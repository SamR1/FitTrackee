<template>
  <div class="about-text">
    <div>
      <p class="error-message" v-html="$t('about.FITTRACKEE_DESCRIPTION')" />
      <p>
        <i class="fa fa-book fa-padding" aria-hidden="true"></i>
        <a
          href="https://samr1.github.io/FitTrackee/"
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
          >
            AGPLv3
          </a>
        </i18n-t>
      </p>
      <div v-if="appConfig.admin_contact">
        <i class="fa fa-envelope-o fa-padding" aria-hidden="true"></i>
        <a :href="`mailto:${appConfig.admin_contact}`">
          {{ $t('about.CONTACT_ADMIN') }}
        </a>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { ComputedRef, computed, capitalize } from 'vue'

  import { ROOT_STORE } from '@/store/constants'
  import { TAppConfig } from '@/types/application'
  import { useStore } from '@/use/useStore'

  const store = useStore()
  const appConfig: ComputedRef<TAppConfig> = computed(
    () => store.getters[ROOT_STORE.GETTERS.APP_CONFIG]
  )
</script>

<style lang="scss" scoped>
  @import '~@/scss/base.scss';

  .about-text {
    margin-top: 200px;
    @media screen and (max-width: $small-limit) {
      margin-top: 0;
    }
    .fa-padding {
      padding-right: $default-padding;
    }
  }
</style>
