<template>
  <div class="custom-textarea">
    <textarea
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
    <div class="remaining-chars">
      {{ $t('workouts.REMAINING_CHARS') }}: {{ text.length }}/{{ charLimit }}
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ref, toRefs, watch } from 'vue'

  interface Props {
    name: string
    charLimit?: number
    disabled?: boolean
    input?: string | null
    rows?: number
    required?: boolean
    placeholder?: string
  }
  const props = withDefaults(defineProps<Props>(), {
    charLimit: 500,
    disabled: false,
    input: '',
    rows: 2,
    required: false,
    placeholder: '',
  })

  const emit = defineEmits(['updateValue'])

  const { input } = toRefs(props)
  const text = ref(input.value ? input.value : '')

  function updateText(event: Event) {
    const target = event.target as HTMLInputElement
    emit('updateValue', {
      value: target.value,
      selectionStart: target.selectionStart,
    })
  }

  watch(
    () => props.input,
    (value) => {
      text.value = value === null ? '' : value
    }
  )
</script>

<style lang="scss" scoped>
  .custom-textarea {
    display: flex;
    flex-direction: column;
    .remaining-chars {
      font-size: 0.8em;
      font-style: italic;
    }
  }
</style>
