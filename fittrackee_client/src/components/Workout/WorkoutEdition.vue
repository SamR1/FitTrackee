<template>
  <div id="workout-edition">
    <Card :without-title="false">
      <template #title>{{ t('workouts.EDIT_WORKOUT') }}</template>
      <template #content>
        <div id="workout-form">
          <form @submit.prevent="updateWorkout">
            <div class="form-items">
              <div class="form-item">
                <label> {{ t('workouts.SPORT', 1) }}: </label>
                <select id="sport" v-model="workoutDataObject.sport_id">
                  <option
                    v-for="sport in translatedSports"
                    :value="sport.id"
                    :key="sport.id"
                  >
                    {{ sport.label }}
                  </option>
                </select>
              </div>
              <div class="form-item">
                <label for="title"> {{ t('workouts.TITLE') }}: </label>
                <input
                  id="title"
                  name="title"
                  type="text"
                  v-model="workoutDataObject.title"
                />
              </div>
              <div class="form-item">
                <label> {{ t('workouts.NOTES') }}: </label>
                <CustomTextArea
                  name="notes"
                  :input="workoutDataObject.notes"
                  @updateValue="updateNotes"
                />
              </div>
            </div>
            <ErrorMessage :message="errorMessages" v-if="errorMessages" />
            <div class="form-buttons">
              <button class="confirm" type="submit">
                {{ t('buttons.SUBMIT') }}
              </button>
              <button
                class="cancel"
                @click="
                  $router.push({
                    name: 'Workout',
                    params: { workoutId: workout.id },
                  })
                "
              >
                {{ t('buttons.CANCEL') }}
              </button>
            </div>
          </form>
        </div>
      </template>
    </Card>
  </div>
</template>

<script lang="ts">
  import {
    ComputedRef,
    PropType,
    defineComponent,
    computed,
    reactive,
    watch,
    onUnmounted,
  } from 'vue'
  import { useI18n } from 'vue-i18n'

  import Card from '@/components/Common/Card.vue'
  import CustomTextArea from '@/components/Common/CustomTextArea.vue'
  import ErrorMessage from '@/components/Common/ErrorMessage.vue'
  import { ROOT_STORE, WORKOUTS_STORE } from '@/store/constants'
  import { ISport } from '@/types/sports'
  import { IWorkout } from '@/types/workouts'
  import { useStore } from '@/use/useStore'
  import { translateSports } from '@/utils/sports'

  export default defineComponent({
    name: 'AddOrEditWorkout',
    components: {
      Card,
      CustomTextArea,
      ErrorMessage,
    },
    props: {
      sports: {
        type: Object as PropType<ISport[]>,
        required: true,
      },
      workout: {
        type: Object as PropType<IWorkout>,
        required: true,
      },
    },
    setup(props) {
      const { t } = useI18n()
      const store = useStore()

      const translatedSports: ComputedRef<ISport[]> = computed(() =>
        translateSports(props.sports, t)
      )
      const errorMessages: ComputedRef<string | string[] | null> = computed(
        () => store.getters[ROOT_STORE.GETTERS.ERROR_MESSAGES]
      )
      const workoutForm = reactive({
        sport_id: 0,
        title: '',
        notes: '',
      })

      function updateNotes(value: string) {
        workoutForm.notes = value
      }
      function updateWorkout() {
        if (props.workout) {
          store.dispatch(WORKOUTS_STORE.ACTIONS.EDIT_WORKOUT, {
            workoutId: props.workout.id,
            data: workoutForm,
          })
        }
      }

      watch(
        () => props.workout,
        async (newWorkout: IWorkout | undefined) => {
          if (newWorkout && newWorkout.id) {
            workoutForm.sport_id = newWorkout.sport_id
            workoutForm.title = newWorkout.title
            workoutForm.notes = newWorkout.notes
          }
        }
      )

      onUnmounted(() => store.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES))

      return {
        errorMessages,
        t,
        translatedSports,
        workoutDataObject: workoutForm,
        updateNotes,
        updateWorkout,
      }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base';

  #workout-edition {
    margin: 25% auto;
    width: 700px;

    ::v-deep(.card) {
      .card-title {
        text-align: center;
        text-transform: uppercase;
      }
      .card-content {
        .form-items {
          display: flex;
          flex-direction: column;

          .form-item {
            display: flex;
            flex-direction: column;
            padding: $default-padding;

            label {
              text-transform: capitalize;
            }
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

    @media screen and (max-width: $small-limit) {
      width: 100%;
    }
  }
</style>
