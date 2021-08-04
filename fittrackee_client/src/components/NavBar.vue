<template>
  <div id="nav">
    <div class="container">
      <div class="nav-app-name">
        <div class="nav-item app-name">FitTrackee</div>
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
          <router-link class="nav-item" to="/">{{
            t('dashboard.DASHBOARD')
          }}</router-link>
          <div class="nav-item">{{ t('workouts.WORKOUTS') }}</div>
          <div class="nav-item">{{ t('statistics.STATISTICS') }}</div>
          <div class="nav-item">{{ t('administration.ADMIN') }}</div>
          <div class="nav-item">{{ t('workouts.ADD_WORKOUT') }}</div>
        </div>
        <div class="nav-items-user-menu">
          <div class="nav-item">User</div>
          <div class="nav-item">{{ t('user.LOGOUT') }}</div>
          <!--          <span class="nav-item">{{ t('user.REGISTER') }}</span>-->
          <!--          <span class="nav-item">{{ t('user.LOGIN') }}</span>-->
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
  import { computed, defineComponent, ref } from 'vue'
  import { useI18n } from 'vue-i18n'
  import { useStore } from 'vuex'

  import { IDropdownOption } from '@/types'
  import Dropdown from '@/components/Common/Dropdown.vue'

  export default defineComponent({
    name: 'NavBar',
    components: {
      Dropdown,
    },
    setup() {
      const { t, locale, availableLocales } = useI18n()
      const store = useStore()
      const availableLanguages = availableLocales.map((l) => {
        return { label: l.toUpperCase(), value: l }
      })
      let isMenuOpen = ref(false)
      function openMenu() {
        isMenuOpen.value = true
      }
      function closeMenu() {
        isMenuOpen.value = false
      }
      function updateLanguage(option: IDropdownOption) {
        locale.value = option.value.toString()
        store.commit('setLanguage', option.value)
      }

      return {
        availableLanguages,
        isMenuOpen,
        language: computed(() => store.state.language),
        t,
        openMenu,
        closeMenu,
        updateLanguage,
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

    a {
      &.router-link-exact-active {
        color: var(--nav-bar-link-active);
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
        margin-right: 18px;
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

        .nav-item {
          padding: 7px 25px;
        }
      }
    }
  }
</style>
