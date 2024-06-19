<template>
  <div class="sport-stat-card">
    <div class="stat-content">
      <div class="stat-icon">
        <i class="fa" :class="`fa-${icon}`" />
      </div>
      <div class="stat-details">
        <div class="stat-label">{{ label }}</div>
        <div class="stat-values">
          <i class="fa fa-refresh fa-spin fa-fw" v-if="loading"></i>
          <span class="stat-huge" v-else>
            {{ totalValue ? totalValue : '' }}
          </span>
          <span class="stat" v-if="text">{{ text }}</span>
        </div>
        <div
          class="stat-average"
          v-if="!['calendar', 'tachometer'].includes(icon)"
        >
          <div v-if="loading"><i class="fa fa-refresh fa-spin fa-fw"></i></div>
          <slot v-else name="average"></slot>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { toRefs } from 'vue'

  interface Props {
    icon: string
    text?: string
    totalValue: string | number
    label: string
    loading: boolean
  }
  const props = withDefaults(defineProps<Props>(), {
    text: '',
  })
  const { icon, loading, text, totalValue } = toRefs(props)
</script>

<style lang="scss">
  @import '~@/scss/vars.scss';
  .sport-stat-card {
    flex: 1 0 33%;
    @media screen and (max-width: $small-limit) {
      flex: 1 0 50%;
    }
    @media screen and (max-width: $x-small-limit) {
      flex: 1 0 100%;
    }

    .stat-content {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: space-between;
      padding: $default-padding $default-padding * 2;

      .stat-icon {
        .fa {
          font-size: 3em;
          @media screen and (max-width: $medium-limit) {
            font-size: 2em;
          }
        }
      }
      .stat-details {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: space-around;
        @media screen and (max-width: $medium-limit) {
          width: 100%;
        }

        .stat-label {
          padding: $default-padding 0 $default-padding * 0.5;
          text-transform: capitalize;
        }

        .stat-values {
          display: flex;
          gap: $default-padding * 0.5;
          align-items: baseline;
          min-height: 37px;
          .stat-huge {
            font-size: 1.7em;
            font-weight: bold;
            @media screen and (max-width: $medium-limit) {
              font-size: 1.3em;
            }
            @media screen and (max-width: $x-small-limit) {
              font-size: 1.2em;
            }
          }
          .fa-refresh {
            font-size: 1.4em;
          }
          .stat {
            font-size: 1em;
            @media screen and (max-width: $medium-limit) {
              font-size: 0.9em;
            }
            @media screen and (max-width: $x-small-limit) {
              font-size: 0.8em;
            }
          }
        }

        .stat-average {
          display: flex;
          gap: $default-padding * 0.5;
          font-style: italic;
          font-size: 0.9em;
          margin: $default-margin * 0.5 0;
          text-transform: lowercase;
          min-height: 25px;
        }
      }
    }
  }
</style>
