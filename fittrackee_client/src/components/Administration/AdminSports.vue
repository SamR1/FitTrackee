<template>
  <div id="admin-sports" class="admin-card">
    <Card>
      <template #title>{{ $t('admin.SPORTS.TITLE') }}</template>
      <template #content>
        <button class="top-button" @click.prevent="$router.push('/admin')">
          {{ $t('admin.BACK_TO_ADMIN') }}
        </button>
        <div class="responsive-table">
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>{{ $t('admin.SPORTS.TABLE.IMAGE') }}</th>
                <th class="text-left">
                  {{ $t('admin.SPORTS.TABLE.LABEL') }}
                </th>
                <th>{{ $t('admin.SPORTS.TABLE.ACTIVE') }}</th>
                <th class="text-left sport-action">
                  {{ $t('admin.ACTION') }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="sport in translatedSports" :key="sport.id">
                <td class="text-center">
                  <span class="cell-heading">id</span>
                  {{ sport.id }}
                </td>
                <td>
                  <span class="cell-heading">
                    {{ $t('admin.SPORTS.TABLE.IMAGE') }}
                  </span>
                  <SportImage
                    :title="sport.translatedLabel"
                    :sport-label="sport.label"
                    :color="sport.color"
                  />
                </td>
                <td class="sport-label">
                  <span class="cell-heading">
                    {{ $t('admin.SPORTS.TABLE.LABEL') }}
                  </span>
                  {{ sport.translatedLabel }}
                </td>
                <td class="text-center">
                  <span class="cell-heading">
                    {{ $t('admin.SPORTS.TABLE.ACTIVE') }}
                  </span>
                  <i
                    :class="`fa fa${sport.is_active ? '-check' : ''}`"
                    aria-hidden="true"
                  />
                </td>
                <td class="sport-action">
                  <span class="cell-heading">
                    {{ $t('admin.ACTION') }}
                  </span>
                  <div class="action-button">
                    <button
                      :class="{ danger: sport.is_active }"
                      @click="updateSportStatus(sport.id, !sport.is_active)"
                    >
                      {{ $t(`buttons.${sport.is_active ? 'DIS' : 'EN'}ABLE`) }}
                    </button>
                    <span v-if="sport.has_workouts" class="has-workouts">
                      <i class="fa fa-warning" aria-hidden="true" />
                      {{ $t('admin.SPORTS.TABLE.HAS_WORKOUTS') }}
                    </span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
          <ErrorMessage :message="errorMessages" v-if="errorMessages" />
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
  import useSports from '@/composables/useSports'
  import { SPORTS_STORE } from '@/store/constants'
  import { useStore } from '@/use/useStore'

  const store = useStore()

  const { errorMessages } = useApp()
  const { translatedSports } = useSports()

  function updateSportStatus(id: number, isActive: boolean) {
    store.dispatch(SPORTS_STORE.ACTIONS.UPDATE_SPORTS, {
      id,
      isActive,
    })
  }

  onBeforeMount(() => store.dispatch(SPORTS_STORE.ACTIONS.GET_SPORTS, true))
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';
  #admin-sports {
    table {
      td {
        font-size: 1.1em;
      }
    }
    .sport-img {
      height: 35px;
      width: 35px;
      margin: 0 auto;
    }
    .has-workouts {
      font-size: 0.95em;
      font-style: italic;
      padding: 0 $default-padding;
    }
    .sport-action {
      padding-left: $default-padding * 4;
    }
    .action-button {
      display: block;
    }
    .top-button {
      display: none;
    }

    @media screen and (max-width: $small-limit) {
      .sport-action {
        padding-left: $default-padding;
      }
      .has-workouts {
        padding-top: $default-padding * 0.5;
      }
      .action-button {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        flex-direction: column;
      }
      .top-button {
        display: block;
        margin-bottom: $default-margin * 2;
      }
    }
  }
</style>
