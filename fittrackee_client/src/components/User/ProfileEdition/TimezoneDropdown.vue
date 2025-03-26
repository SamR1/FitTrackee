<template>
  <div id="tz-dropdown">
    <input
      class="tz-dropdown-input"
      id="timezone"
      name="timezone"
      :value="timezone"
      :disabled="disabled"
      required
      role="combobox"
      aria-autocomplete="list"
      aria-controls="tz-dropdown-list"
      :aria-expanded="isOpen"
      @keydown.esc="cancelUpdate()"
      @keydown.enter="onEnter"
      @input="openDropdown"
      @blur="closeDropdown()"
      @keydown.down="onKeyDown()"
      @keydown.up="onKeyUp()"
    />
    <ul
      class="tz-dropdown-list"
      id="tz-dropdown-list"
      v-if="isOpen"
      role="listbox"
      tabindex="-1"
      :aria-label="$t('user.PROFILE.TIMEZONE', 0)"
    >
      <li
        v-for="(tz, index) in filteredTimezones"
        :key="tz"
        :id="`tz-dropdown-item-${index}`"
        class="tz-dropdown-item"
        :class="{ focus: index === focusItemIndex }"
        @click="onUpdateTimezone(index)"
        @mouseover="onMouseOver(index)"
        :autofocus="index === focusItemIndex"
        role="option"
      >
        {{ tz }}
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
  import { computed, onBeforeMount, ref, toRefs, watch } from 'vue'
  import type { ComputedRef, Ref } from 'vue'

  import { AUTH_USER_STORE } from '@/store/constants.ts'
  import { useStore } from '@/use/useStore.ts'

  interface Props {
    input: string
    disabled?: boolean
  }
  const props = withDefaults(defineProps<Props>(), {
    disabled: false,
  })
  const { input, disabled } = toRefs(props)

  const store = useStore()

  const emit = defineEmits(['updateTimezone'])

  const timezone: Ref<string> = ref(input.value)
  const isOpen: Ref<boolean> = ref(false)
  const focusItemIndex: Ref<number> = ref(0)

  let timeZones: ComputedRef<string[]> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.TIMEZONES]
  )

  const filteredTimezones: ComputedRef<string[]> = computed(() =>
    input.value
      ? timeZones.value.filter((t) => matchTimezone(t))
      : timeZones.value
  )

  function matchTimezone(t: string): RegExpMatchArray | null {
    return t.toLowerCase().match(timezone.value.toLowerCase())
  }
  function onMouseOver(index: number) {
    focusItemIndex.value = index
  }
  function onUpdateTimezone(index: number) {
    if (filteredTimezones.value.length > index) {
      timezone.value = filteredTimezones.value[index]
      emit('updateTimezone', timezone.value)
      isOpen.value = false
    }
  }
  function onEnter(event: Event) {
    event.preventDefault()
    if (filteredTimezones.value.length > 0) {
      onUpdateTimezone(focusItemIndex.value)
    }
  }
  function openDropdown(event: Event) {
    event.preventDefault()
    isOpen.value = true
    timezone.value = (event.target as HTMLInputElement).value.trim()
  }
  function closeDropdown() {
    onUpdateTimezone(focusItemIndex.value)
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
    if (focusItemIndex.value >= filteredTimezones.value.length) {
      focusItemIndex.value = 0
    }
    scrollIntoOption(focusItemIndex.value)
  }
  function onKeyUp() {
    isOpen.value = true
    focusItemIndex.value =
      focusItemIndex.value === null
        ? filteredTimezones.value.length - 1
        : (focusItemIndex.value -= 1)
    if (focusItemIndex.value <= -1) {
      focusItemIndex.value = filteredTimezones.value.length - 1
    }
    scrollIntoOption(focusItemIndex.value)
  }
  function cancelUpdate() {
    if (isOpen.value) {
      isOpen.value = false
      timezone.value = input.value
    }
  }

  watch(
    () => props.input,
    (value) => {
      timezone.value = value
    }
  )

  onBeforeMount(() => {
    if (timeZones.value.length === 0) {
      store.dispatch(AUTH_USER_STORE.ACTIONS.GET_TIMEZONES)
    }
  })
</script>

<style lang="scss" scoped>
  @use '~@/scss/vars.scss' as *;

  #tz-dropdown {
    display: flex;
    flex-direction: column;
    position: relative;

    .tz-dropdown-list {
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
    .tz-dropdown-item {
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
