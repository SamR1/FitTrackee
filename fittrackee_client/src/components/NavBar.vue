<template>
  <div id="nav">
    <div class="container">
      <div class="nav-app-name">
        <span class="nav-item app-name">FitTrackee</span>
      </div>
      <div class="nav-icon-open" :class="{ 'menu-open': isMenuOpen }">
        <i class="fa fa-bars hamburger-icon" @click="openMenu()"></i>
      </div>
      <div class="nav-items" :class="{ 'menu-open': isMenuOpen }">
        <div class="nav-items-close">
          <span class="app-name">FitTrackee</span>
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
          <span class="nav-item">{{ t('workouts.WORKOUTS') }}</span>
          <span class="nav-item">{{ t('statistics.STATISTICS') }}</span>
          <span class="nav-item">{{ t('administration.ADMIN') }}</span>
          <span class="nav-item">{{ t('workouts.ADD_WORKOUT') }}</span>
        </div>
        <div class="nav-items-user-menu">
          <span class="nav-item">User</span>
          <span class="nav-item">{{ t('user.LOGOUT') }}</span>
          <span class="nav-item">{{ t('user.REGISTER') }}</span>
          <span class="nav-item">{{ t('user.LOGIN') }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
  import { defineComponent, ref } from 'vue'
  import { useI18n } from 'vue-i18n'

  export default defineComponent({
    name: 'NavBar',
    setup() {
      let isMenuOpen = ref(false)
      const { t } = useI18n()
      function openMenu() {
        isMenuOpen.value = true
      }
      function closeMenu() {
        isMenuOpen.value = false
      }
      return { isMenuOpen, openMenu, closeMenu, t }
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
      line-height: 12px;
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

      .nav-item {
        padding: 10px 10px;
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
            padding: 19px 25px;
          }
        }
      }
    }
  }
</style>
