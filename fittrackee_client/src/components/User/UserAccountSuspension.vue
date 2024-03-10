<template>
  <div v-if="loading && !appealText">
    <Loader />
  </div>
  <div id="suspension-appeal" v-else>
    <div v-if="accountSuspension.id" class="description-list">
      <dl v-if="accountSuspension.note">
        <dt>{{ $t('user.SUSPENSION_REASON') }}:</dt>
        <dd>{{ accountSuspension.note }}</dd>
      </dl>
      <div
        v-if="isSuccess || accountSuspension.appeal"
        class="appeal-submitted"
      >
        <div
          class="info-box"
          :class="{ 'success-message': isSuccess, 'appeal-success': isSuccess }"
        >
          <span>
            <i class="fa fa-info-circle" aria-hidden="true" />
            {{ $t(`user.APPEAL_${isSuccess ? 'SUBMITTED' : 'IN_PROGRESS'}`) }}
          </span>
        </div>
        <div>
          <button @click="$router.push('/profile')">
            {{ $t('user.PROFILE.BACK_TO_PROFILE') }}
          </button>
        </div>
      </div>
      <form v-else @submit.prevent="submitAppeal">
        <div class="form-items">
          <div class="form-item">
            <label for="appeal">{{ $t('user.APPEAL') }}:</label>
            <CustomTextArea
              name="appeal"
              :required="true"
              @updateValue="updateText"
            />
            <div class="info-box appeal-info">
              <span>
                <i class="fa fa-info-circle" aria-hidden="true" />
                {{ $t('user.YOU_CAN_APPEAL_ONCE') }}
              </span>
            </div>
          </div>
        </div>
        <div class="form-select-buttons">
          <div v-if="loading && appealText">
            <Loader />
          </div>
          <div class="report-buttons" v-else>
            <button class="confirm" type="submit" :disabled="!appealText">
              {{ $t('buttons.SUBMIT') }}
            </button>
            <button @click="$router.push('/profile')">
              {{ $t('user.PROFILE.BACK_TO_PROFILE') }}
            </button>
          </div>
        </div>
        <ErrorMessage :message="errorMessages" v-if="errorMessages" />
      </form>
    </div>
    <div v-else>{{ $t('user.ACTIVE_ACCOUNT') }}</div>
  </div>
</template>

<script setup lang="ts">
  import { computed, onMounted, onUnmounted, ref } from 'vue'
  import type { ComputedRef, Ref } from 'vue'

  import { AUTH_USER_STORE, ROOT_STORE } from '@/store/constants'
  import type { ICustomTextareaData } from '@/types/forms'
  import type { IAccountSuspension } from '@/types/user'
  import { useStore } from '@/use/useStore'

  const store = useStore()

  const loading = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.USER_LOADING]
  )
  const accountSuspension: ComputedRef<IAccountSuspension> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.ACCOUNT_SUSPENSION]
  )
  const errorMessages: ComputedRef<string | string[] | null> = computed(
    () => store.getters[ROOT_STORE.GETTERS.ERROR_MESSAGES]
  )
  const appealText: Ref<string> = ref('')
  const isSuccess: ComputedRef<boolean> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.IS_SUCCESS]
  )

  onMounted(() => loadUserSuspension())

  function loadUserSuspension() {
    store.dispatch(AUTH_USER_STORE.ACTIONS.GET_ACCOUNT_SUSPENSION)
  }
  function updateText(textareaData: ICustomTextareaData) {
    appealText.value = textareaData.value
  }
  function submitAppeal() {
    store.dispatch(AUTH_USER_STORE.ACTIONS.APPEAL, appealText.value)
  }

  onUnmounted(() =>
    store.commit(AUTH_USER_STORE.MUTATIONS.UPDATE_IS_SUCCESS, false)
  )
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars';

  #suspension-appeal {
    .error-message,
    .appeal-info {
      margin: $default-margin 0;
    }

    .appeal-submitted {
      display: flex;
      flex-direction: column;
      gap: $default-padding;

      .appeal-success {
        margin: 0;
      }
    }
    .report-buttons {
      display: flex;
      gap: $default-padding;
    }
  }
</style>
