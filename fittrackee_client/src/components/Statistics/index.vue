<template>
  <div id="user-statistics">
    <Card v-if="translatedSports">
      <template #title>{{ $t('statistics.STATISTICS') }}</template>
      <template #content>
        <div class="chart-filters">
          <div class="chart-arrow">
            <i
              class="fa fa-chevron-left"
              aria-hidden="true"
              @click="handleOnClickArrows(true)"
            />
          </div>
          <div class="time-frames">
            <div class="time-frames-checkboxes">
              <div v-for="frame in timeFrames" class="time-frame" :key="frame">
                <label>
                  <input
                    type="radio"
                    :id="frame"
                    :name="frame"
                    :checked="selectedTimeFrame === frame"
                    @input="updateTimeFrame(frame)"
                  />
                  <span>{{ t(`statistics.TIME_FRAMES.${frame}`) }}</span>
                </label>
              </div>
            </div>
          </div>
          <div class="chart-arrow">
            <i
              class="fa fa-chevron-right"
              aria-hidden="true"
              @click="handleOnClickArrows(false)"
            />
          </div>
        </div>
        <StatChart
          :sports="sports"
          :user="user"
          :chartParams="chartParams"
          :displayed-sport-ids="selectedSportIds"
          :fullStats="true"
        />
        <div class="sports">
          <label
            v-for="sport in translatedSports"
            type="checkbox"
            :key="sport.id"
            :style="{ color: sportColors[sport.label] }"
          >
            <input
              type="checkbox"
              :id="sport.id"
              :name="sport.label"
              :checked="selectedSportIds.includes(sport.id)"
              @input="updateSelectedSportIds(sport.id)"
            />
            <SportImage :sport-label="sport.label" />
            {{ sport.translatedLabel }}
          </label>
        </div>
      </template>
    </Card>
  </div>
</template>

