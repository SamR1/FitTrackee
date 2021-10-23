<template>
  <div class="custom-textarea">
    <textarea
      :id="name"
      :name="name"
      :maxLenght="charLimit"
      :disabled="disabled"
      v-model="text"
      @input="updateText"
    />
    <div class="remaining-chars">
      {{ $t('workouts.REMAINING_CHARS') }}: {{ text.length }}/{{ charLimit }}
    </div>
  </div>
</template>

<script lang="ts">
  import { defineComponent, ref, watch } from 'vue'

  export default defineComponent({
    name: 'CustomTextArea',
    props: {
      charLimit: {
        type: Number,
        default: 500,
      },
      disabled: {
        type: Boolean,
        default: false,
      },
      input: {
        type: String,
        default: '',
      },
      name: {
        type: String,
        required: true,
      },
    },
    emits: ['updateValue'],
    setup(props, { emit }) {
      let text = ref('')

      function updateText(event: Event & { target: HTMLInputElement }) {
        emit('updateValue', event.target.value)
      }

      watch(
        () => props.input,
        (value) => {
          text.value = value
        }
      )

      return { text, updateText }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base.scss';
  .custom-textarea {
    display: flex;
    flex-direction: column;
    .remaining-chars {
      font-size: 0.8em;
      font-style: italic;
    }
  }
</style>
