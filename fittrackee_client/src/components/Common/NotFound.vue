<template>
  <Error
    v-if="errorDisplayed"
    title="404"
    :message="$t(`error.NOT_FOUND.${target}`)"
    :button-text="$t('common.HOME')"
  />
</template>

<script setup lang="ts">
  import { onMounted, ref, toRefs, onUnmounted } from 'vue'
  import type { Ref } from 'vue'

  import Error from '@/components/Common/Error.vue'

  interface Props {
    target?: string
  }
  const props = withDefaults(defineProps<Props>(), {
    target: 'PAGE',
  })
  const { target } = toRefs(props)

  const timer: Ref<number | undefined> = ref()
  const errorDisplayed: Ref<boolean> = ref(false)

  function displayError() {
    timer.value = setTimeout(() => {
      errorDisplayed.value = true
    }, 500)
  }

  onMounted(() => displayError())
  onUnmounted(() => {
    if (timer.value) {
      clearTimeout(timer.value)
    }
  })
</script>
