import { create } from 'zustand'

const KEY = 'marketplace_guest_cart'
const read = () => { try { return JSON.parse(localStorage.getItem(KEY) || '[]') } catch { return [] } }
export const useCartStore = create((set) => ({
  items: read(),
  add: (product, quantity = 1) => set((state) => { const found = state.items.find((item) => item.product.uid === product.uid); const nextQuantity = (found?.quantity || 0) + quantity; const items = found ? (nextQuantity > 0 ? state.items.map((item) => item.product.uid === product.uid ? { ...item, quantity: nextQuantity } : item) : state.items.filter((item) => item.product.uid !== product.uid)) : quantity > 0 ? [...state.items, { product, quantity }] : state.items; localStorage.setItem(KEY, JSON.stringify(items)); return { items } }),
  remove: (uid) => set((state) => { const items = state.items.filter((item) => item.product.uid !== uid); localStorage.setItem(KEY, JSON.stringify(items)); return { items } }),
  clear: () => { localStorage.removeItem(KEY); set({ items: [] }) },
}))
