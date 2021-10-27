<template>
  <div class="workouts-filters">
    <div class="box">
      <div class="form">
        <div class="form-items-group">
          <div class="form-item">
            <label> {{ $t('workouts.FROM') }}: </label>
            <input name="from" type="date" @change="handleFilterChange" />
          </div>
          <div class="form-item">
            <label> {{ $t('workouts.TO') }}: </label>
            <input name="to" type="date" @change="handleFilterChange" />
          </div>
        </div>

        <div class="form-items-group">
          <div class="form-item">
            <label> {{ $t('workouts.SPORT', 1) }}:</label>
            <select name="sport_id" @change="handleFilterChange">
              <option value="" />
              <option
                v-for="sport in translatedSports.filter((s) =>
                  authUser.sports_list.includes(s.id)
                )"
                :value="sport.id"
                :key="sport.id"
              >
                {{ sport.label }}
              </option>
            </select>
          </div>
        </div>

        <div class="form-items-group">
          <div class="form-item">
            <label> {{ $t('workouts.DISTANCE') }} (km): </label>
            <div class="form-inputs-group">
              <input
                name="distance_from"
                type="number"
                min="0"
                step="1"
                @change="handleFilterChange"
              />
              <span>{{ $t('workouts.TO') }}</span>
              <input
                name="distance_to"
                type="number"
                min="0"
                step="1"
                @change="handleFilterChange"
              />
            </div>
          </div>
        </div>

        <div class="form-items-group">
          <div class="form-item">
            <label> {{ $t('workouts.DURATION') }} (km): </label>
            <div class="form-inputs-group">
              <input
                name="duration_from"
                @change="handleFilterChange"
                pattern="^([0-9]*[0-9]):([0-5][0-9])$"
                placeholder="hh:mm"
                type="text"
              />
              <span>{{ $t('workouts.TO') }}</span>
              <input
                name="duration_to"
                @change="handleFilterChange"
                pattern="^([0-9]*[0-9]):([0-5][0-9])$"
                placeholder="hh:mm"
                type="text"
              />
            </div>
          </div>
        </div>

        <div class="form-items-group">
          <div class="form-item">
            <label> {{ $t('workouts.AVE_SPEED') }} (km): </label>
            <div class="form-inputs-group">
              <input
                min="0"
                name="ave_speed_from"
                @change="handleFilterChange"
                step="1"
                type="number"
              />
              <span>{{ $t('workouts.TO') }}</span>
              <input
                min="0"
                name="ave_speed_to"
                @change="handleFilterChange"
                step="1"
                type="number"
              />
            </div>
          </div>
        </div>

        <div class="form-items-group">
          <div class="form-item">
            <label> {{ $t('workouts.MAX_SPEED') }} (km): </label>

            <div class="form-inputs-group">
              <input
                min="0"
                name="max_speed_from"
                @change="handleFilterChange"
                step="1"
                type="number"
              />
              <span>{{ $t('workouts.TO') }}</span>
              <input
                min="0"
                name="max_speed_to"
                @change="handleFilterChange"
                step="1"
                type="number"
              />
            </div>
          </div>
        </div>
      </div>

      <div class="form-button">
        <button class="confirm" @click="onFilter">
          {{ $t('buttons.FILTER') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
  import { computed, ComputedRef, defineComponent, PropType } from 'vue'
  import { useI18n } from 'vue-i18n'

  import { ISport } from '@/types/sports'
  import { IAuthUserProfile } from '@/types/user'
  import { translateSports } from '@/utils/sports'

  export default defineComponent({
    name: 'WorkoutsFilters',
    props: {
      authUser: {
        type: Object as PropType<IAuthUserProfile>,
        required: true,
      },
      sports: {
        type: Object as PropType<ISport[]>,
        required: true,
      },
    },
    emits: ['filter', 'filtersUpdate'],
    setup(props, { emit }) {
      const { t } = useI18n()
      const translatedSports: ComputedRef<ISport[]> = computed(() =>
        translateSports(props.sports, t)
      )
      const params: Record<string, string> = {}

      function handleFilterChange(event: Event & { target: HTMLInputElement }) {
        if (event.target.value === '') {
          delete params[event.target.name]
        } else {
          params[event.target.name] = event.target.value
        }
      }
      function onFilter() {
        emit('filter', { ...params })
      }

      return { translatedSports, onFilter, handleFilterChange }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base.scss';

  .workouts-filters {
    .form {
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
            height: 36px;
            padding: 0 $default-padding * 0.5;
          }
        }
      }
    }

    .form-button {
      display: flex;
      justify-content: center;

      button {
        margin: $default-padding * 2 $default-padding * 0.5 $default-padding
          $default-padding * 0.5;
        width: 100%;
      }
    }

    @media screen and (max-width: $medium-limit) {
      .form {
        flex-direction: row;
        padding-top: $default-padding * 0.5;

        .form-items-group {
          padding: 0 $default-padding * 0.5;
          height: 100%;

          .form-item {
            label {
              font-size: 0.9em;
            }

            .form-inputs-group {
              flex-direction: column;
              justify-content: normal;
              padding: 0;

              input {
                width: 75%;
              }
            }
          }
        }
      }

      .form-button {
        button {
          margin: $default-padding $default-padding * 0.5;
          width: 100%;
        }
      }
    }
    @media screen and (max-width: $small-limit) {
      .form {
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
      .form-button {
        button {
          margin: $default-padding $default-padding * 0.5;
        }
      }
    }
  }
</style>
