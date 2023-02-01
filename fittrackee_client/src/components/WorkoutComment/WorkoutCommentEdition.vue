<template>
  <div class="add-comment">
    <form @submit.prevent="submitComment">
      <div class="form-items">
        <div class="form-item add-comment-label">
          <CustomTextArea
            class="comment"
            name="text"
            :input="commentText"
            :required="true"
            :placeholder="$t('workouts.COMMENTS.ADD')"
            @updateValue="updateText"
          />
        </div>
      </div>
      <div class="form-select-buttons">
        <div class="form-item text-visibility" v-if="!comment">
          <label> {{ $t('privacy.VISIBILITY') }}: </label>
          <select
            id="text_visibility"
            v-model="commentTextVisibility"
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
        <button class="cancel" @click.prevent="onCancel">
          {{ $t('buttons.CANCEL') }}
        </button>
      </div>
      <ErrorMessage :message="errorMessages" v-if="errorMessages"/>
    </form>
  </div>
</template>

<script setup lang="ts">
  import { ComputedRef, Ref, computed, ref, toRefs } from 'vue'

  import { ROOT_STORE, WORKOUTS_STORE } from "@/store/constants"
  import { TAppConfig } from "@/types/application"
  import { TPrivacyLevels } from "@/types/user";
  import { IComment, ICommentForm, IWorkout } from "@/types/workouts"
  import { useStore } from "@/use/useStore"
  import { getPrivacyLevels, getPrivacyLevelForLabel } from "@/utils/privacy"

  interface Props {
    workout: IWorkout
    comment?: IComment | null
    replyTo?: string | null
  }

  const props = withDefaults(defineProps<Props>(), {
    comment: null,
    replyTo: null,
  })
  const { workout, comment, replyTo }  = toRefs(props)

  const store = useStore()

  const emit = defineEmits(['closeEdition'])

  const appConfig: ComputedRef<TAppConfig> = computed(
    () => store.getters[ROOT_STORE.GETTERS.APP_CONFIG]
  )
  const privacyLevels = computed(() =>
    getPrivacyLevels(appConfig.value.federation_enabled)
  )
  const commentText: Ref<string> = ref(comment?.value ? comment.value.text : '')
  const commentTextVisibility: Ref<TPrivacyLevels> = ref(comment?.value ? comment.value.text_visibility : workout.value.workout_visibility)
  const errorMessages: ComputedRef<string | string[] | null> = computed(
      () => store.getters[ROOT_STORE.GETTERS.ERROR_MESSAGES]
  )

  function updateText(value: string) {
    commentText.value = value
  }
  function onCancel() {
    updateText('')
    emit('closeEdition')
  }
  function submitComment() {
    if (comment?.value && comment.value.id) {
      const payload: ICommentForm = {
        id: comment.value.id,
        text: commentText.value,
        workout_id: workout.value.id,
      }
      store.dispatch(WORKOUTS_STORE.ACTIONS.EDIT_WORKOUT_COMMENT, payload)
      emit('closeEdition')
    } else {
      const payload: ICommentForm = {
        text: commentText.value,
        text_visibility: commentTextVisibility.value,
        workout_id: workout.value.id,
      }
      if (replyTo?.value) {
        payload.reply_to = replyTo.value
      }
      store.dispatch(WORKOUTS_STORE.ACTIONS.ADD_COMMENT, payload)
      updateText('')
    }
  }
</script>

<style scoped lang="scss">
  @import '~@/scss/vars.scss';

  .add-comment {
    margin: $default-margin * 2 0;
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
    .add-comment-label {
      font-style: italic;
    }
  }
</style>