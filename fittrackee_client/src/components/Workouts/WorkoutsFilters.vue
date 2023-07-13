<template>
  <div class="workouts-filters">
    <div class="box">
      <form v-on:submit.prevent="onFilter" class="form">
        <div class="form-all-items">
          <div class="form-items-group">
            <div class="form-item">
              <label> {{ $t('workouts.FROM') }}: </label>
              <input
                name="from"
                type="date"
                :value="$route.query.from"
                @change="handleFilterChange"
              />
            </div>
            <div class="form-item">
              <label> {{ $t('workouts.TO') }}: </label>
              <input
                name="to"
                type="date"
                :value="$route.query.to"
                @change="handleFilterChange"
              />
            </div>
          </div>

          <div class="form-items-group">
            <div class="form-item">
              <label> {{ $t('workouts.SPORT', 1) }}:</label>
              <select
                name="sport_id"
                :value="$route.query.sport_id"
                @change="handleFilterChange"
                @keyup.enter="onFilter"
              >
                <option value="" />
                <option
                  v-for="sport in translatedSports.filter((s) =>
                    authUser.sports_list.includes(s.id)
                  )"
                  :value="sport.id"
                  :key="sport.id"
                >
                  {{ sport.translatedLabel }}
                </option>
              </select>
            </div>
            <div class="form-item form-item-title">
              <label> {{ $t('workouts.TITLE', 1) }}:</label>
              <div class="form-inputs-group">
                <input
                  class="title"
                  name="title"
                  :value="$route.query.title"
                  @change="handleFilterChange"
                  placeholder=""
                  type="text"
                  @keyup.enter="onFilter"
                />
              </div>
            </div>
          </div>

          <div class="form-items-group">
            <div class="form-item">
              <label> {{ $t('workouts.DISTANCE') }} ({{ toUnit }}): </label>
              <div class="form-inputs-group">
                <input
                  name="distance_from"
                  type="number"
                  min="0"
                  step="0.1"
                  :value="$route.query.distance_from"
                  @change="handleFilterChange"
                  @keyup.enter="onFilter"
                />
                <span>{{ $t('workouts.TO') }}</span>
                <input
                  name="distance_to"
                  type="number"
                  min="0"
                  step="0.1"
                  :value="$route.query.distance_to"
                  @change="handleFilterChange"
                  @keyup.enter="onFilter"
                />
              </div>
            </div>
          </div>

          <div class="form-items-group">
            <div class="form-item">
              <label> {{ $t('workouts.DURATION') }}: </label>
              <div class="form-inputs-group">
                <input
                  name="duration_from"
                  :value="$route.query.duration_from"
                  @change="handleFilterChange"
                  pattern="^([0-9]*[0-9]):([0-5][0-9])$"
                  placeholder="hh:mm"
                  type="text"
                  @keyup.enter="onFilter"
                />
                <span>{{ $t('workouts.TO') }}</span>
                <input
                  name="duration_to"
                  :value="$route.query.duration_to"
                  @change="handleFilterChange"
                  pattern="^([0-9]*[0-9]):([0-5][0-9])$"
                  placeholder="hh:mm"
                  type="text"
                  @keyup.enter="onFilter"
                />
              </div>
            </div>
          </div>

          <div class="form-items-group">
            <div class="form-item">
              <label> {{ $t('workouts.AVE_SPEED') }} ({{ toUnit }}/h): </label>
              <div class="form-inputs-group">
                <input
                  min="0"
                  name="ave_speed_from"
                  :value="$route.query.ave_speed_from"
                  @change="handleFilterChange"
                  step="0.1"
                  type="number"
                  @keyup.enter="onFilter"
                />
                <span>{{ $t('workouts.TO') }}</span>
                <input
                  min="0"
                  name="ave_speed_to"
                  :value="$route.query.ave_speed_to"
                  @change="handleFilterChange"
                  step="0.1"
                  type="number"
                  @keyup.enter="onFilter"
                />
              </div>
            </div>
          </div>

          <div class="form-items-group">
            <div class="form-item">
              <label> {{ $t('workouts.MAX_SPEED') }} ({{ toUnit }}/h): </label>

              <div class="form-inputs-group">
                <input
                  min="0"
                  name="max_speed_from"
                  :value="$route.query.max_speed_from"
                  @change="handleFilterChange"
                  step="0.1"
                  type="number"
                  @keyup.enter="onFilter"
                />
                <span>{{ $t('workouts.TO') }}</span>
                <input
                  min="0"
                  name="max_speed_to"
                  :value="$route.query.max_speed_to"
                  @change="handleFilterChange"
                  step="0.1"
                  type="number"
                  @keyup.enter="onFilter"
                />
              </div>
            </div>
          </div>
        </div>

        <div class="form-button">
          <button type="submit" class="confirm" @click="onFilter">
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
  import { ComputedRef, computed, toRefs, watch } from 'vue'
  import { useI18n } from 'vue-i18n'
  import { LocationQuery, useRoute, useRouter } from 'vue-router'

  import { ISport } from '@/types/sports'
  import { IAuthUserProfile } from '@/types/user'
  import { translateSports } from '@/utils/sports'
  import { units } from '@/utils/units'

  interface Props {
    authUser: IAuthUserProfile
    sports: ISport[]
  }
  const props = defineProps<Props>()

  const emit = defineEmits(['filter'])

  const { t } = useI18n()
  const route = useRoute()
  const router = useRouter()

  const { authUser } = toRefs(props)

  const toUnit = authUser.value.imperial_units
    ? units['km'].defaultTarget
    : 'km'
  const translatedSports: ComputedRef<ISport[]> = computed(() =>
    translateSports(props.sports, t)
  )
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
    router.push({ path: '/workouts', query: params })
  }
  function onClearFilter() {
    emit('filter')
    router.push({ path: '/workouts', query: {} })
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

  .workouts-filters {
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
