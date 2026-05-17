import { ref } from 'vue'
import type { Ref } from 'vue'

export default function useScroll() {
  const timer: Ref<ReturnType<typeof setTimeout> | undefined> = ref()

  function scrollTo(selector: string, delay: number = 100) {
    timer.value = setTimeout(() => {
      const element = document.getElementById(selector)
      if (element) {
        element.scrollIntoView({ behavior: 'smooth' })
      }
    }, delay)
  }

  function resetTimeout() {
    if (timer.value) {
      clearTimeout(timer.value)
    }
  }

  return {
    resetTimeout,
    scrollTo,
  }
}
