const appScheme = import.meta.env.VITE_APP_SCHEME;
const backendHost = import.meta.env.VITE_BACKEND_HOST;
export const backendUrl = appScheme + "://" + backendHost + "/";