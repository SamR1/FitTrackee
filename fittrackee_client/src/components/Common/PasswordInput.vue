<template>
  <div class="password-input">
    <input
      :disabled="disabled"
      :placeholder="placeholder"
      :required="required"
      :type="showPassword ? 'text' : 'password'"
      minlength="8"
      @input="updatePassword"
      @invalid="invalidPassword"
    />
    <span class="show-password" @click="togglePassword">
      {{ $t(`user.${showPassword ? 'HIDE' : 'SHOW'}_PASSWORD`) }}
    </span>
  </div>
</template>

<script setup lang="ts">
  import { ref, toRefs, withDefaults } from 'vue'
  interface Props {
    disabled?: boolean
    placeholder?: string
    required?: boolean
  }

  const props = withDefaults(defineProps<Props>(), {
    disabled: false,
    required: false,
  })
  const { disabled, placeholder, required } = toRefs(props)
  const showPassword = ref(false)

  const emit = defineEmits(['updatePassword', 'passwordError'])

  function togglePassword() {
    showPassword.value = !showPassword.value
  }
  function updatePassword(event: Event & { target: HTMLInputElement }) {
    emit('updatePassword', event.target.value)
  }
  function invalidPassword() {
    emit('passwordError')
  }
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';

  .password-input {
    display: flex;
    flex-direction: column;
    .show-password {
      font-style: italic;
      font-size: 0.85em;
      margin-top: -0.75 * $default-margin;
      padding-left: $default-padding;
      cursor: pointer;
    }
  }
</style>
