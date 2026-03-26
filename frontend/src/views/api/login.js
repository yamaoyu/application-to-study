import axios from 'axios';
import { backendUrl } from '../config/env';

export const login = (username, password) => {
  return axios.post(
    backendUrl + "login",
    { username, password },
    { withCredentials: true }
  )
};
