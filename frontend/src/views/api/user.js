import axios from 'axios';
import { backendUrl } from '../config/env';

export const createUser = (param) => {
  return axios.post(
    backendUrl + "users",
    { 
      username: param.username, 
      password: param.password,
      email: param.email }
  )
};
