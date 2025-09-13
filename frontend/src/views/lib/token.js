import axios from "axios"

export function verifyRefreshToken(){
    const response = axios.post(import.meta.env.VITE_BACKEND_URL + "token",
        {},
        { withCredentials: true })
    return response
}
