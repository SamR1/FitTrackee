<template>
  <div id="admin-tile-providers" class="admin-card">
    <Card>
      <template #title>{{ $t('admin.TILE_PROVIDERS.TITLE') }}</template>
      <template #content>
        <button class="top-button" @click.prevent="$router.push('/admin')">
          {{ $t('admin.BACK_TO_ADMIN') }}
        </button>
        <div class="responsive-table">
          <table>
            <thead>
              <tr>
                <th class="text-left">
                  {{ $t('common.TILE_PROVIDERS', 0) }}
                </th>
                <th>{{ $t('admin.TILE_PROVIDERS.ENABLED') }}</th>
                <th>{{ $t('admin.TILE_PROVIDERS.DEFAULT') }}</th>
                <th class="text-left">
                  {{ $t('admin.ACTION') }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="tileProvider in tileProviders" :key="tileProvider.id">
                <td>
                  <span class="cell-heading">
                    {{ $t('admin.TILE_PROVIDERS.LABEL') }}
                  </span>
                  {{ tileProvider.name }}
                </td>
                <td
                  v-if="'enabled' in tileProvider"
                  class="tile-provider-attribute"
                >
                  <span class="cell-heading">
                    {{ $t('admin.TILE_PROVIDERS.ENABLED') }}
                  </span>
                  <i
                    :class="`fa fa${tileProvider.enabled ? '-check' : ''}`"
                    aria-hidden="true"
                  />
                </td>
                <td class="tile-provider-attribute">
                  <span class="cell-heading">
                    {{ $t('admin.TILE_PROVIDERS.ENABLED') }}
                  </span>
                  <i
                    :class="`fa fa${tileProvider.default ? '-check' : ''}`"
                    aria-hidden="true"
                  />
                </td>
                <td>
                  <div class="tile-providers-actions">
                    <span class="cell-heading">
                      {{ $t('admin.ACTION') }}
                    </span>
                    <button
                      :class="{ danger: tileProvider.enabled }"
                      :disabled="
                        (tileProvider as ITileProviderForAdmin)
                          .api_key_is_missing
                      "
                      @click="
                        updateTileProvider(
                          tileProvider.id,
                          !tileProvider.enabled,
                          tileProvider.default
                        )
                      "
                    >
                      {{
                        $t(`buttons.${tileProvider.enabled ? 'DIS' : 'EN'}ABLE`)
                      }}
                    </button>
                    <button
                      v-if="
                        !(tileProvider as ITileProviderForAdmin)
                          .api_key_is_missing && !tileProvider.default
                      "
                      @click="updateTileProvider(tileProvider.id, true, true)"
                    >
                      {{ $t('buttons.SET_AS_DEFAULT') }}
                    </button>
                    <span
                      v-if="
                        (tileProvider as ITileProviderForAdmin)
                          .api_key_is_missing
                      "
                      class="provider-warning"
                    >
                      <i class="fa fa-warning" aria-hidden="true" />
                      {{ $t('admin.TILE_PROVIDERS.NO_API_KEY_SET') }}
                    </span>
                    <span
                      v-if="
                        (tileProvider as ITileProviderForAdmin).set_by_users
                      "
                      class="provider-warning"
                    >
                      <i class="fa fa-warning" aria-hidden="true" />
                      {{ $t('admin.TILE_PROVIDERS.SET_BY_USERS') }}
                    </span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
          <ErrorMessage :message="errorMessages" v-if="errorMessages" />
          <div class="admin-help">
            <span class="info-box">
              <i class="fa fa-info-circle" aria-hidden="true" />
              {{ $t('admin.APPLICATION_MAY_BE_RESTARTED_AFTER_CHANGES') }}
            </span>
          </div>
          <button @click.prevent="$router.push('/admin')">
            {{ $t('admin.BACK_TO_ADMIN') }}
          </button>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
  import { onBeforeMount } from 'vue'

  import useApp from '@/composables/useApp'
  import useTileProviders from '@/composables/useTileProviders.ts'
  import { TILE_PROVIDERS_STORE } from '@/store/constants.ts'
  import type { ITileProviderForAdmin } from '@/types/tileProviders.ts'
  import { useStore } from '@/use/useStore.ts'

  const store = useStore()

  const { errorMessages } = useApp()
  const { tileProviders, updateTileProvider } = useTileProviders()

  onBeforeMount(() =>
    store.dispatch(TILE_PROVIDERS_STORE.ACTIONS.GET_TILE_PROVIDERS)
  )
</script>

<style lang="scss" scoped>
  @use '~@/scss/vars.scss' as *;
  #admin-tile-providers {
    .top-button {
      display: none;
    }
    table {
      .tile-providers-actions {
        display: flex;
        justify-content: initial;
        align-items: center;
        gap: $default-padding;
        flex-wrap: wrap;
      }
      .tile-provider-attribute {
        text-align: center;
      }
      .provider-warning {
        font-size: 0.95em;
        font-style: italic;
        padding: 0 $default-padding;
      }
    }
    .admin-help {
      margin-bottom: $default-margin;
    }

    @media screen and (max-width: $small-limit) {
      .top-button {
        display: block;
        margin-bottom: $default-margin * 2;
      }
      table {
        .tile-providers-actions {
          justify-content: center;
        }
      }
    }
  }
</style>
