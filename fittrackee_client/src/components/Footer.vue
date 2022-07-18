<template>
  <div id="footer">
    <div class="footer-items">
      <div class="footer-item">
        <strong>FitTrackee</strong>
        v{{ version }}
      </div>
      <div class="footer-item bullet">•</div>
      <div class="footer-item">
        <router-link to="/about">
          {{ $t('common.ABOUT') }}
        </router-link>
      </div>
      <div class="footer-item bullet" v-if="adminContact">•</div>
      <div class="footer-item" v-if="adminContact">
        <a :href="`mailto:${adminContact}`">{{ $t('common.CONTACT') }}</a>
      </div>
      <div class="footer-item bullet">•</div>
      <div class="footer-item">
        <a
          href="https://samr1.github.io/FitTrackee/"
          target="_blank"
          rel="noopener noreferrer"
        >
          {{ $t('common.DOCUMENTATION') }}
        </a>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { toRefs } from 'vue'

  interface Props {
    version: string
    adminContact?: string
  }
  const props = defineProps<Props>()

  const { adminContact, version } = toRefs(props)
</script>

<style scoped lang="scss">
  @import '~@/scss/vars.scss';

  #footer {
    display: flex;

    bottom: 0;
    position: fixed;
    width: 100%;

    background: var(--footer-background-color);
    color: var(--footer-color);
    font-size: 0.9em;

    a {
      text-decoration: none;
    }

    .footer-items {
      display: flex;
      align-content: center;
      justify-content: center;

      width: 100%;

      .footer-item {
        padding: 10px 10px;

        border-top: solid 1px var(--footer-border-color);
        text-align: center;
      }
    }

    @media screen and (max-width: $x-small-limit) {
      .footer-items {
        font-size: 0.85em;

        .footer-item {
          padding: 5px 5px;
        }

        .bullet {
          padding: 5px 0;
        }
      }
    }
  }
</style>
