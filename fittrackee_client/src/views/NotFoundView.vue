<template>
  <div class="not-found">
    <NotFound />
  </div>
</template>

<script lang="ts">
  import { defineComponent } from 'vue'
  import { useI18n } from 'vue-i18n'

  import NotFound from '@/components/Common/NotFound.vue'

  export default defineComponent({
    name: 'NotFoundView',
    components: {
      NotFound,
    },
    setup() {
      const { t } = useI18n()
      return { t }
    },
  })
</script>