<script lang="ts">
  import {
    addMonths,
    addWeeks,
    addYears,
    endOfMonth,
    endOfWeek,
    endOfYear,
    startOfMonth,
    startOfWeek,
    startOfYear,
    subMonths,
    subWeeks,
    subYears,
  } from 'date-fns'
  import {
    ComputedRef,
    PropType,
    Ref,
    computed,
    defineComponent,
    ref,
    watch,
  } from 'vue'
  import { useI18n } from 'vue-i18n'

  import Card from '@/components/Common/Card.vue'
  import SportImage from '@/components/Common/SportImage/index.vue'
  import StatChart from '@/components/Common/StatsChart/index.vue'
  import { ISport, ITranslatedSport } from '@/types/sports'
  import { IStatisticsDateParams } from '@/types/statistics'
  import { IAuthUserProfile } from '@/types/user'
  import { translateSports, sportColors } from '@/utils/sports'

  export default defineComponent({
    name: 'UserMonthStats',
    components: {
      Card,
      SportImage,
      StatChart,
    },
    props: {
      sports: {
        type: Object as PropType<ISport[]>,
        required: true,
      },
      user: {
        type: Object as PropType<IAuthUserProfile>,
        required: true,
      },
    },
    setup(props) {
      const { t } = useI18n()
      let selectedTimeFrame = ref('month')
      const timeFrames = ['week', 'month', 'year']
      const chartParams: Ref<IStatisticsDateParams> = ref(
        getChartParams(selectedTimeFrame.value)
      )
      const translatedSports: ComputedRef<ITranslatedSport[]> = computed(() =>
        translateSports(props.sports, t)
      )
      const selectedSportIds: Ref<number[]> = ref(getSports(props.sports))

      function updateTimeFrame(timeFrame: string) {
        selectedTimeFrame.value = timeFrame
        chartParams.value = getChartParams(selectedTimeFrame.value)
      }
      function getChartParams(timeFrame: string): IStatisticsDateParams {
        const date = new Date()
        const start =
          timeFrame === 'year'
            ? startOfYear(subYears(date, 9))
            : selectedTimeFrame.value === 'week'
            ? startOfMonth(subMonths(date, 2))
            : startOfMonth(subMonths(date, 11))
        const end =
          timeFrame === 'year'
            ? endOfYear(date)
            : timeFrame === 'week'
            ? endOfWeek(date)
            : endOfMonth(date)
        return {
          duration: timeFrame,
          end,
          start,
        }
      }
      function handleOnClickArrows(backward: boolean) {
        chartParams.value = {
          duration: selectedTimeFrame.value,
          end:
            selectedTimeFrame.value === 'year'
              ? startOfYear(
                  backward
                    ? endOfYear(subYears(chartParams.value.end, 1))
                    : endOfYear(addYears(chartParams.value.end, 1))
                )
              : selectedTimeFrame.value === 'week'
              ? startOfMonth(
                  backward
                    ? endOfWeek(subWeeks(chartParams.value.end, 1))
                    : endOfWeek(addWeeks(chartParams.value.end, 1))
                )
              : startOfMonth(
                  backward
                    ? endOfMonth(subMonths(chartParams.value.end, 1))
                    : endOfMonth(addMonths(chartParams.value.end, 1))
                ),
          start:
            selectedTimeFrame.value === 'year'
              ? startOfYear(
                  backward
                    ? startOfYear(subYears(chartParams.value.start, 1))
                    : startOfYear(addYears(chartParams.value.start, 1))
                )
              : selectedTimeFrame.value === 'week'
              ? startOfMonth(
                  backward
                    ? startOfWeek(subWeeks(chartParams.value.start, 1))
                    : startOfWeek(addWeeks(chartParams.value.start, 1))
                )
              : startOfMonth(
                  backward
                    ? startOfMonth(subMonths(chartParams.value.start, 1))
                    : startOfMonth(addMonths(chartParams.value.start, 1))
                ),
        }
      }
      function getSports(sports: ISport[]) {
        return sports.map((sport) => sport.id)
      }
      function updateSelectedSportIds(sportId: number) {
        if (selectedSportIds.value.includes(sportId)) {
          selectedSportIds.value = selectedSportIds.value.filter(
            (id) => id !== sportId
          )
        } else {
          selectedSportIds.value.push(sportId)
        }
      }

      watch(
        () => props.sports,
        (newSports) => {
          selectedSportIds.value = getSports(newSports)
        }
      )

      return {
        chartParams,
        selectedTimeFrame,
        sportColors,
        t,
        timeFrames,
        translatedSports,
        selectedSportIds,
        handleOnClickArrows,
        updateSelectedSportIds,
        updateTimeFrame,
      }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base';

  #user-statistics {
    display: flex;
    width: 100%;
    margin-bottom: 30px;
    ::v-deep(.card) {
      width: 100%;
      .card-content {
        .chart-filters {
          display: flex;

          .chart-arrow,
          .time-frames {
            flex-grow: 1;
            text-align: center;
          }

          .chart-arrow {
            cursor: pointer;
          }

          .time-frames {
            display: flex;
            justify-content: space-around;

            .time-frames-checkboxes {
              display: inline-flex;

              .time-frame {
                label {
                  font-weight: normal;
                  float: left;
                  padding: 0 5px;
                  cursor: pointer;
                }

                label input {
                  display: none;
                }

                label span {
                  border: solid 1px var(--time-frame-border-color);
                  border-radius: 9%;
                  display: block;
                  font-size: 0.9em;
                  padding: 2px 6px;
                  text-align: center;
                }

                input:checked + span {
                  background-color: var(--time-frame-checked-bg-color);
                  color: var(--time-frame-checked-color);
                }
              }
            }
          }
        }

        .chart-radio {
          justify-content: space-around;
          padding: $default-padding * 2 $default-padding;
        }

        .sports {
          display: flex;
          justify-content: space-between;
          padding: $default-padding * 2 $default-padding;
          @media screen and (max-width: $medium-limit) {
            justify-content: normal;
            flex-wrap: wrap;
          }

          label {
            display: flex;
            align-items: center;
            font-size: 0.9em;
            font-weight: normal;
            min-width: 120px;
            padding: $default-padding;
            @media screen and (max-width: $medium-limit) {
              min-width: 100px;
            }
            @media screen and (max-width: $x-small-limit) {
              width: 100%;
            }
          }

          .sport-img {
            padding: 3px;
            width: 20px;
            height: 20px;
          }
        }
      }
    }
  }
</style>
