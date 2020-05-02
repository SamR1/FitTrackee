import React from 'react'
import { Link } from 'react-router-dom'

import { formatUrl, rangePagination } from '../../utils'

export default class Pagination extends React.PureComponent {
  getUrl(value) {
    const { query, pathname } = this.props
    const newQuery = Object.assign({}, query)
    let page = query.page ? +query.page : 1
    switch (value) {
      case 'prev':
        page -= 1
        break
      case 'next':
        page += 1
        break
      default:
        page = +value
    }
    newQuery.page = page
    return formatUrl(pathname, newQuery)
  }

  render() {
    const { pagination, t } = this.props
    return (
      <>
        {pagination && Object.keys(pagination).length > 0 && (
          <nav aria-label="Page navigation example">
            <ul className="pagination justify-content-center">
              <li
                className={`page-item ${pagination.has_prev ? '' : 'disabled'}`}
              >
                <Link
                  className="page-link"
                  to={this.getUrl('prev')}
                  aria-disabled={!pagination.has_prev}
                >
                  {t('common:Previous')}
                </Link>
              </li>
              {rangePagination(pagination.pages).map(page => (
                <li
                  key={page}
                  className={`page-item ${
                    page === pagination.page ? 'active' : ''
                  }`}
                >
                  <Link className="page-link" to={this.getUrl(page)}>
                    {page}
                  </Link>
                </li>
              ))}
              <li
                className={`page-item ${pagination.has_next ? '' : 'disabled'}`}
              >
                <Link
                  className="page-link"
                  to={this.getUrl('next')}
                  aria-disabled={!pagination.has_next}
                >
                  {t('common:Next')}
                </Link>
              </li>
            </ul>
          </nav>
        )}
      </>
    )
  }
}
