<template>
  <div id="profile" class="view" v-if="authUser.username">
    <router-view :user="authUser"></router-view>
    <div id="bottom" />
  </div>
</template>

<script setup lang="ts">
  import useAuthUser from '@/composables/useAuthUser'

  const { authUser } = useAuthUser()
</script>

<style lang="scss" scoped>
  @use '~@/scss/vars.scss' as *;
  #profile {
    display: flex;
    flex-direction: column;
    padding: 0 $default-padding 40px;

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
