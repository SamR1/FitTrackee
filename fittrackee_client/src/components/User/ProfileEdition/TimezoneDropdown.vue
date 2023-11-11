<template>
  <div id="tz-dropdown">
    <input
      class="tz-dropdown-input"
      id="timezone"
      name="timezone"
      :value="timezone"
      :disabled="disabled"
      required
      @keydown.esc="onUpdateTimezone(input)"
      @keydown.enter="onEnter"
      @input="openDropdown"
    />
    <ul class="tz-dropdown-list" v-if="isOpen" ref="tzList">
      <li
        v-for="(tz, index) in timeZones.filter((t) => matchTimezone(t))"
        :key="tz"
        class="tz-dropdown-item"
        :class="{ focus: index === focusItemIndex }"
        @click="onUpdateTimezone(tz)"
        @mouseover="onMouseOver(index)"
        :autofocus="index === focusItemIndex"
      >
        {{ tz }}
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
  import { ref, toRefs, watch } from 'vue'
  import type { Ref } from 'vue'

  import { timeZones } from '@/utils/timezone'

  interface Props {
    input: string
    disabled?: boolean
  }
  const props = withDefaults(defineProps<Props>(), {
    disabled: false,
  })

  const emit = defineEmits(['updateTimezone'])

  const { input, disabled } = toRefs(props)
  const timezone: Ref<string> = ref(input.value)
  const isOpen: Ref<boolean> = ref(false)
  const tzList: Ref<HTMLInputElement | null> = ref(null)
  const focusItemIndex: Ref<number> = ref(0)

  function matchTimezone(t: string): RegExpMatchArray | null {
    return t.toLowerCase().match(timezone.value.toLowerCase())
  }
  function onMouseOver(index: number) {
    focusItemIndex.value = index
  }
  function onUpdateTimezone(value: string) {
    timezone.value = value
    isOpen.value = false
    emit('updateTimezone', value)
  }
  function onEnter(event: Event & { target: HTMLInputElement }) {
    event.preventDefault()
    if (tzList.value?.firstElementChild?.innerHTML) {
      onUpdateTimezone(tzList.value?.firstElementChild?.innerHTML)
    }
  }
  function openDropdown(event: Event & { target: HTMLInputElement }) {
    event.preventDefault()
    isOpen.value = true
    timezone.value = event.target.value.trim()
  }

  watch(
    () => props.input,
    (value) => {
      timezone.value = value
    }
  )
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';

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
