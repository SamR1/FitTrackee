<template>
  <div class="notifications-filters">
    <div class="box">
      <form class="form">
        <div class="form-all-items">
          <div class="form-items-group">
            <span class="status-title">{{ $t('notifications.STATUS') }}</span>
            <div class="status-radio">
              <label>
                <input
                  type="radio"
                  name="duration"
                  :checked="notificationsStatus === 'unread'"
                  @click="filterOnStatus('unread')"
                />
                {{ $t('notifications.UNREAD') }}
              </label>
              <label>
                <input
                  type="radio"
                  name="all"
                  :checked="notificationsStatus !== 'unread'"
                  @click="filterOnStatus('all')"
                />
                {{ $t('notifications.ALL') }}
              </label>
            </div>
          </div>
          <div class="form-items-group">
            <div class="form-item">
              <label> {{ $t('notifications.TYPES.LABEL') }}</label>
              <select
                name="type"
                :disabled="notificationOptions.length === 0"
                :value="$route.query.type"
                @change="filterOnType"
              >
                <template v-if="notificationOptions.length > 0">
                  <option :value="''">
                    {{ $t('notifications.TYPES.ALL') }}
                  </option>
                  <option disabled>──────</option>
                </template>
                <option
                  v-for="option in notificationOptions"
                  :value="option.value"
                  :key="option.value"
                >
                  {{ option.label }}
                </option>
              </select>
            </div>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { computed, onBeforeMount, onUnmounted, ref, watch } from 'vue'
  import type { ComputedRef, Ref } from 'vue'
  import { useI18n } from 'vue-i18n'
  import { useRoute, useRouter } from 'vue-router'
  import type { LocationQuery, LocationQueryValue } from 'vue-router'

  import useAuthUser from '@/composables/useAuthUser'
  import { NOTIFICATIONS_STORE } from '@/store/constants.ts'
  import type { TNotificationType } from '@/types/notifications'
  import { useStore } from '@/use/useStore.ts'

  const route = useRoute()
  const router = useRouter()
  const store = useStore()
  const { t } = useI18n()

  const { authUserHasModeratorRights, isAuthUserSuspended } = useAuthUser()

  const notificationTypes: ComputedRef<TNotificationType[]> = computed(
    () => store.getters[NOTIFICATIONS_STORE.GETTERS.TYPES]
  )
  const notificationOptions = computed(() => getNotificationsOptions())
  let params: LocationQuery = Object.assign({}, route.query)

  const notificationsStatus: Ref<LocationQueryValue | LocationQueryValue[]> =
    ref(getStatusFromQuery(route.query))

  function getStatusFromQuery(query: LocationQuery) {
    return 'status' in query ? query.status : null
  }
  function filterOnStatus(value: string) {
    notificationsStatus.value = value
    params['status'] = value
    filterNotifications()
  }
  function filterOnType(event: Event) {
    const target = event.target as HTMLInputElement
    if (target.value === '') {
      delete params[target.name]
    } else {
      params[target.name] = target.value
    }
    filterNotifications()
  }
  function filterNotifications() {
    if ('page' in params) {
      params['page'] = '1'
    }
    router.push({ path: '/notifications', query: params })
  }
  function sortOptions(
    a: Record<string, string>,
    b: Record<string, string>
  ): number {
    return a.label > b.label ? 1 : a.label < b.label ? -1 : 0
  }
  function loadNotificationTypes() {
    if (!isAuthUserSuspended.value) {
      store.dispatch(NOTIFICATIONS_STORE.ACTIONS.GET_NOTIFICATION_TYPES, params)
    }
  }
  function getNotificationsOptions() {
    const options: Record<string, string>[] = []
    notificationTypes.value
      .filter(
        (type) =>
          !['report', 'suspension_appeal', 'user_warning_appeal'].includes(
            type
          ) || authUserHasModeratorRights.value
      )
      .map((type) => {
        options.push({
          label: t(`notifications.TYPES.${type}`),
          value: type,
        })
      })
    return options.sort(sortOptions)
  }

  watch(
    () => route.query,
    (newQuery) => {
      params = Object.assign({}, newQuery)
      notificationsStatus.value = getStatusFromQuery(newQuery)
      loadNotificationTypes()
    }
  )

  onBeforeMount(() => loadNotificationTypes())
  onUnmounted(() => {
    store.commit(NOTIFICATIONS_STORE.MUTATIONS.UPDATE_TYPES, [])
  })
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

    .status-title {
      font-weight: bold;
    }
    .status-radio {
      display: flex;
      justify-content: space-around;
      padding-top: 5px;
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
    }

    @media screen and (max-width: $x-small-limit) {
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
