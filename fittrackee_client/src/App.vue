<template>
  <div id="top" />
  <NavBar @menuInteraction="updateHideScrollBar" />
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
    <div
      class="scroll-button"
      :class="{ 'display-button': displayScrollButton }"
      @click="scrollToTop"
    >
      <i class="fa fa-chevron-up" aria-hidden="true"></i>
    </div>
  </div>
  <Footer v-if="appConfig" :version="appConfig ? appConfig.version : ''" />
</template>

<script setup lang="ts">
  import { ComputedRef, computed, ref, onBeforeMount, onMounted } from 'vue'

  import Footer from '@/components/Footer.vue'
  import NavBar from '@/components/NavBar.vue'
  import NoConfig from '@/components/NoConfig.vue'
  import { ROOT_STORE } from '@/store/constants'
  import { TAppConfig } from '@/types/application'
  import { useStore } from '@/use/useStore'

  const store = useStore()

  const appConfig: ComputedRef<TAppConfig> = computed(
    () => store.getters[ROOT_STORE.GETTERS.APP_CONFIG]
  )
  const appLoading: ComputedRef<boolean> = computed(
    () => store.getters[ROOT_STORE.GETTERS.APP_LOADING]
  )
  const hideScrollBar = ref(false)
  const displayScrollButton = ref(false)

  onBeforeMount(() => store.dispatch(ROOT_STORE.ACTIONS.GET_APPLICATION_CONFIG))
  onMounted(() => scroll())

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
      let bottom = document.querySelector('#bottom')
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
    }, 300)
  }
</script>

<style lang="scss">
  @import '~@/scss/base.scss';
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
      background-color: var(--scroll-button-bg-color);
      border-radius: $border-radius;
      box-shadow: 1px 1px 3px lightgrey;
      display: none;
      padding: 0 $default-padding;

      &.display-button {
        display: block;
      }
    }
  }
</style>
