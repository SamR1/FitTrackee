<template>
  <div>
    <WorkoutVisibility
      :workoutObject="workoutObject"
      :useImperialUnits="displayOptions.useImperialUnits"
      :displayHARecord="displayOptions.displayAscent"
      v-if="workoutObject.workoutVisibility"
    />
    <div class="workout-equipments" v-if="workoutObject.equipments">
      <EquipmentBadge
        v-for="equipment in workoutObject.equipments"
        :equipment="equipment"
        :workout-id="workoutObject.workoutId"
        :key="equipment.label"
      />
    </div>
  </div>
</template>
<script setup lang="ts">
  import { toRefs } from 'vue'

  import EquipmentBadge from '@/components/Common/EquipmentBadge.vue'
  import WorkoutVisibility from '@/components/Workout/WorkoutDetail/WorkoutVisibility.vue'
  import type { IDisplayOptions } from '@/types/application.ts'
  import type { IWorkoutObject } from '@/types/workouts.ts'

  interface Props {
    workoutObject: IWorkoutObject
    displayOptions: IDisplayOptions
  }
  const props = defineProps<Props>()
  const { workoutObject, displayOptions } = toRefs(props)
</script>
