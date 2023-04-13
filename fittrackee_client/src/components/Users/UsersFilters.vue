<template>
  <div class="users-filters">
    <div class="search-username">
      <input
        id="username"
        name="username"
        v-model.trim="username"
        @keyup.enter="searchUsers"
      />
      <i
        v-if="username !== ''"
        class="fa fa-times"
        aria-hidden="true"
        @click="resetFilter"
      />
    </div>
    <i
      class="fa fa-search"
      :class="{ 'fa-disabled': username === '' }"
      aria-hidden="true"
      @click="searchUsers"
    />
  </div>
</template>

<script lang="ts" setup>
  import { ref } from 'vue'
  import { useRoute } from 'vue-router'

  const route = useRoute()
  const username = ref(route.query.q ? route.query.q : '')

  const emit = defineEmits(['filterOnUsername'])
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
    padding: $default-padding;
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
