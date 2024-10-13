<template>
  <div id="authorize-oauth2-app">
    <div v-if="client.client_id">
      <h1 id="authorize-oauth2-title">
        <i18n-t keypath="oauth2.AUTHORIZE_APP">
          <router-link :to="{ name: 'UserApp', params: { id: client.id } }">
            {{ client.name }}
          </router-link>
        </i18n-t>
      </h1>
      <ErrorMessage :message="errorMessages" v-if="errorMessages" />
      <div class="oauth2-access description-list">
        <p>{{ $t('oauth2.APP_REQUESTING_ACCESS') }}</p>
        <dl>
          <template v-for="scope in client.scope.split(' ')" :key="scope">
            <dt class="client-scope">
              <code>{{ scope }}</code>
            </dt>
            <dd v-html="$t(`oauth2.APP.SCOPE.${scope}_DESCRIPTION`)"></dd>
          </template>
        </dl>
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
    <div v-else>
      <p class="no-app">{{ $t('oauth2.NO_APP') }}</p>
      <button @click="$router.push('/profile/apps')">
        {{ $t('buttons.BACK') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { computed, onBeforeMount } from 'vue'
  import type { ComputedRef } from 'vue'
  import { useRoute } from 'vue-router'

  import useApp from '@/composables/useApp'
  import { OAUTH2_STORE } from '@/store/constants'
  import type { IOAuth2Client } from '@/types/oauth'
  import { useStore } from '@/use/useStore'

  const route = useRoute()
  const store = useStore()

  const { errorMessages } = useApp()

  const client: ComputedRef<IOAuth2Client> = computed(
    () => store.getters[OAUTH2_STORE.GETTERS.CLIENT]
  )

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
      state: `${route.query.state ? route.query.state : ''}`,
      code_challenge: `${
        route.query.code_challenge ? route.query.code_challenge : ''
      }`,
      code_challenge_method: `${
        route.query.code_challenge_method
          ? route.query.code_challenge_method
          : ''
      }`,
    })
  }

  onBeforeMount(() => loadApp())
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
