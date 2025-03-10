import axios from "axios"

export function verifyRefreshToken(){
    const response = axios.post(process.env.VUE_APP_BACKEND_URL + "token",
        {},
        { withCredentials: true })
    return response
}
