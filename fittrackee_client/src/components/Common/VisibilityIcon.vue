<template>
  <div class="visibility">
    <i
      :class="`fa fa-${getPrivacyIcon(visibility)}`"
      aria-hidden="true"
      :title="$t(`privacy.LEVELS.${visibility}`)"
    />
  </div>
</template>

<script setup lang="ts">
import { toRefs } from 'vue'

import { TPrivacyLevels } from "@/types/user";

interface Props {
  visibility: TPrivacyLevels
}

const props = defineProps<Props>()
const { visibility } = toRefs(props)

function getPrivacyIcon(privacyLevel: TPrivacyLevels): string {
  switch (privacyLevel) {
    case 'public':
      return 'globe'
    case 'followers_and_remote_only':
    case 'followers_only':
      return 'users'
    default:
    case 'private':
      return 'lock'
  }
}
</script>