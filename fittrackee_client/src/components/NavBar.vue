<template>
  <header id="nav">
    <Modal
      v-if="displayModal"
      :title="$t('common.CONFIRMATION')"
      :message="$t('user.LOGOUT_CONFIRMATION')"
      @confirmAction="logout"
      @cancelAction="updateDisplayModal(false)"
      @keydown.esc="updateDisplayModal(false)"
    />
    <div class="nav-container">
      <div class="nav-app-name">
        <div class="nav-item app-name">FitTrackee</div>
      </div>
      <div class="nav-icon-open" :class="{ 'menu-open': isMenuOpen }">
        <button class="menu-button transparent" @click="openMenu()">
          <i class="fa fa-bars hamburger-icon"></i>
        </button>
      </div>
      <div class="nav-items" :class="{ 'menu-open': isMenuOpen }">
        <div class="nav-items-close">
          <div class="app-name">FitTrackee</div>
          <button class="menu-button transparent" @click="closeMenu()">
            <i
              class="fa fa-close close-icon nav-item"
              :class="{ 'menu-closed': !isMenuOpen }"
            />
          </button>
        </div>
        <div class="nav-items-app-menu" @click="closeMenu()">
          <div class="nav-items-group" v-if="isAuthenticated && !isSuspended">
            <router-link class="nav-item" to="/">
              {{ $t('dashboard.DASHBOARD') }}
            </router-link>
            <router-link class="nav-item" to="/workouts">
              {{ capitalize($t('workouts.WORKOUT', 2)) }}
            </router-link>
            <router-link class="nav-item" to="/statistics">
              {{ $t('statistics.STATISTICS') }}
            </router-link>
            <router-link class="nav-item" to="/users">
              {{ capitalize($t('user.USER', 0)) }}
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
            <router-link
              class="nav-item nav-profile-img"
              to="/profile"
              @click="closeMenu"
              :title="authUser.username"
            >
              <UserPicture :user="authUser" />
              <span class="user-name">{{ authUser.username }}</span>
            </router-link>
            <router-link
              v-if="!isSuspended"
              class="nav-item nav-profile-img notifications"
              to="/notifications?status=unread"
              @click="closeMenu"
            >
              <i
                class="notifications-icons"
                :class="`fa fa-bell${
                  hasUnreadNotifications ? '-ringing' : ''
                }-o`"
                aria-hidden="true"
              />
              <span class="notifications-label">
                {{ capitalize($t('notifications.NOTIFICATIONS', 0)) }}
              </span>
            </router-link>
            <button
              class="nav-button logout-button transparent"
              @click="updateDisplayModal(true)"
              :title="$t('user.LOGOUT')"
            >
              <i class="fa fa-sign-out nav-button-fa" aria-hidden="true" />
              <span class="nav-button-text">{{ $t('user.LOGOUT') }}</span>
            </button>
          </div>
          <div class="nav-items-group" v-else>
            <router-link class="nav-item" to="/login" @click="closeMenu">
              {{ $t('user.LOGIN') }}
            </router-link>
            <router-link class="nav-item" to="/register" @click="closeMenu">
              {{ $t('user.REGISTER') }}
            </router-link>
          </div>
          <div class="theme-button">
            <button
              class="nav-button transparent"
              @click="toggleTheme"
              :title="$t('user.TOGGLE_THEME')"
            >
              <i
                v-if="darkTheme"
                class="fa nav-button-fa fa-moon"
                aria-hidden="true"
              />
              <img
                v-else
                class="clear-theme"
                src="/img/weather/clear-day.svg"
                alt=""
                aria-hidden="true"
              />
              <span class="nav-button-text">{{ $t('user.TOGGLE_THEME') }}</span>
            </button>
          </div>
          <Dropdown
            v-if="availableLanguages && language"
            class="nav-item"
            :options="availableLanguages"
            :selected="language"
            @selected="updateLanguage"
            :buttonLabel="$t('user.LANGUAGE')"
          >
            <i class="fa fa-language"></i>
          </Dropdown>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
  import { computed, ref, capitalize, onBeforeMount, watch } from 'vue'
  import type { ComputedRef, Ref } from 'vue'

  import UserPicture from '@/components/User/UserPicture.vue'
  import {
    AUTH_USER_STORE,
    NOTIFICATIONS_STORE,
    ROOT_STORE,
  } from '@/store/constants'
  import type { IDropdownOption } from '@/types/forms'
  import type { TLanguage } from '@/types/locales'
  import type { IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { getDarkTheme } from '@/utils'
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
  const isMenuOpen: Ref<boolean> = ref(false)
  const displayModal: Ref<boolean> = ref(false)
  const darkMode: ComputedRef<boolean | null> = computed(
    () => store.getters[ROOT_STORE.GETTERS.DARK_MODE]
  )
  const darkTheme: ComputedRef<boolean> = computed(() =>
    getDarkTheme(darkMode.value)
  )
  const hasUnreadNotifications: ComputedRef<boolean> = computed(
    () => store.getters[NOTIFICATIONS_STORE.GETTERS.UNREAD_STATUS]
  )
  const isSuspended: ComputedRef<boolean> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.IS_SUSPENDED]
  )

  onBeforeMount(() => setTheme())

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
      option.value as TLanguage
    )
  }
  function logout() {
    store.dispatch(AUTH_USER_STORE.ACTIONS.LOGOUT)
    displayModal.value = false
  }
  function updateDisplayModal(display: boolean) {
    displayModal.value = display
  }
  function setTheme() {
    if (darkTheme.value) {
      document.body.setAttribute('data-theme', 'dark')
    } else {
      document.body.removeAttribute('data-theme')
    }
  }
  function toggleTheme() {
    store.commit(ROOT_STORE.MUTATIONS.UPDATE_DARK_MODE, !darkTheme.value)
  }

  watch(
    () => darkTheme.value,
    () => {
      setTheme()
    }
  )
</script>

<style scoped lang="scss">
  @import '~@/scss/fonts.scss';
  @import '~@/scss/colors.scss';
  @import '~@/scss/vars.scss';

  #nav {
    background: var(--nav-bar-background-color);
    display: flex;
    padding: 15px 10px;

    a {
      text-decoration: none;
    }

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
      line-height: 1.6em;
    }

    .fa {
      font-size: 1.2em;
    }

    .notifications-icons {
      font-size: 1em;
      padding-top: 7px;
    }

    .nav-icon-open {
      display: none;
    }

    .hamburger-icon,
    .close-icon {
      display: none;
    }
    .menu-button {
      padding: 0;
    }

    .nav-items {
      display: flex;
      flex: 1;
      justify-content: space-between;
      line-height: 2em;
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
        align-items: flex-start;
      }
      .nav-item {
        padding: 0 10px;
        height: 28px;
        &.dropdown-wrapper {
          padding: 0;
          margin-left: 2px;
          ::v-deep(.dropdown-list) {
            z-index: 1000;
            margin-left: -150px !important;
            width: 180px !important;
          }
        }

        &.notifications {
          .notifications-label {
            display: none;
          }
        }
      }

      .nav-link {
        color: var(--app-a-color);
        cursor: pointer;
      }

      .nav-profile-img {
        display: flex;
        gap: $default-padding;
        align-items: flex-start;
        margin-bottom: -$default-padding;
        ::v-deep(.user-picture) {
          min-width: auto;
          img {
            height: 32px;
            width: 32px;
            object-fit: cover;
          }
          .no-picture {
            font-size: 1.7em;
            padding: 0;
          }
        }
        .user-name {
          max-width: 180px;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }
      }

      .nav-separator {
        display: none;
      }
      .nav-button {
        padding: $default-padding * 0.5 $default-padding * 0.75;
        margin-left: 2px;
        .nav-button-fa {
          display: block;
        }
        .nav-button-text {
          display: none;
        }
      }

      .clear-theme {
        filter: var(--workout-img-color);
        height: 20px;
        margin-bottom: -5px;
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
      .notifications-icons {
        padding: 6px 0 0 4px;
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

          .nav-button {
            padding: $default-padding $default-padding $default-padding
              $default-padding * 2.4;
            color: var(--app-a-color);
            text-align: left;
            .nav-button-fa {
              display: none;
              width: 36px;
            }
            .nav-button-text {
              display: block;
            }
          }
        }

        .nav-item {
          padding: 7px 25px;
          &.dropdown-wrapper {
            padding-left: $default-padding * 2;
            ::v-deep(.dropdown-list) {
              margin-left: initial !important;
              width: auto !important;
              height: 200px;
              overflow-y: scroll;
            }
          }
          &.notifications {
            padding-top: $default-padding;
            .notifications-label {
              display: block;
            }
          }
        }

        .nav-separator {
          display: flex;
          border-top: solid 1px var(--nav-border-color);
          margin: 0 $default-margin * 2;
          padding: 0 0 $default-padding;
          width: 88%;
        }
      }
      .theme-button {
        margin-left: $default-padding * 2;
      }
    }
    .fa-language {
      cursor: pointer;
    }
  }
</style>
