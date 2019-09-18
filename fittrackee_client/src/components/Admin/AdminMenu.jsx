import React from 'react'
import { Link } from 'react-router-dom'

import { capitalize } from '../../utils/index'

const menuItems = ['application', 'sports', 'users']

export default function AdminMenu() {
  return (
    <div>
      <ul className="admin-items">
        {menuItems.map(item => (
          <li key={item}>
            <Link
              to={{
                pathname: `/admin/${item}`,
              }}
            >
              {capitalize(item)}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  )
}
