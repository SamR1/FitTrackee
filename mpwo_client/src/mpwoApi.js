const apiUrl = `${process.env.REACT_APP_API_URL}`


export default class MpwoApi {
  static login(email, password) {
    const request = new Request(`${apiUrl}auth/login`, {
      method: 'POST',
      headers: new Headers({
        'Content-Type': 'application/json',
      }),
      body: JSON.stringify({
        email: email,
        password: password,
      }),
    })
    return fetch(request)
      .then(response => response.json())
      .catch(error => error)
  }
  static register(username, email, password, passwordConf) {
    const request = new Request(`${apiUrl}auth/register`, {
      method: 'POST',
      headers: new Headers({
        'Content-Type': 'application/json',
      }),
      body: JSON.stringify({
        username: username,
        email: email,
        password: password,
        password_conf: passwordConf,
      }),
    })
    return fetch(request)
      .then(response => response.json())
      .catch(error => error)
  }
  static getProfile() {
    const request = new Request(`${apiUrl}auth/profile`, {
      method: 'GET',
      headers: new Headers({
        'Content-Type': 'application/json',
        Authorization: `Bearer ${window.localStorage.getItem('authToken')}`,
      }),
    })
    return fetch(request)
      .then(response => response.json())
      .catch(error => error)
  }
  static updateProfile(form) {
    const request = new Request(`${apiUrl}auth/profile/edit`, {
      method: 'POST',
      headers: new Headers({
        'Content-Type': 'application/json',
        Authorization: `Bearer ${window.localStorage.getItem('authToken')}`,
      }),
      body: JSON.stringify({
        first_name: form.firstName,
        last_name: form.lastName,
        bio: form.bio,
        location: form.location,
        birth_date: form.birthDate,
        password: form.password,
        password_conf: form.passwordConf,
      }),
    })
    return fetch(request)
      .then(response => response.json())
      .catch(error => error)
  }
}
