<template>
  <div id="location-dropdown">
    <input
      id="location"
      name="location"
      v-model="location"
      role="combobox"
      aria-autocomplete="list"
      aria-controls="location-dropdown-list"
      :aria-expanded="isOpen"
      @keydown.esc="cancelUpdate()"
      @keydown.enter="onEnter"
      @blur="closeDropdown()"
      @keydown.down="onKeyDown()"
      @keydown.up="onKeyUp()"
    />
    <ul
      class="location-dropdown-list"
      id="location-dropdown-list"
      v-if="isOpen"
      role="listbox"
      tabindex="-1"
      :aria-label="$t('workouts.LOCATIONS')"
    >
      <li
        v-for="(location, index) in locations"
        :key="index"
        :id="`location-dropdown-item-${index}`"
        class="location-dropdown-item"
        :class="{ focus: index === focusItemIndex }"
        @click="onUpdateLocation(index)"
        @mouseover="onMouseOver(index)"
        :autofocus="index === focusItemIndex"
        role="option"
      >
        {{ location.display_name }}
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
  import { onUnmounted, ref, watch } from 'vue'
  import type { Ref } from 'vue'

  import type { ILocation } from '@/types/workouts.ts'
  import { getLocationFromQuery } from '@/utils/geocode.ts'

  const emit = defineEmits(['updateCoordinates'])

  const location: Ref<string> = ref('')
  const isOpen: Ref<boolean> = ref(false)
  const focusItemIndex: Ref<number> = ref(0)
  const timer: Ref<ReturnType<typeof setTimeout> | undefined> = ref()
  const locations: Ref<ILocation[]> = ref([])

  function onMouseOver(index: number) {
    focusItemIndex.value = index
  }
  function onUpdateLocation(index: number) {
    isOpen.value = false
    if (locations.value.length > index) {
      location.value = locations.value[index].display_name
      emit('updateCoordinates', locations.value[index].coordinates)
      isOpen.value = false
    }
  }
  function onEnter(event: Event) {
    event.preventDefault()
    if (locations.value.length > 0) {
      onUpdateLocation(focusItemIndex.value)
    }
  }
  function closeDropdown() {
    onUpdateLocation(focusItemIndex.value)
  }
  function scrollIntoOption(index: number) {
    const option = document.getElementById(`tz-dropdown-item-${index}`)
    if (option) {
      option.focus()
      option.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
    }
  }
  function onKeyDown() {
    isOpen.value = true
    focusItemIndex.value =
      focusItemIndex.value === null ? 0 : (focusItemIndex.value += 1)
    if (focusItemIndex.value >= locations.value.length) {
      focusItemIndex.value = 0
    }
    scrollIntoOption(focusItemIndex.value)
  }
  function onKeyUp() {
    isOpen.value = true
    focusItemIndex.value =
      focusItemIndex.value === null
        ? locations.value.length - 1
        : (focusItemIndex.value -= 1)
    if (focusItemIndex.value <= -1) {
      focusItemIndex.value = locations.value.length - 1
    }
    scrollIntoOption(focusItemIndex.value)
  }
  function cancelUpdate() {
    if (isOpen.value) {
      isOpen.value = false
      location.value = ''
    }
  }

  watch(
    () => location.value,
    async (newValue) => {
      if (!newValue) {
        locations.value = []
      } else if (
        locations.value.filter(({ display_name }) => display_name === newValue)
          .length === 0
      ) {
        clearTimeout(timer.value)
        timer.value = setTimeout(async () => {
          locations.value = await getLocationFromQuery(newValue)
        }, 1000)
      }
    },
    { immediate: true }
  )
  watch(
    () => locations.value,
    async (value) => {
      if (value.length > 0) {
        isOpen.value = true
      }
    },
    { immediate: true }
  )

  onUnmounted(() => {
    if (timer.value) {
      clearTimeout(timer.value)
    }
  })
</script>

<style lang="scss" scoped>
  @use '~@/scss/vars.scss' as *;

  #location-dropdown {
    display: flex;
    flex-direction: column;
    position: relative;

    .location-dropdown-list {
      background-color: var(--input-bg-color);
      border-radius: $border-radius;
      border: solid 1px var(--input-border-color);
      padding: $default-padding * 0.5 0;
      position: absolute;
      overflow-y: auto;
      top: 20px;
      left: 0;
      right: 0;
      max-height: 200px;
      width: inherit;
    }
    .location-dropdown-item {
      cursor: pointer;
      font-size: 0.9em;
      font-weight: normal;
      padding: $default-padding * 0.5;

      &.focus {
        background-color: var(--dropdown-hover-color);
      }
    }
  }
</style>
