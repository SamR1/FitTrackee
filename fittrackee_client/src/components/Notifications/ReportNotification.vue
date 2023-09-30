<script setup lang="ts">
  import { toRefs } from 'vue'

  import UserPicture from '@/components/User/UserPicture.vue'
  import { IReportForAdmin } from '@/types/reports'

  interface Props {
    report: IReportForAdmin
  }

  const props = defineProps<Props>()
  const { report } = toRefs(props)
</script>

<template>
  <div class="report-notification" v-if="report.reported_user">
    <div class="reported-user">
      <UserPicture :user="report.reported_user" />
      <div class="user-name">
        <router-link :to="`/users/${report.reported_user.username}`">
          {{ report.reported_user.username }}
        </router-link>
      </div>
    </div>
    <div class="report-button">
      <button @click="$router.push(`/admin/reports/${report.id}`)">
        {{ $t('admin.APP_MODERATION.REPORT') }}
      </button>
    </div>
  </div>
</template>

<style scoped lang="scss">
  @import '~@/scss/vars';
  .report-notification {
    display: flex;
    justify-content: space-between;

    .reported-user {
      display: flex;
      align-items: center;
      .user-picture {
        min-width: initial;
        padding: 0 $default-padding;
      }
    }
    .report-button {
      display: flex;
      flex-direction: column;
      justify-content: center;
      button {
        text-transform: capitalize;
      }
    }
  }
</style>
