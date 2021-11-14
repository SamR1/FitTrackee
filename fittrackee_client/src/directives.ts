import { Directive, DirectiveBinding } from 'vue'

interface ClickOutsideHTMLElement extends HTMLElement {
  clickOutsideEvent?: (event: MouseEvent | TouchEvent) => void
}

export const clickOutsideDirective: Directive = {
  mounted: (
    element: ClickOutsideHTMLElement,
    binding: DirectiveBinding
  ): void => {
    element.clickOutsideEvent = function (event) {
      if (!(element === event.target || element.contains(<Node>event.target))) {
        binding.value(event)
      }
    }
    document.body.addEventListener('click', element.clickOutsideEvent)
    document.body.addEventListener('touchstart', element.clickOutsideEvent)
  },
  unmounted: function (element: ClickOutsideHTMLElement): void {
    if (element.clickOutsideEvent) {
      document.body.removeEventListener('click', element.clickOutsideEvent)
      document.body.removeEventListener('touchstart', element.clickOutsideEvent)
      element.clickOutsideEvent = undefined
    }
  },
}
