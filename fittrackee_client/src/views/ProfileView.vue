<template>
  <div id="profile" class="container" v-if="authUser.username">
    <ProfileEdition :user="authUser" :tab="tab" v-if="edition" />
    <Profile :user="authUser" :tab="tab" v-else />
  </div>
</template>

<script lang="ts">
  import { computed, ComputedRef, defineComponent } from 'vue'

  import Profile from '@/components/User/ProfileDisplay/index.vue'
  import ProfileEdition from '@/components/User/ProfileEdition/index.vue'
  import { USER_STORE } from '@/store/constants'
  import { IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'

  export default defineComponent({
    name: 'ProfileView',
    components: {
      Profile,
      ProfileEdition,
    },
    props: {
      edition: {
        type: Boolean,
        required: true,
      },
      tab: {
        type: String,
        required: true,
      },
    },
    setup() {
      const store = useStore()
      const authUser: ComputedRef<IAuthUserProfile> = computed(
        () => store.getters[USER_STORE.GETTERS.AUTH_USER_PROFILE]
      )
      return {
        authUser,
      }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base.scss';
  #profile {
    display: flex;
    flex-direction: column;

    ::v-deep(.profile-form) {
      display: flex;
      flex-direction: column;

      hr {
        border-color: var(--card-border-color);
        border-width: 1px 0 0 0;
      }

      .form-items {
        display: flex;
        flex-direction: column;

        input {
          margin: $default-padding * 0.5 0;
        }

        select {
          height: 35px;
          padding: $default-padding * 0.5 0;
        }
        ::v-deep(.custom-textarea) {
          textarea {
            padding: $default-padding * 0.5;
          }
        }

        .form-item {
          display: flex;
          flex-direction: column;
          padding: $default-padding;
        }
        .birth-date {
          height: 20px;
        }
      }

      .form-buttons {
        display: flex;
        margin-top: $default-margin;
        padding: $default-padding 0;
        gap: $default-padding;
      }
    }
  }
</style>
