<template>
  <div class="add-comment">
    <form :class="{ errors: formErrors }" @submit.prevent="submitComment">
      <div class="form-items">
        <div class="form-item">
          <label> {{ $t('workouts.COMMENTS.ADD') }}: </label>
          <CustomTextArea
              class="comment"
              name="text"
              :value="commentForm.text"
              @updateValue="updateText"
          />
        </div>
      </div>
      <div class="form-select-buttons">
        <div class="form-item text-visibility">
          <label> {{ $t('privacy.VISIBILITY') }}: </label>
          <select
            id="text_visibility"
            v-model="commentForm.textVisibility"
          >
            <option
              v-for="level in privacyLevels"
              :value="level"
              :key="level"
            >
              {{
                $t(
                  `privacy.LEVELS.${getPrivacyLevelForLabel(
                    level,
                    appConfig.federation_enabled
                  )}`
                )
              }}
            </option>
          </select>
        </div>
        <div class="spacer" />
        <button class="confirm" type="submit">
          {{ $t('buttons.SUBMIT') }}
        </button>
        <button class="cancel">
          {{ $t('buttons.CANCEL') }}
        </button>
      </div>
      <ErrorMessage :message="errorMessages" v-if="errorMessages"/>
    </form>
  </div>
</template>

<script setup lang="ts">
  import { ComputedRef, computed, reactive, ref, toRefs } from 'vue'

  import { ROOT_STORE, WORKOUTS_STORE } from "@/store/constants"
  import { TAppConfig } from "@/types/application"
  import { ICommentForm, IWorkout } from "@/types/workouts"
  import { useStore } from "@/use/useStore"
  import { getPrivacyLevels, getPrivacyLevelForLabel } from "@/utils/privacy"

  interface Props {
    workout: IWorkout
  }

  const props = defineProps<Props>()
  const { workout }  = toRefs(props)

  const store = useStore()

  const appConfig: ComputedRef<TAppConfig> = computed(
    () => store.getters[ROOT_STORE.GETTERS.APP_CONFIG]
  )
  const privacyLevels = computed(() =>
    getPrivacyLevels(appConfig.value.federation_enabled)
  )
  const commentForm = reactive({
    text: '',
    textVisibility: workout.value.workout_visibility,
  })
  const errorMessages: ComputedRef<string | string[] | null> = computed(
      () => store.getters[ROOT_STORE.GETTERS.ERROR_MESSAGES]
  )
  const formErrors = ref(false)

  function updateText(value: string) {
    commentForm.text = value
  }
  function submitComment() {
    const payload: ICommentForm = {
      text: commentForm.text,
      textVisibility: commentForm.textVisibility,
      workoutId: workout.value.id,
    }
    store.dispatch(WORKOUTS_STORE.ACTIONS.ADD_COMMENT, payload)
  }
</script>

<style scoped lang="scss">
  @import '~@/scss/vars.scss';

  .add-comment {
    margin-top: $default-margin;
    .comment {
      padding: $default-padding 0;
    }
    .form-select-buttons {
      display: flex;
      gap: $default-padding;
      flex-wrap: wrap;
      .spacer {
        flex-grow: 3;
      }
    }
    .text-visibility {
      display: flex;
      gap: $default-padding;
      align-items: center;
      padding-top: $default-padding * 0.5;
      select {
        padding: $default-padding * 0.5 $default-padding;
      }
    }
  }
</style>