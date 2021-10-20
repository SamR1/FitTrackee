<template>
  <Error
    title="404"
    :message="$t(`error.NOT_FOUND.${target}`)"
    :button-text="t('common.HOME')"
  />
</template>

<script lang="ts">
  import { defineComponent } from 'vue'

  import Error from '@/components/Common/Error.vue'

  export default defineComponent({
    name: 'NotFound',
    components: {
      Error,
    },
    props: {
      target: {
        type: String,
        default: 'PAGE',
      },
    },
  })
</script>
