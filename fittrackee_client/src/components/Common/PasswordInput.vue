<template>
  <div class="password-input">
    <input
      :id="id"
      :disabled="disabled"
      :placeholder="placeholder"
      :required="required"
      :type="showPassword ? 'text' : 'password'"
      v-model="passwordValue"
      minlength="8"
      @input="updatePassword"
      @invalid="invalidPassword"
      :autocomplete="autocomplete"
    />
    <div class="show-password">
      <button class="transparent" @click.prevent="togglePassword" type="button">
        {{ $t(`user.${showPassword ? 'HIDE' : 'SHOW'}_PASSWORD`) }}
        <i
          class="fa"
          :class="`fa-eye${showPassword ? '-slash' : ''}`"
          aria-hidden="true"
        />
      </button>
    </div>
    <div v-if="checkStrength" class="form-info">
      <i class="fa fa-info-circle" aria-hidden="true" />
      {{ $t('user.PASSWORD_INFO') }}
    </div>
    <PasswordStrength v-if="checkStrength" :password="passwordValue" />
  </div>
</template>

<script setup lang="ts">
  import { ref, toRefs, watch } from 'vue'
  import type { Ref } from 'vue'

  import PasswordStrength from '@/components/Common/PasswordStength.vue'

  interface Props {
    checkStrength?: boolean
    disabled?: boolean
    id?: string
    password?: string
    placeholder?: string
    required?: boolean
    autocomplete: string
  }
  const props = withDefaults(defineProps<Props>(), {
    checkStrength: false,
    disabled: false,
    id: 'password',
    password: '',
    required: false,
  })
  const {
    autocomplete,
    checkStrength,
    disabled,
    id,
    password,
    placeholder,
    required,
  } = toRefs(props)

  const emit = defineEmits(['updatePassword', 'passwordError'])

  const showPassword: Ref<boolean> = ref(false)
  const passwordValue: Ref<string> = ref('')

  function togglePassword() {
    showPassword.value = !showPassword.value
  }
  function updatePassword(event: Event) {
    emit('updatePassword', (event.target as HTMLInputElement).value)
  }
  function invalidPassword() {
    emit('passwordError')
  }

  watch(
    () => password.value,
    (newPassword) => {
      if (newPassword === '') {
        passwordValue.value = ''
        showPassword.value = false
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
      margin-top: -0.5 * $default-margin;
      display: flex;
      justify-content: right;
      button {
        font-style: italic;
        font-size: 0.85em;
        padding: $default-padding * 0.5 $default-padding;
        cursor: pointer;
      }
    }
  }
</style>
