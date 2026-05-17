<template>
  <div class="custom-textarea">
    <div
      v-show="preview"
      :style="{ 'min-height': `${rows * rowHeight}px` }"
      class="preview"
      :class="{ 'white-space-pre-wrap': !useConvert }"
      v-html="useConvert ? convertToMarkdown(text) : linkifyAndClean(text)"
    />
    <textarea
      v-show="!preview"
      :style="{ 'min-height': `${textAreaHeight}px` }"
      :id="name"
      :name="name"
      :maxLength="charLimit"
      :disabled="disabled"
      :rows="rows"
      :required="required"
      :placeholder="placeholder"
      v-model="text"
      @input="updateText"
    />
    <div class="char-count-btn">
      <div class="remaining-chars" v-if="charLimit">
        {{ $t('workouts.REMAINING_CHARS') }}: {{ text.length }}/{{ charLimit }}.
        <span v-if="withMarkdown && withMarkdownInfo === 'text'">
          {{ $t('common.MARKDOWN_SYNTAX_CAN_BE_USED') }}
        </span>
      </div>
      <button
        v-if="withMarkdown"
        type="button"
        @click="preview = !preview"
        :disabled="!text"
      >
        {{ $t(`buttons.${preview ? 'WRITE' : 'PREVIEW'}`) }}
      </button>
    </div>
  </div>
  <span
    class="markdown-hints info-box"
    v-if="withMarkdown && withMarkdownInfo === 'info-box'"
  >
    <i class="fa fa-info-circle" aria-hidden="true" />
    {{ $t('workouts.MARKDOWN_SYNTAX') }}
  </span>
</template>

<script setup lang="ts">
  import { computed, ref, toRefs, watch } from 'vue'

  import { convertToMarkdown, linkifyAndClean } from '@/utils/inputs.ts'

  interface Props {
    name: string
    rows: number
    charLimit?: number
    disabled?: boolean
    input?: string | null
    required?: boolean
    placeholder?: string
    withMarkdown?: boolean
    withMarkdownInfo?: 'none' | 'info-box' | 'text'
    useConvert?: boolean
  }
  const props = withDefaults(defineProps<Props>(), {
    disabled: false,
    input: '',
    required: false,
    placeholder: '',
    withMarkdown: false,
    withMarkdownInfo: 'info-box',
    useConvert: false,
  })

  const emit = defineEmits(['updateValue'])

  const rowHeight = 17

  const { input, rows } = toRefs(props)
  const text = ref(input.value ? input.value : '')
  const preview = ref(false)

  const textAreaHeight = computed(() => calculateHeight())

  function updateText(event: Event) {
    const target = event.target as HTMLInputElement
    emit('updateValue', {
      value: target.value,
      selectionStart: target.selectionStart,
    })
  }
  function calculateHeight() {
    if (!text.value) {
      return rows.value * rowHeight
    }
    const lineBreaksCount = Math.max(
      (text.value.match(/\n/g) || []).length,
      rows.value
    )
    return rowHeight + lineBreaksCount * rowHeight
  }

  watch(
    () => props.input,
    (value) => {
      text.value = value === null ? '' : value
    }
  )
</script>

<style lang="scss" scoped>
  @use '~@/scss/vars.scss' as *;
  .custom-textarea {
    display: flex;
    flex-direction: column;
    .preview {
      font-weight: normal;
      font-style: normal;
      padding: $default-padding 0;
    }
    .char-count-btn {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      flex-wrap: wrap;
      .remaining-chars {
        font-weight: normal;
        font-size: 0.8em;
        font-style: italic;
      }
      button {
        margin-top: $default-margin * 0.5;
      }
    }
  }
  .markdown-hints {
    display: block;
    font-weight: normal;
  }
</style>
