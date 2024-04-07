<template>
  <div class="profile-tabs">
    <div class="profile-tabs-links">
      <router-link
        class="profile-tab"
        :class="{ selected: tab === selectedTab }"
        v-for="tab in tabs"
        :to="getPath(tab)"
        :key="tab"
      >
        {{ $t(`user.PROFILE.TABS.${tab}`) }}
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { onMounted, toRefs } from 'vue'

  interface Props {
    tabs: string[]
    selectedTab: string
    edition: boolean
  }
  const props = defineProps<Props>()

  const { tabs, selectedTab } = toRefs(props)

  onMounted(() => {
    const input = document.getElementById(`tab-${tabs.value[0]}`)
    if (input) {
      input.focus()
    }
  })

  function getPath(tab: string) {
    switch (tab) {
      case 'ACCOUNT':
      case 'PICTURE':
      case 'PRIVACY-POLICY':
        return `/profile/edit/${tab.toLocaleLowerCase()}`
      case 'APPS':
      case 'EQUIPMENTS':
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
  @import '~@/scss/vars.scss';

  .profile-tabs-links {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: $default-margin * 1.5;
    margin-bottom: $default-margin;

    a {
      border: solid 1px var(--custom-checkbox-border-color);
      border-radius: 5px;
      color: var(--app-color);
      display: block;
      font-size: 0.9em;
      padding: 2px 6px;
      text-align: center;
      text-decoration: none;

      &.selected {
        background-color: var(--custom-checkbox-checked-bg-color);
        color: var(--custom-checkbox-checked-color);
      }
    }
  }
</style>
