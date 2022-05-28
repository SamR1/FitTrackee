<template>
  <div id="new-oauth2-app">
    <p id="new-oauth2-title">{{ $t('oauth2.ADD_A_NEW_APP') }}</p>
    <div id="apps-form">
      <form @submit.prevent="createApp">
        <div class="form-items">
          <div class="form-item">
            <label for="app-name">{{ $t('oauth2.APP.NAME') }}*</label>
            <input
              id="app-name"
              type="text"
              required
              v-model="appForm.client_name"
            />
          </div>
          <div class="form-item">
            <label for="app-description">{{
              $t('oauth2.APP.DESCRIPTION')
            }}</label>
            <CustomTextArea
              name="app-description"
              :charLimit="200"
              :input="appForm.description"
              @updateValue="updateDescription"
            />
          </div>
          <div class="form-item">
            <label for="app-url">{{ $t('oauth2.APP.URL') }}*</label>
            <input
              id="app-url"
              type="text"
              required
              v-model="appForm.client_uri"
            />
          </div>
          <div class="form-item">
            <label for="app-redirect-uri"
              >{{ $t('oauth2.APP.REDIRECT_URL') }}*</label
            >
            <input
              id="app-redirect-uri"
              type="text"
              required
              v-model="appForm.redirect_uri"
            />
          </div>
          <div class="form-item-scope">
            <div class="form-item-scope-label">
              {{ $t('oauth2.APP.SCOPE.LABEL') }}*
            </div>
            <div class="form-item-scope-checkboxes">
              <label>
                <input
                  type="checkbox"
                  :checked="appForm.read"
                  @change="appForm.read = !appForm.read"
                />
                {{ $t('oauth2.APP.SCOPE.READ') }}
              </label>
              <label>
                <input
                  type="checkbox"
                  :checked="appForm.write"
                  @change="appForm.write = !appForm.write"
                />
                {{ $t('oauth2.APP.SCOPE.WRITE') }}
              </label>
            </div>
          </div>
        </div>
        <div class="form-buttons">
          <button
            class="confirm"
            type="submit"
            :disabled="!appForm.read && !appForm.write"
          >
            {{ $t('buttons.SUBMIT') }}
          </button>
          <button
            class="cancel"
            @click.prevent="() => $router.push('/profile/apps')"
          >
            {{ $t('buttons.CANCEL') }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { reactive } from 'vue'

  import { OAUTH2_STORE } from '@/store/constants'
  import { IOAuth2ClientPayload } from '@/types/oauth'
  import { useStore } from '@/use/useStore'

  const store = useStore()
  const appForm = reactive({
    client_name: '',
    client_uri: '',
    client_description: '',
    redirect_uri: '',
    read: true,
    write: false,
  })

  function createApp() {
    const payload: IOAuth2ClientPayload = {
      client_name: appForm.client_name,
      client_description: appForm.client_description,
      client_uri: appForm.client_uri,
      redirect_uris: [appForm.redirect_uri],
      scope: `${appForm.read ? 'read' : ''} ${appForm.write ? 'write' : ''}`,
    }
    store.dispatch(OAUTH2_STORE.ACTIONS.CREATE_CLIENT, payload)
  }
  function updateDescription(value: string) {
    appForm.client_description = value
  }
</script>

<style scoped lang="scss">
  @import '~@/scss/vars.scss';

  #new-oauth2-app {
    #new-oauth2-title {
      font-size: 1.05em;
      font-weight: bold;
      padding: 0 $default-padding;
    }

    #apps-form {
      .form-items {
        display: flex;
        flex-direction: column;

        input {
          height: 20px;
        }
        .form-item-scope {
          padding: $default-padding;

          .form-item-scope-label {
            font-weight: bold;
          }

          .form-item-scope-checkboxes {
            display: flex;
            gap: $default-padding;
          }
        }

        .form-item {
          display: flex;
          flex-direction: column;
          padding: $default-padding;
        }
      }

      .form-buttons {
        display: flex;
        justify-content: flex-end;
        button {
          margin: $default-padding * 0.5;
        }
      }
    }
  }
</style>
