<template>
  <span
    class="sport-badge"
    :class="{ inactive: !sport.is_active_for_user }"
    :key="sport.label"
  >
    <SportImage
      :title="sport.translatedLabel"
      :sport-label="sport.label"
      :color="sport.color ? sport.color : sportColors[sport.label]"
    />
    <router-link :to="`/profile/sports/${sport.id}${from}`">
      {{ sport.translatedLabel }}
      {{ sport.is_active_for_user ? '' : `(${$t('common.INACTIVE')})` }}
    </router-link>
  </span>
</template>

<script setup lang="ts">
  import { toRefs } from 'vue'

  import useSports from '@/composables/useSports.ts'
  import type { ITranslatedSport } from '@/types/sports.ts'

  interface Props {
    sport: ITranslatedSport
    from: string
  }
  const props = defineProps<Props>()
  const { sport } = toRefs(props)

  const { sportColors } = useSports()
</script>

<style scoped lang="scss">
  @use '~@/scss/vars.scss' as *;

  .sport-badge {
    display: inline-flex;
    gap: $default-padding;
    border: solid 1px var(--card-border-color);
    border-radius: $border-radius;
    padding: $default-padding * 0.75 $default-padding * 1.2;
    &.inactive {
      font-style: italic;
    }
    .sport-img {
      height: 20px;
      width: 20px;
      margin: 0;
    }
  }
</style>
