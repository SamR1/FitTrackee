<template>
  <div id="new-oauth2-app">
    <h1 id="new-oauth2-title">{{ $t('oauth2.ADD_A_NEW_APP') }}</h1>
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
            <label for="app-description">
              {{ $t('oauth2.APP.DESCRIPTION') }}
            </label>
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
            <label for="app-redirect-uri">
              {{ $t('oauth2.APP.REDIRECT_URL') }}*
            </label>
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
            <div
              v-for="scope in filtered_scopes"
              class="form-item-scope-checkboxes"
              :key="scope"
            >
              <label class="scope-label">
                <input
                  type="checkbox"
                  :name="scope"
                  :checked="scopes.includes(scope)"
                  @change="updateScopes(scope)"
                />
                <code>{{ scope }}</code>
              </label>
              <p
                class="scope-description"
                v-html="$t(`oauth2.APP.SCOPE.${scope}_DESCRIPTION`)"
              ></p>
            </div>
          </div>
        </div>
        <div class="form-buttons">
          <button class="confirm" type="submit" :disabled="scopes.length === 0">
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
  import { computed, reactive, toRefs } from 'vue'
  import type { ComputedRef, Reactive } from 'vue'

  import { OAUTH2_STORE } from '@/store/constants'
  import type { ICustomTextareaData } from '@/types/forms'
  import type { IOAuth2ClientPayload } from '@/types/oauth'
  import type { IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { admin_oauth2_scopes, oauth2_scopes } from '@/utils/oauth'

  interface Props {
    authUser: IAuthUserProfile
  }
  const props = defineProps<Props>()
  const { authUser } = toRefs(props)

  const store = useStore()

  const appForm = reactive({
    client_name: '',
    client_uri: '',
    client_description: '',
    description: '',
    redirect_uri: '',
  })
  const scopes: Reactive<string[]> = reactive([])

  const filtered_scopes: ComputedRef<string[]> = computed(() =>
    getScopes(authUser.value, admin_oauth2_scopes, oauth2_scopes)
  )

  function createApp() {
    const payload: IOAuth2ClientPayload = {
      client_name: appForm.client_name,
      client_description: appForm.client_description,
      client_uri: appForm.client_uri,
      redirect_uris: [appForm.redirect_uri],
      scope: scopes.sort().join(' '),
    }
    store.dispatch(OAUTH2_STORE.ACTIONS.CREATE_CLIENT, payload)
  }
  function updateDescription(textareaData: ICustomTextareaData) {
    appForm.client_description = textareaData.value
  }
  function updateScopes(scope: string) {
    const index = scopes.indexOf(scope)
    if (index > -1) {
      scopes.splice(index, 1)
    } else {
      scopes.push(scope)
    }
  }
  function getScopes(
    authUser: IAuthUserProfile,
    admin_scopes: string[],
    scopes: string[]
  ) {
    const filtered_scopes = [...scopes]
    if (authUser.admin) {
      filtered_scopes.push(...admin_scopes)
    }
    return filtered_scopes.sort()
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

        input[type='text'] {
          height: 20px;
        }
        .form-item-scope {
          padding: $default-padding;

          .form-item-scope-label {
            font-weight: bold;
          }

          .form-item-scope-checkboxes {
            padding-bottom: $default-padding;

            .scope-label {
              height: inherit;
            }
            .scope-description {
              font-style: italic;
              margin: 0 $default-margin * 0.5;
            }
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
