<template>
  <div id="authorize-oauth2-app" v-if="client.client_id">
    <h1 id="authorize-oauth2-title">
      <i18n-t keypath="oauth2.AUTHORIZE_APP">
        <router-link :to="{ name: 'UserApp', params: { id: client.id } }">
          {{ client.name }}
        </router-link>
      </i18n-t>
    </h1>
    <ErrorMessage :message="errorMessages" v-if="errorMessages" />
    <div class="oauth2-access">
      <p>{{ $t('oauth2.APP_REQUESTING_ACCESS') }}</p>
      <ul>
        <li
          class="client-scope"
          v-for="scope in client.scope.split(' ')"
          :key="scope"
        >
          {{ $t(`oauth2.APP.SCOPE.${scope.toUpperCase()}`) }}
        </li>
      </ul>
      <div class="authorize-oauth2-buttons">
        <button class="danger" @click="authorizeApp">
          {{ $t('buttons.AUTHORIZE') }}
        </button>
        <button class="cancel" @click="$router.push('/profile/apps')">
          {{ $t('buttons.CANCEL') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { computed, ComputedRef, onBeforeMount } from 'vue'
  import { useRoute } from 'vue-router'

  import { OAUTH2_STORE, ROOT_STORE } from '@/store/constants'
  import { IOAuth2Client } from '@/types/oauth'
  import { useStore } from '@/use/useStore'

  const route = useRoute()
  const store = useStore()

  const client: ComputedRef<IOAuth2Client> = computed(
    () => store.getters[OAUTH2_STORE.GETTERS.CLIENT]
  )
  const errorMessages: ComputedRef<string | string[] | null> = computed(
    () => store.getters[ROOT_STORE.GETTERS.ERROR_MESSAGES]
  )

  onBeforeMount(() => loadApp())

  function loadApp() {
    if (route.query.client_id && typeof route.query.client_id === 'string') {
      store.dispatch(
        OAUTH2_STORE.ACTIONS.GET_CLIENT_BY_CLIENT_ID,
        route.query.client_id
      )
    }
  }

  function authorizeApp() {
    store.dispatch(OAUTH2_STORE.ACTIONS.AUTHORIZE_CLIENT, {
      client_id: `${route.query.client_id}`,
      redirect_uri: `${route.query.redirect_uri}`,
      response_type: `${route.query.response_type}`,
      scope: `${route.query.scope}`,
      state: `${route.query.state}`,
    })
  }
</script>

<style scoped lang="scss">
  @import '~@/scss/vars.scss';

  #authorize-oauth2-app {
    #authorize-oauth2-title {
      font-size: 1.05em;
      font-weight: bold;
      padding: 0 $default-padding;
    }

    .oauth2-access {
      padding: 0 $default-padding;
    }
    .authorize-oauth2-buttons {
      display: flex;
      button {
        margin: $default-padding * 0.5;
      }
    }
  }
</style>
