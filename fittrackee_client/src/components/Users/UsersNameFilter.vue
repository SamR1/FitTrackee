<template>
  <div class="users-filters">
    <div class="search-username">
      <label for="username" class="visually-hidden">
        {{ $t('user.USERNAME') }}
      </label>
      <input
        id="username"
        name="username"
        v-model.trim="username"
        @keyup.enter="searchUsers"
        :placeholder="$t('user.FILTER_ON_USERNAME')"
      />
      <button
        v-if="username !== ''"
        class="transparent search-buttons"
        :title="$t('buttons.CLEAR_FILTER')"
      >
        <i class="fa fa-times" aria-hidden="true" @click="resetFilter" />
      </button>
    </div>
    <button class="transparent search-buttons" :title="$t('buttons.SEARCH')">
      <i
        class="fa fa-search"
        :class="{ 'fa-disabled': username === '' }"
        aria-hidden="true"
        @click="searchUsers"
      />
    </button>
  </div>
</template>

<script lang="ts" setup>
  import { ref } from 'vue'
  import type { Ref } from 'vue'
  import { useRoute } from 'vue-router'
  import type { LocationQueryValue } from 'vue-router'

  const emit = defineEmits(['filterOnUsername'])

  const route = useRoute()

  const username: Ref<string | LocationQueryValue[]> = ref(
    route.query.q ? route.query.q : ''
  )

  function searchUsers() {
    if (username.value !== '') {
      emit('filterOnUsername', username)
    }
  }
  function resetFilter() {
    username.value = ''
    emit('filterOnUsername', username.value)
  }
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';

  .users-filters {
    display: flex;
    align-items: center;
    padding: $default-padding 0;
    gap: $default-padding;

    .fa {
      font-size: 1.5em;
    }
    .fa-disabled {
      color: var(--disabled-color);
    }

    .search-username {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: $default-padding;

      border: solid 1px var(--card-border-color);
      border-radius: $border-radius;
      color: var(--info-color);
      width: 45%;

      input {
        border: none;
        height: 12px;
        width: 90%;
      }
      input:focus {
        outline: none;
      }
      .fa-times {
        padding-right: 10px;
      }
    }

    .search-buttons {
      padding: 0;
    }
  }

  @media screen and (max-width: $small-limit) {
    .users-filters {
      .search-username {
        width: 400px;
      }
    }
  }
  @media screen and (max-width: $x-small-limit) {
    .users-filters {
      .search-username {
        width: 90%;
      }
    }
  }
</style>
