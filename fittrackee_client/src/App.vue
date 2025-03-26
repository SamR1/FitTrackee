<template>
  <div id="top" />
  <NavBar @menuInteraction="updateHideScrollBar" />
  <main>
    <div v-if="appLoading" class="app-container">
      <div class="app-loading">
        <Loader />
      </div>
    </div>
    <div v-else class="app-container" :class="{ 'hide-scroll': hideScrollBar }">
      <router-view v-if="appConfig" />
      <NoConfig v-else />
    </div>
    <div class="container scroll">
      <button
        class="scroll-button"
        :class="{ 'display-button': displayScrollButton }"
        @click="scrollToTop"
        :title="$t('common.SCROLL_UP')"
        id="scroll-up-button"
      >
        <i class="fa fa-chevron-up" aria-hidden="true"></i>
      </button>
    </div>
  </main>
  <Footer
    v-if="appConfig"
    :version="appConfig ? appConfig.version : ''"
    :adminContact="appConfig.admin_contact"
  />
</template>

<script setup lang="ts">
  import { ref, onBeforeMount, onMounted } from 'vue'
  import type { Ref } from 'vue'

  import Footer from '@/components/Footer.vue'
  import NavBar from '@/components/NavBar.vue'
  import NoConfig from '@/components/NoConfig.vue'
  import useApp from '@/composables/useApp'
  import { ROOT_STORE } from '@/store/constants'
  import type { TLanguage } from '@/types/locales'
  import { useStore } from '@/use/useStore'
  import { isLanguageSupported } from '@/utils/locales'

  const store = useStore()

  const { appConfig, appLoading } = useApp()

  const hideScrollBar: Ref<boolean> = ref(false)
  const displayScrollButton: Ref<boolean> = ref(false)

  function updateHideScrollBar(isMenuOpen: boolean) {
    hideScrollBar.value = isMenuOpen
  }
  function isScrolledToBottom(element: Element): boolean {
    return (
      element.getBoundingClientRect().top < window.innerHeight &&
      element.getBoundingClientRect().bottom >= 0
    )
  }
  function scroll() {
    window.onscroll = () => {
      const bottom = document.querySelector('#bottom')
      displayScrollButton.value = bottom !== null && isScrolledToBottom(bottom)
    }
  }
  function scrollToTop() {
    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    })
    setTimeout(() => {
      displayScrollButton.value = false
      // for now scroll down button only exists in workouts list
      const scrollDownBtn = document.getElementById('scroll-down-button')
      if (scrollDownBtn) {
        scrollDownBtn.focus()
      } else {
        const ft = document.getElementById('fittrackee-name')
        ft?.focus()
      }
    }, 300)
  }
  function initLanguage() {
    let language: TLanguage = 'en'
    try {
      const navigatorLanguage = navigator.language.split('-')[0]
      if (isLanguageSupported(navigatorLanguage)) {
        language = navigatorLanguage
      }
    } catch (e) {
      language = 'en'
    }
    store.dispatch(ROOT_STORE.ACTIONS.UPDATE_APPLICATION_LANGUAGE, language)
  }

  onBeforeMount(() => {
    initLanguage()
    store.dispatch(ROOT_STORE.ACTIONS.GET_APPLICATION_CONFIG)
  })
  onMounted(() => scroll())
</script>

<style src="vue-multiselect/dist/vue-multiselect.css" />
<style lang="scss">
  @use '~@/scss/base.scss';
  @use '~@/scss/vars.scss' as *;

  .app-container {
    height: $app-height;

    &.hide-scroll {
      overflow: hidden;
    }

    .app-loading {
      display: flex;
      align-items: center;
      height: 100%;
    }
  }

  .scroll {
    display: flex;
    justify-content: flex-end;
    position: fixed;
    bottom: 42px;
    right: -15px;
    padding: 0 $default-padding * 2.5;

    .scroll-button {
      &.display-button {
        display: block;
      }
    }
  }
</style>
