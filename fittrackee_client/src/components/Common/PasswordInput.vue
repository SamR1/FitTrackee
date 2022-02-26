<template>
  <div class="password-input">
    <input
      :disabled="disabled"
      :placeholder="placeholder"
      :required="required"
      :type="showPassword ? 'text' : 'password'"
      v-model="passwordValue"
      minlength="8"
      @input="updatePassword"
      @invalid="invalidPassword"
    />
    <div class="show-password" @click="togglePassword">
      {{ $t(`user.${showPassword ? 'HIDE' : 'SHOW'}_PASSWORD`) }}
      <i
        class="fa"
        :class="`fa-eye${showPassword ? '-slash' : ''}`"
        aria-hidden="true"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
  import { Ref, ref, toRefs, watch, withDefaults } from 'vue'

  interface Props {
    disabled?: boolean
    password?: string
    placeholder?: string
    required?: boolean
  }

  const props = withDefaults(defineProps<Props>(), {
    disabled: false,
    required: false,
  })
  const { disabled, password, placeholder, required } = toRefs(props)

  const showPassword: Ref<boolean> = ref(false)
  const passwordValue: Ref<string> = ref('')

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

  watch(
    () => password.value,
    (newPassword) => {
      if (newPassword === '') {
        passwordValue.value = ''
      }
    }
  )
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';

  .password-input {
    display: flex;
    flex-direction: column;

    .show-password {
      font-style: italic;
      font-size: 0.85em;
      text-align: right;
      margin-top: -0.75 * $default-margin;
      padding-right: $default-padding;
      cursor: pointer;
    }
  }
</style>
