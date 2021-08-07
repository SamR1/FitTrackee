<template>
  <div class="not-found">
    <Error
      title="404"
      :message="t('error.not-found.PAGE')"
      :button-text="t('common.HOME')"
    />
  </div>
</template>

<script lang="ts">
  import { defineComponent } from 'vue'
  import { useI18n } from 'vue-i18n'
  import Error from '@/components/Error.vue'

  export default defineComponent({
    name: 'NotFound',
    components: {
      Error,
    },
    setup() {
      const { t } = useI18n()
      return { t }
    },
  })
</script>
