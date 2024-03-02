<template>
  <div class="dropdown-wrapper">
    <button
      aria-controls="dropdown-list"
      :aria-expanded="isOpen"
      aria-haspopup="true"
      :aria-label="buttonLabel"
      class="dropdown-selector transparent"
      @click="toggleDropdown()"
      ref="dropdownButton"
    >
      <slot></slot>
    </button>
    <ul
      v-if="isOpen"
      :aria-labelledby="listLabel"
      class="dropdown-list"
      id="dropdown-list"
      role="menu"
    >
      <li
        class="dropdown-item"
        :class="{
          selected: option.value === selected,
          focused: index === focusOptionIndex,
        }"
        v-for="(option, index) in options"
        :key="index"
        :id="`dropdown-item-${index}`"
        tabindex="-1"
        @click="updateSelected(option)"
        @keydown.enter="updateSelected(option)"
        @mouseover="onMouseOver(index)"
        role="menuitem"
      >
        {{ option.label }}
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
  import { type Ref, ref, onMounted, onUnmounted, toRefs, watch } from 'vue'
  import { useRoute } from 'vue-router'

  import type { IDropdownOption, TDropdownOptions } from '@/types/forms'
  interface Props {
    options: TDropdownOptions
    selected: string
    buttonLabel: string
    listLabel: string
  }
  const props = defineProps<Props>()
  const { options, selected } = toRefs(props)

  const emit = defineEmits({
    selected: (option: IDropdownOption) => option,
  })

  const route = useRoute()
  const isOpen = ref(false)
  const dropdownButton: Ref<HTMLButtonElement | null> = ref(null)
  const focusOptionIndex: Ref<number> = ref(
    getIndexFromOptionValue(selected.value)
  )

  function toggleDropdown() {
    if (isOpen.value) {
      closeDropdown()
    } else {
      isOpen.value = true
      const option = document.getElementById(
        `dropdown-item-${focusOptionIndex.value}`
      )
      option?.focus()
    }
  }
  function closeDropdown() {
    isOpen.value = false
    focusOptionIndex.value = getIndexFromOptionValue(selected.value)
    dropdownButton.value?.focus()
  }
  function updateSelected(option: IDropdownOption) {
    emit('selected', option)
    isOpen.value = false
  }
  function getIndexFromOptionValue(value: string) {
    const index = options.value.findIndex((o) => o.value === value)
    return index >= 0 ? index : 0
  }
  function handleKey(e: KeyboardEvent) {
    let prevent = false
    if (isOpen.value) {
      if (e.key === 'ArrowDown') {
        prevent = true
        focusOptionIndex.value += 1
        if (focusOptionIndex.value > options.value.length) {
          focusOptionIndex.value = 0
        }
      }
      if (e.key === 'ArrowUp') {
        prevent = true
        focusOptionIndex.value -= 1
        if (focusOptionIndex.value < 0) {
          focusOptionIndex.value = options.value.length - 1
        }
      }
      if (e.key === 'Home') {
        prevent = true
        focusOptionIndex.value = 0
      }
      if (e.key === 'End') {
        prevent = true
        focusOptionIndex.value = options.value.length - 1
      }
      if (e.key === 'Enter') {
        prevent = true
        updateSelected(options.value[focusOptionIndex.value])
      }
      if (e.key === 'Escape' || e.key === 'Tab') {
        prevent = e.key === 'Escape'
        closeDropdown()
      }
    }
    if (prevent) {
      e.stopPropagation()
      e.preventDefault()
    }
  }
  function onMouseOver(index: number) {
    focusOptionIndex.value = index
  }

  watch(
    () => route.path,
    () => (isOpen.value = false)
  )
  watch(
    () => selected.value,
    (value) => (focusOptionIndex.value = getIndexFromOptionValue(value))
  )

  onMounted(() => {
    document.addEventListener('keydown', handleKey)
  })
  onUnmounted(() => {
    document.removeEventListener('keydown', handleKey)
  })
</script>

<style scoped lang="scss">
  @import '~@/scss/vars.scss';
  .dropdown-wrapper {
    .dropdown-selector {
      margin: 0;
      padding: $default-padding * 0.5;
    }

    .dropdown-list {
      list-style-type: none;
      background-color: var(--dropdown-background-color);
      padding: 0 !important;
      margin-top: 5px;
      margin-left: -20px !important;
      position: absolute;
      text-align: left;
      border: solid 1px var(--dropdown-border-color);
      box-shadow: 2px 2px 5px var(--app-shadow-color);
      width: auto !important;

      .dropdown-item {
        padding: 3px 12px;
        &.selected {
          font-weight: bold;
        }

        &.selected::after {
          content: ' ✔';
        }

        &:hover,
        &.focused {
          background-color: var(--dropdown-hover-color);
        }
      }
    }
  }
</style>
