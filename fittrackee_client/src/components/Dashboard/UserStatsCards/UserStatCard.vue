<template>
  <div class="user-stat-card">
    <Card :without-title="true">
      <template #content>
        <div class="stat-content">
          <div class="stat-icon">
            <i class="fa" :class="`fa-${icon}`" />
          </div>
          <div class="stat-details">
            <div class="stat-huge">{{ value }}</div>
            <div class="stat">{{ text }}</div>
          </div>
        </div>
      </template>
    </Card>
  </div>
</template>

<script lang="ts">
  import { defineComponent } from 'vue'

  import Card from '@/components/Common/Card.vue'
  export default defineComponent({
    name: 'UserStatCard',
    components: {
      Card,
    },
    props: {
      icon: {
        type: String,
        required: true,
      },
      value: {
        type: [String, Number],
        required: true,
      },
      text: {
        type: String,
        required: true,
      },
    },
  })
</script>

<style lang="scss">
  @import '~@/scss/base';
  .user-stat-card {
    flex: 1;
    max-width: 25%;
    @media screen and (max-width: $small-limit) {
      flex: 1 0 50%;
      max-width: 49%;
    }

    .stat-content {
      display: flex;
      flex-direction: row;
      justify-content: space-between;

      .stat-icon {
        width: 30%;
        text-align: center;
        vertical-align: center;
        @media screen and (max-width: $medium-limit) {
          width: 50%;
          text-align: left;
        }

        .fa {
          font-size: 3em;
          @media screen and (max-width: $medium-limit) {
            font-size: 2em;
          }
          @media screen and (max-width: $x-small-limit) {
            font-size: 1.5em;
          }
        }
      }
      .stat-details {
        width: 70%;
        text-align: right;
        @media screen and (max-width: $medium-limit) {
          width: 100%;
        }

        .stat-huge {
          font-size: 1.7em;
          font-weight: bold;
          @media screen and (max-width: $medium-limit) {
            font-size: 1.3em;
          }
          @media screen and (max-width: $x-small-limit) {
            font-size: 1em;
          }
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
    }
  }
</style>
