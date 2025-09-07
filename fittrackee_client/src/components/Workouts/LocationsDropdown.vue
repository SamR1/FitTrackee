<template>
  <div id="location-dropdown">
    <input
      id="location"
      name="location"
      v-model="locationDisplayName"
      role="combobox"
      aria-autocomplete="list"
      aria-controls="location-dropdown-list"
      :aria-expanded="isOpen"
      :title="locationDisplayName || undefined"
      @keydown.esc="cancelUpdate()"
      @keydown.enter="onEnter"
      @blur="closeDropdown()"
      @keydown.down="onKeyDown()"
      @keydown.up="onKeyUp()"
    />
    <span v-if="geocodeLoading" class="geocode-loader">
      <i class="fa fa-spinner fa-pulse" aria-hidden="true" />
    </span>
    <ul
      class="location-dropdown-list"
      id="location-dropdown-list"
      v-if="isOpen"
      role="listbox"
      tabindex="-1"
      :aria-label="$t('workouts.LOCATION', 0)"
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
        {{ location.display_name }} ({{
          t(`workouts.NOMINATIM_ADDRESS_TYPE.${location.addresstype}`)
        }})
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
  import { computed, onUnmounted, ref, toRefs, watch } from 'vue'
  import type { ComputedRef, Ref } from 'vue'
  import { useI18n } from 'vue-i18n'

  import store from '@/store'
  import { WORKOUTS_STORE } from '@/store/constants.ts'
  import type { ILocation } from '@/types/workouts.ts'
  import { getLocationFromCity } from '@/utils/geocode.ts'

  interface Props {
    location: string
  }
  const props = defineProps<Props>()
  const { location } = toRefs(props)

  const { t } = useI18n()

  const emit = defineEmits(['updateCoordinates'])

  const locationDisplayName: Ref<string> = ref(location.value)
  const isOpen: Ref<boolean> = ref(false)
  const focusItemIndex: Ref<number> = ref(0)
  const timer: Ref<ReturnType<typeof setTimeout> | undefined> = ref()
  const locations: Ref<ILocation[]> = ref([])
  const geocodeLoading: ComputedRef<boolean> = computed(
    () => store.getters[WORKOUTS_STORE.GETTERS.GEOCODE_LOADING]
  )
  function onMouseOver(index: number) {
    focusItemIndex.value = index
  }
  function onUpdateLocation(index: number) {
    isOpen.value = false
    if (locations.value.length > index) {
      locationDisplayName.value = `${locations.value[index].display_name} (${t(`workouts.NOMINATIM_ADDRESS_TYPE.${locations.value[index].addresstype}`)})`
      emit('updateCoordinates', {
        coordinates: locations.value[index].coordinates,
        display_name: locationDisplayName.value,
        osm_id: locations.value[index].osm_id,
      })
    } else {
      locationDisplayName.value = ''
      emit('updateCoordinates', {
        coordinates: '',
        display_name: '',
        osm_id: '',
      })
    }
  }
  function onEnter(event: Event) {
    event.preventDefault()
    if (locations.value.length > 0) {
      onUpdateLocation(focusItemIndex.value)
    } else {
      emit('updateCoordinates', {
        coordinates: '',
        osm_id: '',
      })
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
      locationDisplayName.value = ''
    }
  }

  watch(
    () => location.value,
    (newValue) => {
      locationDisplayName.value = newValue
    }
  )
  watch(
    () => locationDisplayName.value,
    async (newValue) => {
      if (!newValue) {
        locations.value = []
      } else if (
        location.value !== newValue &&
        locations.value.filter(
          ({ display_name, addresstype }) =>
            `${display_name} (${t(`workouts.NOMINATIM_ADDRESS_TYPE.${addresstype}`)})` ===
            newValue
        ).length === 0
      ) {
        clearTimeout(timer.value)
        timer.value = setTimeout(async () => {
          store.commit(WORKOUTS_STORE.MUTATIONS.SET_GEOCODE_LOADING, true)
          locations.value = await getLocationFromCity(newValue)
          store.commit(WORKOUTS_STORE.MUTATIONS.SET_GEOCODE_LOADING, false)
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

    .geocode-loader {
      position: absolute;
      right: 10px;
      top: 10px;
    }
  }
</style>
