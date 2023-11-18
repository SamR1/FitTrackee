<template>
  <div class="profile-tabs custom-checkboxes-group">
    <div class="profile-tabs-checkboxes custom-checkboxes">
      <div v-for="tab in tabs" class="profile-tab custom-checkbox" :key="tab">
        <label>
          <input
            type="radio"
            :id="tab"
            :name="tab"
            :checked="selectedTab.split('/')[0] === tab"
            :disabled="disabled"
            @input="$router.push(getPath(tab))"
          />
          <span
            :id="`tab-${tab}`"
            :tabindex="0"
            role="button"
            @keydown.enter="$router.push(getPath(tab))"
          >
            {{ $t(`user.PROFILE.TABS.${tab}`) }}
          </span>
        </label>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { onMounted, toRefs } from 'vue'

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
      case 'BLOCKED-USERS':
      case 'FOLLOW-REQUESTS':
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

  .profile-tabs-checkboxes {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: $default-margin * 0.5;
  }
  @media screen and (max-width: $small-limit) {
    .profile-tabs-checkboxes {
      display: flex;
      flex-wrap: wrap;
      justify-content: center;

      .profile-tab {
        padding-bottom: $default-padding * 0.5;
      }
    }
  }
</style>
