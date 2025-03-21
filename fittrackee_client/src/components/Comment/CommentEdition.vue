<template>
  <div class="add-comment">
    <form @submit.prevent="submitComment">
      <div class="form-items">
        <div class="form-item add-comment-label">
          <label for="comment" class="visually-hidden">
            {{ $t('workouts.COMMENTS.ADD') }}
          </label>
          <CustomTextArea
            id="comment"
            class="comment"
            :name="name"
            :input="commentText"
            :required="true"
            :placeholder="$t('workouts.COMMENTS.ADD')"
            @updateValue="updateText"
          />
          <div class="markdown-hints info-box">
            <i class="fa fa-info-circle" aria-hidden="true" />
            {{ $t('workouts.MARKDOWN_SYNTAX') }}
          </div>
          <ul class="users-suggestions" v-if="matchingUsers.length > 0">
            <li
              v-for="user in matchingUsers"
              :key="user.username"
              tabindex="0"
              @click="(e) => selectUser(e, user, comment)"
              @keydown.enter="(e) => selectUser(e, user, comment)"
            >
              <UserPicture :user="user" />
              <span>{{ user.username }}</span>
            </li>
          </ul>
        </div>
      </div>
      <div class="form-select-buttons">
        <div
          class="form-item text-visibility"
          v-if="!comment && workout && workout.workout_visibility"
        >
          <label for="text_visibility">
            {{ $t('visibility_levels.VISIBILITY') }}:
          </label>
          <select id="text_visibility" v-model="commentTextVisibility">
            <option
              v-for="level in getCommentVisibilityLevels(
                workout.workout_visibility
              )"
              :value="level"
              :key="level"
            >
              {{ $t(`visibility_levels.COMMENT_LEVELS.${level}`) }}
            </option>
          </select>
        </div>
        <div class="spacer" />
        <div v-if="isLoading">
          <Loader />
        </div>
        <div class="comment-buttons" v-else>
          <button class="confirm" type="submit">
            {{ $t('buttons.SUBMIT') }}
          </button>
          <button class="cancel" @click.prevent="onCancel">
            {{ $t('buttons.CANCEL') }}
          </button>
        </div>
      </div>
      <ErrorMessage :message="errorMessages" v-if="errorMessages" />
    </form>
  </div>
</template>

