<template>
  <Error
    title="404"
    :message="$t(`error.NOT_FOUND.${target}`)"
    :button-text="$t('common.HOME')"
  />
</template>

<script setup lang="ts">
  import { toRefs, withDefaults } from 'vue'

  import Error from '@/components/Common/Error.vue'
  interface Props {
    target?: string
  }
  const props = withDefaults(defineProps<Props>(), {
    target: 'PAGE',
  })
  const { target } = toRefs(props)
</script>
