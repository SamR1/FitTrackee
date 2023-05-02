<template>
  <div id="notifications" class="view items-list-view">
    <div class="container items-list-container">
      <div class="filters-container" :class="{ hidden: hiddenFilters }">
        <notificationsFilters @filter="toggleFilters" />
      </div>
      <div class="display-filters">
        <div @click="toggleFilters">
          <i
            :class="`fa fa-caret-${hiddenFilters ? 'down' : 'up'}`"
            aria-hidden="true"
          />
          <span>
            {{ $t(`workouts.${hiddenFilters ? 'DISPLAY' : 'HIDE'}_FILTERS`) }}
          </span>
        </div>
      </div>
      <div class="list-container">
        <Notifications />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ref } from 'vue'

  import Notifications from '@/components/Notifications/Notifications.vue'
  import NotificationsFilters from '@/components/Notifications/NotificationsFilters.vue'

  const hiddenFilters = ref(true)

  function toggleFilters() {
    hiddenFilters.value = !hiddenFilters.value
  }
</script>
