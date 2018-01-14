

export const isLoggedIn = () => !!window.localStorage.authToken

export function generateIds(arr) {
  let i = 0
  let arrWithIds = arr.map(arr => {
        const obj = { id: i, value: arr }
        i++
        return obj
    })
    return arrWithIds
}