<script setup lang="ts">
  import { computed, onUnmounted, ref, toRefs } from 'vue'
  import type { ComputedRef, Ref } from 'vue'

  import UserPicture from '@/components/User/UserPicture.vue'
  import useApp from '@/composables/useApp'
  import { USERS_STORE, WORKOUTS_STORE } from '@/store/constants'
  import type { ICustomTextareaData } from '@/types/forms'
  import type {
    IAuthUserProfile,
    IUserLightProfile,
    IUserProfile,
    TVisibilityLevels,
  } from '@/types/user'
  import type { IComment, ICommentForm, IWorkout } from '@/types/workouts'
  import { useStore } from '@/use/useStore'
  import { getUsernameQuery, replaceUsername } from '@/utils/inputs'
  import { getCommentVisibilityLevels } from '@/utils/visibility_levels'

  interface ISuggestion {
    position: number | null
    usernameQuery: string | null
  }

  interface Props {
    workout: IWorkout | null
    commentsLoading: string | null
    authUser: IAuthUserProfile
    comment?: IComment | null
    name?: string | null
    mentions?: IUserLightProfile[]
  }
  const props = withDefaults(defineProps<Props>(), {
    comment: null,
    name: 'text',
    mentions: () => [],
  })
  const { authUser, comment, commentsLoading, mentions, name, workout } =
    toRefs(props)

  const store = useStore()

  const { errorMessages } = useApp()

  let suggestion: ISuggestion = { position: null, usernameQuery: null }

  const commentText: Ref<string> = ref(getText())
  const commentTextVisibility: Ref<TVisibilityLevels | undefined> = ref(
    comment?.value
      ? comment.value.text_visibility
      : workout.value?.workout_visibility
  )

  const isLoading: ComputedRef<boolean> = computed(() =>
    comment.value
      ? comment.value.id === commentsLoading.value
      : commentsLoading.value === 'new'
  )
  const matchingUsers: ComputedRef<IUserProfile[]> = computed(
    () => store.getters[USERS_STORE.GETTERS.USERS]
  )

  function getText(): string {
    // comment edition
    if (comment?.value) {
      return comment.value.text || ''
    }
    // comment w/ mention
    if (mentions.value.length > 0) {
      const filteredMentions = mentions.value.filter(
        (m) => m.username !== authUser.value.username
      )
      if (filteredMentions.length > 0) {
        return filteredMentions.map((m) => `@${m.username}`).join(' ') + ' '
      }
    }
    // add workout owner as mention
    if (
      workout.value?.user &&
      workout.value?.user.username !== authUser.value.username
    ) {
      return `@${workout.value?.user.username} `
    }
    // no mentions in comment
    return ''
  }
  function searchUsers(usernameQuery: string) {
    store.dispatch(USERS_STORE.ACTIONS.GET_USERS, {
      per_page: 5,
      q: usernameQuery,
      with_following: 'true',
    })
  }
  function updateText(textareaData: ICustomTextareaData) {
    commentText.value = textareaData.value
    suggestion = getUsernameQuery(textareaData)
    if (suggestion.usernameQuery) {
      searchUsers(suggestion.usernameQuery)
    } else {
      store.dispatch(USERS_STORE.ACTIONS.EMPTY_USERS)
    }
  }
  function selectUser(
    event: Event,
    user: IUserProfile,
    comment: IComment | null
  ) {
    event.preventDefault()
    event.stopPropagation()
    const textAreaId = `text${comment ? `-${comment.id}` : ''}`
    if (suggestion.position !== null && suggestion.usernameQuery) {
      const updatedText = replaceUsername(
        commentText.value,
        suggestion.position,
        suggestion.usernameQuery,
        user.username
      )
      const element: HTMLElement | null = document.getElementById(textAreaId)
      if (element && element instanceof HTMLTextAreaElement) {
        element.value = updatedText
        element.focus()
        element.selectionStart = updatedText.length
        commentText.value = updatedText
      }
    }
    store.dispatch(USERS_STORE.ACTIONS.EMPTY_USERS)
  }
  function onCancel() {
    updateText({ value: '', selectionStart: 0 })
    store.commit(WORKOUTS_STORE.MUTATIONS.SET_CURRENT_COMMENT_EDITION, {})
  }
  function submitComment() {
    if (workout.value) {
      if (comment?.value && comment.value.id) {
        const payload: ICommentForm = {
          id: comment.value.id,
          text: commentText.value,
          workout_id: workout.value.id,
        }
        store.dispatch(WORKOUTS_STORE.ACTIONS.EDIT_WORKOUT_COMMENT, payload)
      } else {
        const payload: ICommentForm = {
          text: commentText.value,
          text_visibility: commentTextVisibility.value,
          workout_id: workout.value.id,
        }
        store.dispatch(WORKOUTS_STORE.ACTIONS.ADD_COMMENT, payload)
        updateText({ value: '', selectionStart: 0 })
      }
    }
  }

  onUnmounted(() => {
    store.dispatch(USERS_STORE.ACTIONS.EMPTY_USERS)
  })
</script>

<style scoped lang="scss">
  @use '~@/scss/vars.scss' as *;

  .add-comment {
    margin: $default-margin * 2 0;
    .comment {
      padding: $default-padding 0 0;
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
      flex-wrap: wrap;
      gap: $default-padding;
      align-items: center;
      padding-top: $default-padding * 0.5;
      select {
        padding: $default-padding * 0.5 $default-padding;
      }
    }
    .add-comment-label {
      font-style: italic;
      position: relative;

      .users-suggestions {
        list-style-type: none;
        background-color: var(--user-suggestion-background);
        margin-top: 0;
        padding: 0;
        border: 1px solid var(--input-border-color);
        border-radius: $border-radius;
        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.25);
        max-width: 200px;
        top: 30px;

        li {
          display: flex;
          gap: $default-padding;
          padding: $default-padding;

          ::v-deep(.user-picture) {
            min-width: min-content;
            align-items: flex-start;
            img {
              height: 25px;
              width: 25px;
            }
            .no-picture {
              font-size: 1.5em;
            }
          }

          &:hover,
          &:focus {
            background-color: var(--dropdown-hover-color);
            font-weight: bold;
            cursor: pointer;

            ::v-deep(.user-picture) {
              background-color: var(--dropdown-hover-color);
            }
          }
        }
      }
    }
    .comment-buttons {
      display: flex;
      gap: $default-padding;
    }
    .loader {
      border-width: 5px;
      height: 15px;
      margin: 0 10px;
      width: 15px;
    }
  }
</style>
