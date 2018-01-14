export const isLoggedIn = () => !!window.localStorage.authToken

export function generateIds(arr) {
  let i = 0
  return arr.map(val => {
        const obj = { id: i, value: val }
        i++
        return obj
    })
}
