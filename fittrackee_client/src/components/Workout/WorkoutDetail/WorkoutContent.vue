<template>
  <div id="workout-content">
    <Card>
      <template #title>{{ $t(`workouts.${contentType}`) }}</template>
      <template #content>
        <span
          :class="{ notes: contentType === 'NOTES' || !content }"
          v-html="
            displayedContent && displayedContent !== ''
              ? linkifyAndClean(displayedContent)
              : $t(`workouts.NO_${contentType}`)
          "
        />
        <button
          class="read-more transparent"
          v-if="displayReadMoreButton"
          @click="readMore = !readMore"
        >
          <i
            :class="`fa fa-caret-${readMore ? 'up' : 'down'}`"
            aria-hidden="true"
          />
          {{ $t(`buttons.${readMore ? 'HIDE' : 'READ_MORE'}`) }}
        </button>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
  import { computed, toRefs, ref } from 'vue'
  import type { ComputedRef, Ref } from 'vue'

  import { linkifyAndClean } from '@/utils/inputs'

  interface Props {
    contentType: 'DESCRIPTION' | 'NOTES'
    content?: string | null
  }
  const props = withDefaults(defineProps<Props>(), {
    content: () => '',
  })

  const { content, contentType } = toRefs(props)

  const READ_MORE_LIMIT = 1000
  const displayReadMoreButton: ComputedRef<boolean> = computed(
    () => content.value !== null && content.value.length > READ_MORE_LIMIT
  )
  const readMore: Ref<boolean> = ref(false)
  const displayedContent: ComputedRef<string | null> = computed(() =>
    readMore.value ? content.value : getTruncatedText(content.value)
  )

  function getTruncatedText(text: string | null) {
    if (text === null || text.length <= READ_MORE_LIMIT) {
      return text
    }
    return text.slice(0, READ_MORE_LIMIT - 10) + '…'
  }
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';

  #workout-content {
    ::v-deep(.card-title) {
      text-transform: capitalize;
    }
    ::v-deep(.card-content) {
      white-space: pre-wrap;
      .read-more {
        font-size: 0.85em;
        font-weight: bold;
        padding: 0 10px;
      }
      .notes {
        font-style: italic;
      }
    }
  }
</style>
