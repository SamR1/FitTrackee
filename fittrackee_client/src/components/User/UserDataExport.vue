<template>
  <div class="data-export" v-if="exportRequest">
    <div v-if="!canRequestExport()">
      <span class="info-box">
        <i class="fa fa-info-circle" aria-hidden="true" />
        {{ $t('user.EXPORT_REQUEST.ONLY_ONE_EXPORT_PER_DAY') }}
      </span>
    </div>
    <div class="data-export-archive">
      {{ $t('user.EXPORT_REQUEST.DATA_EXPORT') }}
      ({{ exportRequestDate }}):
      <span
        v-if="exportRequest.status === 'successful'"
        class="archive-link"
        @click.prevent="downloadArchive(exportRequest.file_name)"
      >
        <i class="fa fa-download" aria-hidden="true" />
        {{ $t('user.EXPORT_REQUEST.DOWNLOAD_ARCHIVE') }}
        ({{ getReadableFileSizeAsText(exportRequest.file_size) }})
      </span>
      <span v-else>
        {{
          `${$t(
            `user.TASKS.STATUS.${exportRequest.status}`
          )}${exportRequest.status === 'in_progress' ? '…' : ''}`
        }}
        <span v-if="exportRequest.status === 'errored'">
          ({{ $t('user.EXPORT_REQUEST.REQUEST_ANOTHER_EXPORT') }})
        </span>
      </span>
      <span v-if="generatingLink">
        {{ $t(`user.EXPORT_REQUEST.GENERATING_LINK`) }}
        <i class="fa fa-spinner fa-pulse" aria-hidden="true" />
      </span>
    </div>
  </div>
</template>
<script setup lang="ts">
  import { isBefore, subDays } from 'date-fns'
  import { computed, type ComputedRef, ref, type Ref, toRefs } from 'vue'

  import authApi from '@/api/authApi.ts'
  import { AUTH_USER_STORE } from '@/store/constants.ts'
  import type { IAuthUserProfile, IExportRequest } from '@/types/user.ts'
  import { useStore } from '@/use/useStore.ts'
  import { formatDate } from '@/utils/dates.ts'
  import { getReadableFileSizeAsText } from '@/utils/files.ts'

  interface Props {
    user: IAuthUserProfile
  }
  const props = defineProps<Props>()
  const { user } = toRefs(props)

  const store = useStore()

  const generatingLink: Ref<boolean> = ref(false)
  const exportRequest: ComputedRef<IExportRequest | null> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.EXPORT_REQUEST]
  )
  const exportRequestDate: ComputedRef<string | null> = computed(() =>
    getExportRequestDate()
  )
  function getExportRequestDate() {
    return exportRequest.value
      ? formatDate(
          exportRequest.value.created_at,
          user.value.timezone,
          user.value.date_format,
          { withTime: true, language: null, withSeconds: true }
        )
      : null
  }
  function canRequestExport() {
    return exportRequest.value?.created_at
      ? isBefore(
          new Date(exportRequest.value.created_at),
          subDays(new Date(), 1)
        )
      : true
  }
  async function downloadArchive(filename: string) {
    generatingLink.value = true
    await authApi
      .get(`/auth/account/export/${filename}`, {
        responseType: 'blob',
      })
      .then((response) => {
        const archiveFileUrl = window.URL.createObjectURL(
          new Blob([response.data], { type: 'application/zip' })
        )
        const archive_link = document.createElement('a')
        archive_link.href = archiveFileUrl
        archive_link.setAttribute('download', filename)
        document.body.appendChild(archive_link)
        archive_link.click()
        window.URL.revokeObjectURL(archiveFileUrl)
      })
      .finally(() => (generatingLink.value = false))
  }
</script>
<style scoped lang="scss">
  @use '~@/scss/vars.scss' as *;
  .data-export {
    display: flex;
    flex-direction: column;
    gap: $default-padding * 2;
    margin-top: $default-margin * 2;
    .data-export-archive {
      font-size: 0.9em;

      .archive-link {
        color: var(--app-a-color);
        cursor: pointer;
      }
    }
  }
</style>
