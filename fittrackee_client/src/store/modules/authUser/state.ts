import type { IAuthUserState } from '@/store/modules/authUser/types'
import type { IPagination } from '@/types/api.ts'
import type {
  IUserReportAction,
  IAuthUserProfile,
  IArchiveUploadTask,
} from '@/types/user'

export const authUserState: IAuthUserState = {
  authToken: null,
  authUserProfile: <IAuthUserProfile>{},
  isSuccess: false,
  isRegistrationSuccess: false,
  loading: false,
  exportRequest: null,
  followRequests: [],
  blockedUsers: [],
  userReportAction: <IUserReportAction>{},
  timezones: [],
  archiveUploadTasks: {
    task: <IArchiveUploadTask>{},
    tasks: [],
    loading: false,
    pagination: <IPagination>{},
  },
}
