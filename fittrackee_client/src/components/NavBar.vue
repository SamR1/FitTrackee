<template>
  <div id="nav">
    <div class="nav-container">
      <div class="nav-app-name">
        <router-link class="nav-item app-name" to="/">FitTrackee</router-link>
      </div>
      <div class="nav-icon-open" :class="{ 'menu-open': isMenuOpen }">
        <i class="fa fa-bars hamburger-icon" @click="openMenu()"></i>
      </div>
      <div class="nav-items" :class="{ 'menu-open': isMenuOpen }">
        <div class="nav-items-close">
          <div class="app-name">FitTrackee</div>
          <i
            class="fa fa-close close-icon nav-item"
            :class="{ 'menu-closed': !isMenuOpen }"
            @click="closeMenu()"
          />
        </div>
        <div class="nav-items-app-menu" @click="closeMenu()">
          <div class="nav-items-group" v-if="isAuthenticated">
            <router-link class="nav-item" to="/">
              {{ $t('dashboard.DASHBOARD') }}
            </router-link>
            <router-link class="nav-item" to="/workouts">
              {{ capitalize($t('workouts.WORKOUT', 2)) }}
            </router-link>
            <router-link class="nav-item" to="/statistics">
              {{ $t('statistics.STATISTICS') }}
            </router-link>
            <router-link class="nav-item" to="/workouts/add">
              {{ $t('workouts.ADD_WORKOUT') }}
            </router-link>
            <router-link
              class="nav-item"
              v-if="isAuthenticated && authUser.admin"
              to="/admin"
            >
              {{ $t('admin.ADMIN') }}
            </router-link>
            <div class="nav-item nav-separator" />
          </div>
        </div>
        <div class="nav-items-user-menu">
          <div class="nav-items-group" v-if="isAuthenticated">
            <div class="nav-item nav-profile-img">
              <UserPicture :user="authUser" />
            </div>
            <router-link class="nav-item" to="/profile" @click="closeMenu">
              {{ authUser.username }}
            </router-link>
            <div class="nav-item nav-link" @click="logout">
              {{ $t('user.LOGOUT') }}
            </div>
          </div>
          <div class="nav-items-group" v-else>
            <router-link class="nav-item" to="/login" @click="closeMenu">
              {{ $t('user.LOGIN') }}
            </router-link>
            <router-link class="nav-item" to="/register" @click="closeMenu">
              {{ $t('user.REGISTER') }}
            </router-link>
          </div>
          <Dropdown
            v-if="availableLanguages && language"
            class="nav-item"
            :options="availableLanguages"
            :selected="language"
            @selected="updateLanguage"
          >
            <i class="fa fa-language"></i>
          </Dropdown>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ComputedRef, computed, ref, capitalize } from 'vue'

  import UserPicture from '@/components/User/UserPicture.vue'
  import { AUTH_USER_STORE, ROOT_STORE } from '@/store/constants'
  import { IDropdownOption } from '@/types/forms'
  import { IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { availableLanguages } from '@/utils/locales'

  const emit = defineEmits(['menuInteraction'])

  const store = useStore()

  const authUser: ComputedRef<IAuthUserProfile> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.AUTH_USER_PROFILE]
  )
  const isAuthenticated: ComputedRef<boolean> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.IS_AUTHENTICATED]
  )
  const language: ComputedRef<string> = computed(
    () => store.getters[ROOT_STORE.GETTERS.LANGUAGE]
  )
  const isMenuOpen = ref(false)

  function openMenu() {
    isMenuOpen.value = true
    emit('menuInteraction', true)
  }
  function closeMenu() {
    isMenuOpen.value = false
    emit('menuInteraction', false)
  }
  function updateLanguage(option: IDropdownOption) {
    store.dispatch(
      ROOT_STORE.ACTIONS.UPDATE_APPLICATION_LANGUAGE,
      option.value.toString()
    )
  }
  function logout() {
    store.dispatch(AUTH_USER_STORE.ACTIONS.LOGOUT)
  }
</script>

<style scoped lang="scss">
  @import '~@/scss/fonts.scss';
  @import '~@/scss/colors.scss';
  @import '~@/scss/vars.scss';

  #nav {
    background: var(--nav-bar-background-color);
    display: flex;
    padding: 15px 10px;

    .nav-container {
      display: flex;

      margin-left: auto;
      margin-right: auto;
      padding: 0 15px 15px 15px;
      max-width: $container-width;
      width: 100%;

      border-bottom: solid 1px var(--nav-border-color);
    }

    a {
      &.router-link-exact-active {
        color: var(--nav-bar-link-active);
        font-weight: bold;
      }
    }

    .app-name {
      font-size: 1.2em;
      font-weight: bold;
      margin-right: 10px;
    }

    .fa {
      font-size: 1.2em;
    }

    .nav-icon-open {
      display: none;
    }

    .hamburger-icon,
    .close-icon {
      display: none;
    }

    .nav-items {
      display: flex;
      flex: 1;
      justify-content: space-between;
      line-height: 1.8em;
      width: 100%;

      .nav-items-close {
        display: none;
      }

      .nav-items-app-menu,
      .nav-items-user-menu {
        display: flex;
        margin: 0;
        padding: 0;
      }

      .nav-items-group {
        display: flex;
      }
      .nav-item {
        padding: 0 10px;

        ::v-deep(.dropdown-list) {
          z-index: 1000;
          margin-left: -160px !important;
          width: 180px !important;
        }
      }

      .nav-link {
        color: var(--app-a-color);
        cursor: pointer;
      }

      .nav-profile-img {
        margin-bottom: -$default-padding;
        ::v-deep(.user-picture) {
          img {
            height: 32px;
            width: 32px;
            object-fit: cover;
          }
          .no-picture {
            font-size: 1.7em;
          }
        }
      }

      .nav-separator {
        display: none;
      }
    }

    @media screen and (max-width: $medium-limit) {
      .hamburger-icon {
        display: block;
      }
      .nav-icon-open {
        display: block;
        text-align: right;
        width: 100%;
      }
      .nav-icon-open.menu-open {
        display: none;
      }

      .close-icon {
        display: block;
      }
      .close-icon.menu-closed {
        display: none;
      }

      .nav-items {
        display: none;
      }
      .nav-items.menu-open {
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        z-index: 1001;

        position: absolute;
        top: 0;
        right: 0;
        bottom: 0;
        left: 0;

        background: var(--nav-bar-background-color);

        .nav-items-close,
        .nav-items-app-menu,
        .nav-items-user-menu {
          display: flex;
          flex-direction: column;
        }

        .nav-items-close {
          align-items: center;
          display: flex;
          flex-direction: row;
          justify-content: space-between;

          .app-name {
            padding: 15px 25px;
          }
        }

        .nav-items-group {
          display: flex;
          flex-direction: column;
        }

        .nav-item {
          padding: 7px 25px;

          ::v-deep(.dropdown-list) {
            margin-left: initial !important;
            width: auto !important;
          }
        }

        .nav-profile-img {
          display: none;
        }

        .nav-separator {
          display: flex;
          border-top: solid 1px var(--nav-border-color);
          margin: 0 $default-margin * 2;
          padding: 0;
        }
      }

      .nav-items-user-menu :nth-child(1) {
        order: 1;
      }
    }
  }
</style>
