// Use the same origin by default. Vite proxies this path in development,
// Docker's Nginx proxies it in the container, and Vercel's api/[...path].js
// proxy handles it in production. Set VITE_API_URL only when calling the
// backend directly (it must include /api/v1).
export const API_URL = (import.meta.env.VITE_API_URL || '/api/v1').replace(/\/$/, '')
