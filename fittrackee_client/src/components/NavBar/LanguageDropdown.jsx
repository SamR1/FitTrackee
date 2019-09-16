import React, { Component } from 'react'
import { connect } from 'react-redux'

import { ReactComponent as EnFlag } from '../../images/flags/en.svg'
import { ReactComponent as FrFlag } from '../../images/flags/fr.svg'
import { updateLanguage } from '../../actions/index'

export const languages = [
  {
    name: 'en',
    selected: true,
    flag: <EnFlag />,
  },
  {
    name: 'fr',
    selected: false,
    flag: <FrFlag />,
  },
]

class Dropdown extends Component {
  constructor(props) {
    super(props)
    this.state = {
      isOpen: false,
    }
  }

  toggleDropdown() {
    this.setState(prevState => ({
      isOpen: !prevState.isOpen,
    }))
  }

  render() {
    const { isOpen } = this.state
    const { language: selected, onUpdateLanguage } = this.props
    return (
      <div className="dropdown-wrapper" onClick={() => this.toggleDropdown()}>
        <ul className="dropdown-list i18n-flag">
          {languages
            .filter(language =>
              isOpen ? language : language.name === selected
            )
            .map(language => (
              <li
                className={`dropdown-item${
                  language.name === selected && isOpen
                    ? ' dropdown-item-selected'
                    : ''
                }`}
                key={language.name}
                onClick={() => onUpdateLanguage(language.name, selected)}
              >
                {language.flag} {language.name}
              </li>
            ))}
        </ul>
      </div>
    )
  }
}

export default connect(
  state => ({
    language: state.language,
  }),
  dispatch => ({
    onUpdateLanguage: (lang, selected) => {
      if (lang !== selected) {
        dispatch(updateLanguage(lang))
      }
    },
  })
)(Dropdown)
