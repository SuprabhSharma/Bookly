import { api } from '../lib/apiClient'
export const listProducts = (params) => api.get('/products', { params }).then((r) => r.data)
export const listServices = (params) => api.get('/services', { params }).then((r) => r.data)
export const getProduct = (slug) => api.get(`/products/slug/${slug}`).then((r) => r.data)
export const listCategories = () => api.get('/categories').then((r) => r.data)
export const getVendor = (slug) => api.get(`/vendors/${slug}`).then((r) => r.data)
export const listReviews = (slug) => api.get(`/products/${slug}/reviews`).then((r) => r.data)
export const createReview = (productId, payload) => api.post(`/products/${productId}/reviews`, payload).then((r) => r.data)
