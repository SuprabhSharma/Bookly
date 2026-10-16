export const formatCurrency = (value) => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(Number(value || 0))
export const formatDate = (value) => value ? new Intl.DateTimeFormat('en-IN', { dateStyle: 'medium' }).format(new Date(value)) : '—'
export const discountPercent = (price, mrp) => {
  const sellingPrice = Number(price)
  const maximumRetailPrice = Number(mrp)
  if (!Number.isFinite(sellingPrice) || !Number.isFinite(maximumRetailPrice) || maximumRetailPrice <= sellingPrice || maximumRetailPrice <= 0) return 0
  return Math.round(((maximumRetailPrice - sellingPrice) / maximumRetailPrice) * 10000) / 100
}
export const productImage = (product, index = 0) => product?.images?.[index]?.url || `https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=640&q=80&auto=format&fit=crop`
