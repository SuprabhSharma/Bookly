// Use the same origin by default. Vite proxies this path in development and
// Nginx proxies it in the production frontend image, so LAN devices never try
// to reach their own localhost instead of the API host.
export const API_URL = (import.meta.env.VITE_API_URL || '/api/v1').replace(/\/$/, '')
