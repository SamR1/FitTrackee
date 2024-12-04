<template>
  <div class="visibility">
    <i
      :class="`fa fa-${getVisibilityIcon(visibility)}`"
      aria-hidden="true"
      :title="
        $t(
          `visibility_levels.${isComment ? 'COMMENT_' : ''}LEVELS.${visibility}`
        )
      "
    />
  </div>
</template>

<script setup lang="ts">
  import { toRefs } from 'vue'

  import type { TVisibilityLevels } from '@/types/user'

  interface Props {
    visibility: TVisibilityLevels
    isComment?: boolean
  }

  const props = withDefaults(defineProps<Props>(), {
    isComment: false,
  })
  const { visibility, isComment } = toRefs(props)

  function getVisibilityIcon(visibilityLevel: TVisibilityLevels): string {
    switch (visibilityLevel) {
      case 'public':
        return 'globe'
      case 'followers_only':
        return 'users'
      default:
      case 'private':
        return 'lock'
    }
  }
</script>
