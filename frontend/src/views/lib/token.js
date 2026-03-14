import axios from "axios"
import { backendUrl } from "./index"

export function verifyRefreshToken(){
    const response = axios.post(backendUrl + "token",
        {},
        { withCredentials: true })
    return response
}
