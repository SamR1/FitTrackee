<template>
  <div id="user-picture-edition">
    <div class="user-picture-form">
      <ErrorMessage :message="errorMessages" v-if="errorMessages" />
      <UserPicture :user="user" />
      <form @submit.prevent="updateUserPicture">
        <input
          type="file"
          name="picture"
          accept=".png,.jpg,.gif"
          @input="updatePictureFile"
        />
        <div class="picture-help">
          <span class="info-box">
            <i class="fa fa-info-circle" aria-hidden="true" />
            {{ $t('workouts.MAX_SIZE') }}: {{ fileSizeLimit }}
          </span>
        </div>
        <div class="picture-buttons">
          <button type="submit" :disabled="!pictureFile">
            {{ $t('user.PROFILE.PICTURE_UPDATE') }}
          </button>
          <button class="danger" v-if="user.picture" @click="deleteUserPicture">
            {{ $t('user.PROFILE.PICTURE_REMOVE') }}
          </button>
          <button class="cancel" @click="$router.push('/profile')">
            {{ $t('user.PROFILE.BACK_TO_PROFILE') }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { computed, ref, toRefs } from 'vue'
  import type { ComputedRef, Ref } from 'vue'

  import UserPicture from '@/components/User/UserPicture.vue'
  import useApp from '@/composables/useApp'
  import { AUTH_USER_STORE } from '@/store/constants'
  import type { IUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { getReadableFileSizeAsText } from '@/utils/files'

  interface Props {
    user: IUserProfile
  }
  const props = defineProps<Props>()
  const { user } = toRefs(props)

  const store = useStore()

  const { appConfig, errorMessages } = useApp()

  const pictureFile: Ref<File | null> = ref(null)

  const fileSizeLimit: ComputedRef<string> = computed(() =>
    appConfig.value.max_single_file_size
      ? getReadableFileSizeAsText(appConfig.value.max_single_file_size)
      : ''
  )

  function deleteUserPicture() {
    store.dispatch(AUTH_USER_STORE.ACTIONS.DELETE_PICTURE)
  }
  function updatePictureFile(event: Event) {
    if ((event.target as HTMLInputElement).files !== null) {
      pictureFile.value = (
        (event.target as HTMLInputElement).files as FileList
      )[0]
    }
  }
  function updateUserPicture() {
    if (pictureFile.value) {
      store.dispatch(AUTH_USER_STORE.ACTIONS.UPDATE_USER_PICTURE, {
        picture: pictureFile.value,
      })
    }
  }
</script>

<style lang="scss" scoped>
  @use '~@/scss/vars.scss' as *;

  #user-picture-edition {
    padding: $default-padding 0;
    .user-picture-form {
      display: flex;
      flex-direction: column;
      margin-top: $default-margin;

      form {
        display: flex;
        flex-direction: column;
        gap: $default-padding;
        justify-content: flex-start;

        input {
          margin-top: $default-margin;
          padding: $default-padding * 0.5;
        }

        span {
          font-style: italic;
          font-size: 0.9em;
          padding-left: $default-padding * 0.5;
        }

        .picture-help {
          display: flex;
          span {
            font-style: italic;
            padding: $default-padding;
          }
          .fa-info-circle {
            margin-right: $default-margin;
          }
        }
      }
      .picture-buttons {
        display: flex;
        flex-direction: row;
        align-items: center;
        gap: $default-padding;
      }

      .picture-buttons,
      .picture-help {
        @media screen and (max-width: $x-small-limit) {
          flex-direction: column;
          align-items: stretch;
        }
      }
    }
  }
</style>
