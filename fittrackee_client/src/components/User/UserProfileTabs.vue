<template>
  <div class="profile-tabs custom-checkboxes-group">
    <div class="profile-tabs-checkboxes custom-checkboxes">
      <div v-for="tab in tabs" class="profile-tab custom-checkbox" :key="tab">
        <label>
          <input
            type="radio"
            :id="tab"
            :name="tab"
            :checked="selectedTab === tab"
            :disabled="disabled"
            @input="$router.push(getPath(tab))"
          />
          <span>{{ $t(`user.PROFILE.TABS.${tab}`) }}</span>
        </label>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { toRefs, withDefaults } from 'vue'

  interface Props {
    tabs: string[]
    selectedTab: string
    edition: boolean
    disabled?: boolean
  }
  const props = withDefaults(defineProps<Props>(), {
    disabled: false,
  })

  const { tabs, selectedTab, disabled } = toRefs(props)

  function getPath(tab: string) {
    switch (tab) {
      case 'PICTURE':
        return '/profile/edit/picture'
      case 'PREFERENCES':
      case 'SPORTS':
        return `/profile${
          props.edition ? '/edit' : ''
        }/${tab.toLocaleLowerCase()}`
      default:
      case 'PROFILE':
        return `/profile${props.edition ? '/edit' : ''}`
    }
  }
</script>

<style lang="scss">
  @import '~@/scss/base.scss';

  .profile-tabs {
    margin: $default-margin 0 $default-margin;
  }
</style>
