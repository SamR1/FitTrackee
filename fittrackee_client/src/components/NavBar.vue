<template>
  <div id="nav">
    <div class="nav-container">
      <div class="nav-app-name">
        <div class="nav-item app-name" @click="$router.push('/')">
          FitTrackee
        </div>
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
          ></i>
        </div>
        <div class="nav-items-app-menu" @click="closeMenu()">
          <div class="nav-items-group" v-if="isAuthenticated">
            <router-link class="nav-item" to="/">{{
              t('dashboard.DASHBOARD')
            }}</router-link>
            <div class="nav-item">
              {{ capitalize(t('workouts.WORKOUT', 2)) }}
            </div>
            <div class="nav-item">{{ t('statistics.STATISTICS') }}</div>
            <div class="nav-item">{{ t('administration.ADMIN') }}</div>
            <div class="nav-item">{{ t('workouts.ADD_WORKOUT') }}</div>
            <div class="nav-item nav-separator" />
          </div>
        </div>
        <div class="nav-items-user-menu">
          <div class="nav-items-group" v-if="isAuthenticated">
            <div class="nav-item nav-profile-img">
              <img
                v-if="authUserPictureUrl !== ''"
                class="nav-profile-user-img"
                alt="User picture"
                :src="authUserPictureUrl"
              />
              <div v-else class="no-picture">
                <i class="fa fa-user-circle-o" aria-hidden="true" />
              </div>
            </div>
            <div class="nav-item">{{ authUser.username }}</div>
            <div class="nav-item nav-link" @click="logout">
              {{ t('user.LOGOUT') }}
            </div>
          </div>
          <div class="nav-items-group" v-else>
            <router-link class="nav-item" to="/login" @click="closeMenu">{{
              t('user.LOGIN')
            }}</router-link>
            <router-link class="nav-item" to="/register" @click="closeMenu">{{
              t('user.REGISTER')
            }}</router-link>
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

<script lang="ts">
  import { ComputedRef, computed, defineComponent, ref } from 'vue'
  import { useI18n } from 'vue-i18n'

  import Dropdown from '@/components/Common/Dropdown.vue'
  import { ROOT_STORE, USER_STORE } from '@/store/constants'
  import { IDropdownOption } from '@/types/forms'
  import { IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { capitalize, getApiUrl } from '@/utils'

  export default defineComponent({
    name: 'NavBar',
    components: {
      Dropdown,
    },
    emits: ['menuInteraction'],
    setup(props, { emit }) {
      const { t, locale, availableLocales } = useI18n()
      const store = useStore()

      const availableLanguages = availableLocales.map((l) => {
        return { label: l.toUpperCase(), value: l }
      })
      const authUser: ComputedRef<IAuthUserProfile> = computed(
        () => store.getters[USER_STORE.GETTERS.AUTH_USER_PROFILE]
      )
      const isAuthenticated: ComputedRef<boolean> = computed(
        () => store.getters[USER_STORE.GETTERS.IS_AUTHENTICATED]
      )
      const authUserPictureUrl: ComputedRef<string> = computed(() =>
        isAuthenticated.value && authUser.value.picture
          ? `${getApiUrl()}/users/${
              authUser.value.username
            }/picture?${Date.now()}`
          : ''
      )
      const language: ComputedRef<string> = computed(
        () => store.getters[ROOT_STORE.GETTERS.LANGUAGE]
      )
      let isMenuOpen = ref(false)

      function openMenu() {
        isMenuOpen.value = true
        emit('menuInteraction', true)
      }
      function closeMenu() {
        isMenuOpen.value = false
        emit('menuInteraction', false)
      }
      function updateLanguage(option: IDropdownOption) {
        locale.value = option.value.toString()
        store.commit(ROOT_STORE.MUTATIONS.UPDATE_LANG, option.value)
      }
      function logout() {
        store.dispatch(USER_STORE.ACTIONS.LOGOUT)
      }

      return {
        availableLanguages,
        authUser,
        authUserPictureUrl,
        isAuthenticated,
        isMenuOpen,
        language,
        t,
        capitalize,
        openMenu,
        closeMenu,
        updateLanguage,
        logout,
      }
    },
  })
</script>

<style scoped lang="scss">
  @import '~@/scss/base';

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

      &:hover {
        cursor: pointer;
      }
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

        &.dropdown-wrapper {
          width: 60px;
        }

        ::v-deep(.dropdown-list) {
          margin-left: -10px;
          padding-left: 10px;
          width: 75px;
        }
      }

      .nav-link {
        color: var(--app-a-color);
        cursor: pointer;
      }

      .nav-profile-img {
        margin-bottom: -$default-padding;
        .nav-profile-user-img {
          border-radius: 50%;
          height: 32px;
          width: 32px;
          object-fit: cover;
        }
        .no-picture {
          color: var(--app-a-color);
          font-size: 1.7em;
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
    }
  }
</style>
