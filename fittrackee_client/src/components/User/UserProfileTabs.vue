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
          <span>{{ t(`user.PROFILE.TABS.${tab}`) }}</span>
        </label>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
  import { PropType, defineComponent } from 'vue'
  import { useI18n } from 'vue-i18n'

  export default defineComponent({
    name: 'UserProfileTabs',
    props: {
      tabs: {
        type: Object as PropType<string[]>,
        required: true,
      },
      selectedTab: {
        type: String,
        required: true,
      },
      edition: {
        type: Boolean,
        required: true,
      },
      disabled: {
        type: Boolean,
        default: false,
      },
    },
    setup(props) {
      const { t } = useI18n()
      function getPath(tab: string) {
        switch (tab) {
          case 'PICTURE':
            return '/profile/edit/picture'
          case 'PREFERENCES':
            return `/profile${props.edition ? '/edit' : ''}/preferences`
          default:
          case 'PROFILE':
            return `/profile${props.edition ? '/edit' : ''}`
        }
      }
      return { t, getPath }
    },
  })
</script>

<style lang="scss">
  @import '~@/scss/base.scss';

  .profile-tabs {
    margin: $default-margin 0 $default-margin;
  }
</style>
