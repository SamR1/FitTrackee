<template>
  <header id="nav">
    <Modal
      v-if="displayModal"
      :title="$t('common.CONFIRMATION')"
      :message="$t('user.LOGOUT_CONFIRMATION')"
      :hide-error-message="true"
      @confirmAction="logout"
      @cancelAction="updateDisplayModal(false)"
      @keydown.esc="updateDisplayModal(false)"
    />
    <div class="nav-container">
      <div class="nav-app-name">
        <router-link class="nav-item app-name" to="/" id="fittrackee-name">
          FitTrackee
        </router-link>
      </div>
      <div class="nav-icon-open" :class="{ 'menu-open': isMenuOpen }">
        <router-link
          v-if="!isAuthUserSuspended"
          class="nav-item nav-profile-img notifications"
          to="/notifications?status=unread"
          :title="capitalize($t('notifications.NOTIFICATIONS', 0))"
          @click="closeMenu"
        >
          <i
            class="notifications-icons"
            :class="`fa fa-bell${hasUnreadNotifications ? '-ringing' : ''}-o`"
            aria-hidden="true"
          />
        </router-link>
        <button class="menu-button transparent" @click="openMenu()">
          <i class="fa fa-bars hamburger-icon"></i>
        </button>
      </div>
      <div class="nav-items" :class="{ 'menu-open': isMenuOpen }">
        <div class="nav-items-close" @click="closeMenu">
          <router-link class="nav-item app-name" to="/">
            FitTrackee
          </router-link>
          <button class="menu-button transparent" @click="closeMenu()">
            <i
              class="fa fa-close close-icon nav-item"
              :class="{ 'menu-closed': !isMenuOpen }"
            />
          </button>
        </div>
        <div class="nav-items-app-menu">
          <div
            class="nav-items-group"
            v-if="isAuthenticated && !isAuthUserSuspended"
          >
            <router-link class="nav-item" to="/" @click="closeMenu()">
              {{ $t('dashboard.DASHBOARD') }}
            </router-link>
            <router-link class="nav-item" to="/workouts" @click="closeMenu()">
              {{ capitalize($t('workouts.WORKOUT', 2)) }}
            </router-link>
            <router-link class="nav-item" to="/statistics" @click="closeMenu()">
              {{ $t('statistics.STATISTICS') }}
            </router-link>
            <router-link class="nav-item" to="/users" @click="closeMenu()">
              {{ capitalize($t('user.USER', 0)) }}
            </router-link>
            <router-link
              class="nav-item"
              to="/workouts/add"
              @click="closeMenu()"
            >
              {{ $t('workouts.ADD_WORKOUT') }}
            </router-link>
            <router-link
              class="nav-item"
              v-if="authUserHasModeratorRights"
              to="/admin"
              @click="closeMenu()"
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
              v-if="!isAuthUserSuspended"
              class="nav-item nav-profile-img notifications"
              to="/notifications?status=unread"
              :title="capitalize($t('notifications.NOTIFICATIONS', 0))"
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
            v-if="availableLanguages && appLanguage"
            class="nav-item"
            :options="availableLanguages"
            :selected="appLanguage"
            @selected="updateLanguage"
            :buttonLabel="$t('user.LANGUAGE')"
            :listLabel="$t('user.LANGUAGE', 0)"
            :isMenuOpen="isMenuOpen"
          >
            <i class="fa fa-language" aria-hidden="true"></i>
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
  import useApp from '@/composables/useApp'
  import useAuthUser from '@/composables/useAuthUser'
  import {
    AUTH_USER_STORE,
    NOTIFICATIONS_STORE,
    ROOT_STORE,
  } from '@/store/constants'
  import type { IDropdownOption } from '@/types/forms'
  import type { TLanguage } from '@/types/locales'
  import { useStore } from '@/use/useStore'
  import { availableLanguages } from '@/utils/locales'

  const emit = defineEmits(['menuInteraction'])

  const store = useStore()

  const { appLanguage, darkTheme } = useApp()
  const {
    authUser,
    isAuthenticated,
    isAuthUserSuspended,
    authUserHasModeratorRights,
  } = useAuthUser()

  const isMenuOpen: Ref<boolean> = ref(false)
  const displayModal: Ref<boolean> = ref(false)

  const hasUnreadNotifications: ComputedRef<boolean> = computed(
    () => store.getters[NOTIFICATIONS_STORE.GETTERS.UNREAD_STATUS]
  )

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

  onBeforeMount(() => setTheme())
</script>

<style scoped lang="scss">
  @use '~@/scss/fonts.scss' as *;
  @use '~@/scss/colors.scss' as *;
  @use '~@/scss/vars.scss' as *;

  #nav {
    background: var(--nav-bar-background-color);
    display: flex;
    padding: 15px 10px 10px;

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
        &.app-name {
          color: var(--app-color);
        }
      }
    }

    .app-name {
      color: var(--app-color);
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
            width: 190px !important;
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
        &.logout-button {
          padding: $default-padding * 0.6 0 0 $default-padding * 0.6;
        }
      }

      .clear-theme {
        filter: var(--workout-img-color);
        height: 20px;
        margin-bottom: -3px;
      }
    }

    @media screen and (max-width: $medium-limit) {
      .hamburger-icon {
        display: block;
      }
      .nav-icon-open {
        display: flex;
        text-align: right;
        justify-content: flex-end;
        gap: $default-padding;
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
          background: var(--nav-bar-background-color);
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
              width: auto !important;
              height: 200px;
              overflow-y: scroll;

              @media screen and (orientation: portrait) {
                margin-left: initial !important;
              }

              @media screen and (orientation: landscape) {
                margin-top: -35px;
                margin-left: 35px !important;
              }
            }
          }
          &.notifications {
            margin: $default-margin 0 0;
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
          height: 0;
          width: 88%;
        }
      }
      .theme-button {
        margin-left: $default-padding * 1.5;
      }
    }
    .fa-language {
      cursor: pointer;
    }
  }
</style>
