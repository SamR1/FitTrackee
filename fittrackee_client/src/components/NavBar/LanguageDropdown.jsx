import React, { Component } from 'react'

import { ReactComponent as EnFlag } from '../../images/flags/en.svg'
import { ReactComponent as FrFlag } from '../../images/flags/fr.svg'

const languages = [
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
      selected: 'en',
    }
  }

  selectLanguage(name) {
    this.setState({
      selected: name,
    })
  }

  toggleDropdown() {
    this.setState(prevState => ({
      isOpen: !prevState.isOpen,
    }))
  }

  render() {
    const { isOpen, selected } = this.state
    return (
      <div className="dropdown-wrapper" onClick={() => this.toggleDropdown()}>
        <ul className="dropdown-list i18n-flag">
          {languages
            .filter(language =>
              isOpen ? language : language.name === selected
            )
            .map(language => (
              <li
                className="dropdown-item"
                key={language.name}
                onClick={() => this.selectLanguage(language.name)}
              >
                {language.flag} {language.name}
              </li>
            ))}
        </ul>
      </div>
    )
  }
}

export default Dropdown
