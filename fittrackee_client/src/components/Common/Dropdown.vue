<template>
  <div class="dropdown-wrapper">
    <div class="dropdown-selected" @click="openDropdown">
      <slot></slot>
    </div>
    <ul class="dropdown-list" v-if="isOpen">
      <li
        class="dropdown-item"
        :class="{ selected: option.value === selected }"
        v-for="(option, index) in dropdownOptions"
        :key="index"
        @click="updateSelected(option)"
      >
        {{ option.label }}
      </li>
    </ul>
  </div>
</template>

<script lang="ts">
  import { PropType, defineComponent, ref } from 'vue'
  import { IDropdownOption } from '@/interfaces'
  import { TDropdownOptions } from '@/types'

  export default defineComponent({
    name: 'Dropdown',
    props: {
      options: {
        type: Object as PropType<TDropdownOptions>,
        required: true,
      },
      selected: {
        type: String,
        required: true,
      },
    },
    emits: {
      selected: (option: IDropdownOption) => option,
    },
    setup(props, { emit }) {
      let isOpen = ref(false)
      let dropdownOptions = props.options.map((option) => option)

      function openDropdown() {
        isOpen.value = true
      }
      function updateSelected(option: IDropdownOption) {
        emit('selected', option)
        isOpen.value = false
      }
      function getSelectedLabel(selectedValue: string) {
        return props.options.filter(
          (option: IDropdownOption) => option.value === selectedValue
        )[0].label
      }

      return {
        dropdownOptions,
        updateSelected,
        getSelectedLabel,
        isOpen,
        openDropdown,
      }
    },
  })
</script>

<style scoped lang="scss">
  .dropdown-list {
    list-style-type: none;
    background-color: #ffffff;
    padding: 0;
    margin: 5px 0;
    position: absolute;
    text-align: left;
    border: solid 1px lightgrey;
    box-shadow: 2px 2px 5px lightgrey;

    li {
      padding-top: 5px;
    }
    li:last-child {
      padding-bottom: 5px;
    }
  }

  .dropdown-item {
    cursor: default;

    &.selected {
      font-weight: bold;
    }

    &.selected::after {
      content: ' ✔';
    }
  }
</style>
