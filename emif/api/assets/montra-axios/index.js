import axios from 'axios';
import { base_url } from '../../../package.json';

const MontraAxios = axios.create({
  baseURL: base_url,
  xsrfHeaderName: "X-CSRFToken",
  xsrfCookieName: "csrftoken",
  withCredentials: true,
});

export default MontraAxios;
