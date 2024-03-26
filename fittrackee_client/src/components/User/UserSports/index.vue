<template>
  <div id="users-sports">
    <router-view
      :authUser="user"
      :isEdition="isEdition"
      :translatedSports="translatedSports"
    >
    </router-view>
  </div>
</template>

<script setup lang="ts">
  import { computed, type ComputedRef, onUnmounted, toRefs } from 'vue'
  import { useI18n } from 'vue-i18n'

  import { OAUTH2_STORE, ROOT_STORE, SPORTS_STORE } from '@/store/constants'
  import type { ISport, ITranslatedSport } from '@/types/sports'
  import type { IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { translateSports } from '@/utils/sports'

  interface Props {
    user: IAuthUserProfile
    isEdition: boolean
  }
  const props = defineProps<Props>()

  const store = useStore()
  const { t } = useI18n()

  const { user, isEdition } = toRefs(props)
  const sports: ComputedRef<ISport[]> = computed(
    () => store.getters[SPORTS_STORE.GETTERS.SPORTS]
  )
  const translatedSports: ComputedRef<ITranslatedSport[]> = computed(() =>
    translateSports(sports.value, t, 'is_active', user.value.sports_list)
  )

  onUnmounted(() => {
    store.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    store.commit(OAUTH2_STORE.MUTATIONS.SET_CLIENTS, [])
  })
</script>
