<template>
  <div class="not-found">
    <NotFound />
  </div>
</template>

<script lang="ts">
  import { defineComponent } from 'vue'

  import NotFound from '@/components/Common/NotFound.vue'

  export default defineComponent({
    name: 'NotFoundView',
    components: {
      NotFound,
    },
  })
</script>
