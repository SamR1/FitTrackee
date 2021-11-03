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
        <span>{{ $t('workouts.MAX_SIZE') }}: {{ fileSizeLimit }}</span>
      </form>
    </div>
  </div>
</template>

<script lang="ts">
  import {
    ComputedRef,
    PropType,
    Ref,
    defineComponent,
    computed,
    ref,
  } from 'vue'

  import UserPicture from '@/components/User/UserPicture.vue'
  import { AUTH_USER_STORE, ROOT_STORE } from '@/store/constants'
  import { TAppConfig } from '@/types/application'
  import { IUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { getReadableFileSize } from '@/utils/files'

  export default defineComponent({
    name: 'UserPictureEdition',
    components: {
      UserPicture,
    },
    props: {
      user: {
        type: Object as PropType<IUserProfile>,
        required: true,
      },
    },
    setup() {
      const store = useStore()
      const errorMessages: ComputedRef<string | string[] | null> = computed(
        () => store.getters[ROOT_STORE.GETTERS.ERROR_MESSAGES]
      )
      const appConfig: ComputedRef<TAppConfig> = computed(
        () => store.getters[ROOT_STORE.GETTERS.APP_CONFIG]
      )
      const fileSizeLimit = appConfig.value.max_single_file_size
        ? getReadableFileSize(appConfig.value.max_single_file_size)
        : ''
      let pictureFile: Ref<File | null> = ref(null)

      function deleteUserPicture() {
        store.dispatch(AUTH_USER_STORE.ACTIONS.DELETE_PICTURE)
      }
      function updatePictureFile(event: Event & { target: HTMLInputElement }) {
        if (event.target.files) {
          pictureFile.value = event.target.files[0]
        }
      }
      function updateUserPicture() {
        if (pictureFile.value) {
          store.dispatch(AUTH_USER_STORE.ACTIONS.UPDATE_USER_PICTURE, {
            picture: pictureFile.value,
          })
        }
      }

      return {
        errorMessages,
        fileSizeLimit,
        pictureFile,
        deleteUserPicture,
        updateUserPicture,
        updatePictureFile,
      }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base.scss';

  #user-picture-edition {
    .user-picture-form {
      display: flex;
      flex-direction: column;

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
      }
      .picture-buttons {
        display: flex;
        flex-direction: row;
        align-items: center;
        gap: $default-padding;
        @media screen and (max-width: $x-small-limit) {
          flex-direction: column;
          align-items: stretch;
        }
      }
    }
  }
</style>
