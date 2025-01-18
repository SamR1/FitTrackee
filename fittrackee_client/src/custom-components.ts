import Comment from '@/components/Comment/Comment.vue'
import AlertMessage from '@/components/Common/AlertMessage.vue'
import Card from '@/components/Common/Card.vue'
import CustomTextArea from '@/components/Common/CustomTextArea.vue'
import Distance from '@/components/Common/Distance.vue'
import Dropdown from '@/components/Common/Dropdown.vue'
import ErrorMessage from '@/components/Common/ErrorMessage.vue'
import EquipmentTypeImage from '@/components/Common/Images/EquipmentTypeImage/index.vue'
import SportImage from '@/components/Common/Images/SportImage/index.vue'
import Loader from '@/components/Common/Loader.vue'
import Modal from '@/components/Common/Modal.vue'
import VisibilityIcon from '@/components/Common/VisibilityIcon.vue'

export const customComponents = [
  { target: AlertMessage, name: 'AlertMessage' },
  { target: Card, name: 'Card' },
  { target: CustomTextArea, name: 'CustomTextArea' },
  { target: Distance, name: 'Distance' },
  { target: Dropdown, name: 'Dropdown' },
  { target: ErrorMessage, name: 'ErrorMessage' },
  { target: Loader, name: 'Loader' },
  { target: Modal, name: 'Modal' },
  { target: SportImage, name: 'SportImage' },
  { target: EquipmentTypeImage, name: 'EquipmentTypeImage' },
  { target: VisibilityIcon, name: 'VisibilityIcon' },
  { target: Comment, name: 'Comment' },
]
