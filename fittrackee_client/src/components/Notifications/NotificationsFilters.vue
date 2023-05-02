<template>
  <div class="notifications-filters">
    <div class="box">
      <form @submit.prevent="onFilter" class="form">
        <div class="form-all-items">
          <div class="form-items-group">
            <div class="form-item">
              <label> {{ $t('notifications.TYPES.LABEL') }}:</label>
              <select
                name="type"
                :value="$route.query.type"
                @change="handleFilterChange"
              >
                <option value="" />
                <option
                  v-for="type in notificationTypes"
                  :value="type"
                  :key="type"
                >
                  {{ $t(`notifications.TYPES.${type}`) }}
                </option>
              </select>
            </div>
          </div>
        </div>
        <div class="form-button">
          <button type="submit" class="confirm">
            {{ $t('buttons.FILTER') }}
          </button>
          <button class="confirm" @click="onClearFilter">
            {{ $t('buttons.CLEAR_FILTER') }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { watch } from 'vue'
  import { LocationQuery, useRoute, useRouter } from 'vue-router'

  import { TNotificationType } from '@/types/notifications'

  const emit = defineEmits(['filter'])

  const route = useRoute()
  const router = useRouter()

  const notificationTypes: TNotificationType[] = [
    'follow',
    'follow_request',
    'comment_like',
    'comment_reply',
    'mention',
    'workout_comment',
    'workout_like',
  ]
  let params: LocationQuery = Object.assign({}, route.query)

  function handleFilterChange(event: Event & { target: HTMLInputElement }) {
    if (event.target.value === '') {
      delete params[event.target.name]
    } else {
      params[event.target.name] = event.target.value
    }
  }
  function onFilter() {
    emit('filter')
    if ('page' in params) {
      params['page'] = '1'
    }
    router.push({ path: '/notifications', query: params })
  }
  function onClearFilter() {
    emit('filter')
    router.push({ path: '/notifications', query: {} })
  }

  watch(
    () => route.query,
    (newQuery) => {
      params = Object.assign({}, newQuery)
    }
  )
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';

  .notifications-filters {
    .form {
      .form-all-items {
        display: flex;
        flex-direction: column;
        padding-top: 0;

        .form-items-group {
          display: flex;
          flex-direction: column;
          padding: $default-padding * 0.5;

          .form-item {
            display: flex;
            flex-direction: column;

            .form-inputs-group {
              display: flex;
              flex-direction: row;
              justify-content: space-around;
              align-items: center;

              input {
                width: 34%;
              }
              span {
                padding: $default-padding * 0.5;
              }
            }

            input {
              height: 16px;
            }

            select {
              height: 38px;
              padding: 0 $default-padding * 0.5;
            }
          }
          .form-item-title {
            padding-top: $default-padding;
            input.title {
              width: 100%;
            }
          }
        }
      }
    }

    .form-button {
      display: flex;
      justify-content: center;
      flex-wrap: wrap;
      margin: $default-margin * 0.5;

      button {
        margin-top: $default-margin;
        width: 100%;
      }
    }

    @media screen and (max-width: $medium-limit) {
      .form {
        .form-all-items {
          flex-direction: row;
          padding-top: $default-padding * 0.5;

          .form-items-group {
            padding: 0 $default-padding * 0.5;
            height: 100%;

            .form-item {
              label,
              span {
                font-size: 0.9em;
              }

              .form-inputs-group {
                flex-direction: column;
                justify-content: normal;
                padding: 0;

                input {
                  width: 85%;
                }
                span {
                  padding: 0;
                }
              }
            }

            .form-item-title {
              padding-top: 0;
            }
          }
        }
      }

      .form-button {
        flex-wrap: initial;
        button {
          margin: $default-padding $default-padding * 0.5;
          width: 100%;
        }
      }
    }
    @media screen and (max-width: $small-limit) {
      .form {
        .form-all-items {
          flex-direction: column;
          padding-top: 0;

          .form-items-group {
            padding: $default-padding * 0.5;

            .form-item {
              label {
                font-size: 1em;
              }

              .form-inputs-group {
                flex-direction: row;
                justify-content: space-around;
                align-items: center;

                input {
                  width: 50%;
                }

                span {
                  padding: $default-padding * 0.5;
                }
              }
            }
          }
        }
      }
      .form-button {
        flex-wrap: initial;
        button {
          margin: $default-padding $default-padding * 0.5;
        }
      }
    }

    @media screen and (max-width: $x-small-limit) {
      .form-button {
        flex-wrap: wrap;
      }
      .form {
        .form-all-items {
          .form-items-group {
            .form-item-title {
              padding-top: $default-padding;

              input.title {
                width: 100%;
              }
            }
          }
        }
      }
    }
  }
</style>
