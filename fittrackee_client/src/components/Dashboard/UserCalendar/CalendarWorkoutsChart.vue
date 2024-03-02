<template>
  <div class="calendar-workouts-chart">
    <button
      class="workouts-chart transparent"
      :id="`workouts-donut-${index}`"
      @click="togglePane"
    >
      <div class="workouts-count">{{ workouts.length }}</div>
      <DonutChart :datasets="datasets" :colors="colors" />
    </button>
    <div class="workouts-pane" v-if="!isHidden">
      <div
        class="more-workouts"
        :id="`workouts-pane-${index}`"
        v-click-outside="togglePane"
      >
        <button class="calendar-more-close transparent" @click="togglePane">
          <i class="fa fa-times" aria-hidden="true" />
        </button>
        <CalendarWorkout
          v-for="(workout, index) in workouts"
          :key="index"
          :displayHARecord="displayHARecord"
          :workout="workout"
          :sportLabel="getSportLabel(workout, sports)"
          :sportColor="getSportColor(workout, sports)"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { nextTick, onMounted, onUnmounted, ref, toRefs } from 'vue'

  import CalendarWorkout from '@/components/Dashboard/UserCalendar/CalendarWorkout.vue'
  import DonutChart from '@/components/Dashboard/UserCalendar/DonutChart.vue'
  import type { ISport } from '@/types/sports'
  import type { IWorkout } from '@/types/workouts'
  import { getSportColor, getSportLabel } from '@/utils/sports'

  interface Props {
    colors: Record<number, string>
    datasets: Record<number, Record<string, number>>
    sports: ISport[]
    workouts: IWorkout[]
    displayHARecord: boolean
    index: number
  }
  const props = defineProps<Props>()
  let tabbableElementIndex = 0

  const { colors, datasets, index, sports, workouts } = toRefs(props)
  const isHidden = ref(true)

  function isWorkoutsMorePaneDisplayed() {
    const pane = document.getElementById(`workouts-pane-${index.value}`)
    return pane?.children && pane?.children.length > 0 ? pane : null
  }

  async function togglePane(event: Event) {
    event.preventDefault()
    event.stopPropagation()
    isHidden.value = !isHidden.value
    await nextTick()
    const pane = isWorkoutsMorePaneDisplayed()
    if (!isHidden.value) {
      ;(pane?.children[0] as HTMLButtonElement).focus()
    } else {
      document.getElementById(`workouts-donut-${index.value}`)?.focus()
    }
  }
  function handleKey(e: KeyboardEvent) {
    if (!isHidden.value) {
      // focusTrap
      if (!isHidden.value && (e.key === 'Tab' || e.keyCode === 9)) {
        e.preventDefault()
        e.stopPropagation()
        const pane = isWorkoutsMorePaneDisplayed()
        if (pane) {
          if (e.shiftKey) {
            tabbableElementIndex -= 1
            if (tabbableElementIndex < 0) {
              tabbableElementIndex = pane.children.length - 1
            }
          } else {
            tabbableElementIndex += 1
            if (tabbableElementIndex >= pane.children.length) {
              tabbableElementIndex = 0
            }
          }
          // children are only links or buttons
          ;(
            pane.children[tabbableElementIndex] as
              | HTMLButtonElement
              | HTMLLinkElement
          ).focus()
        }
      }
      // close pane on Escape
      if (e.key === 'Escape') {
        togglePane(e)
      }
    }
  }

  onMounted(() => {
    document.addEventListener('keydown', handleKey)
  })
  onUnmounted(() => {
    document.removeEventListener('keydown', handleKey)
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';
  .calendar-workouts-chart {
    display: flex;

    .workouts-chart {
      position: relative;
      padding: 0;
      .workouts-count {
        display: flex;
        justify-content: center;
        position: absolute;
        top: 4px;
        left: 6px;
        width: 20px;
        font-size: 1.1em;
        font-weight: bold;
      }
      @media screen and (max-width: $small-limit) {
        .workouts-count {
          top: 16px;
          left: 6px;
        }
        ::v-deep(.donut-chart) {
          padding-top: 12px;
          svg g circle {
            stroke-width: 2;
            stroke-opacity: 0.8;
          }
        }
      }
    }

    .workouts-pane {
      display: flex;
      padding-left: 40px;

      .more-workouts {
        background: var(--calendar-workouts-color);
        border-radius: 4px;
        box-shadow:
          0 4px 8px 0 var(--calendar-workouts-box-shadow-0),
          0 6px 20px 0 var(--calendar-workouts-box-shadow-1);
        position: absolute;
        top: 52px;
        left: 0;
        min-width: 60px;
        @media screen and (max-width: $small-limit) {
          min-width: 70px;
        }

        margin-bottom: 20px;
        padding: 10px 10px;

        display: flex;
        flex-wrap: wrap;
        z-index: 1000;

        .calendar-more-close {
          position: absolute;
          font-size: 0.9em;
          top: 5px;
          right: 5px;
          padding: 0;
        }
      }
    }
  }
</style>
