import React from 'react'

import { version } from './../../utils'

export default function Footer() {
  return (
    <footer className="footer">
      <div className="container">
        <strong>FitTrackee</strong> v{version} -{' '}
        <a
          href="https://github.com/SamR1/FitTrackee"
          target="_blank"
          rel="noopener noreferrer"
        >
          source code
        </a> under{' '}
        <a
          href="https://choosealicense.com/licenses/gpl-3.0/"
          target="_blank"
          rel="noopener noreferrer"
        >
          GPLv3
        </a>{' '}
         license
      </div>
    </footer>
  )
}

