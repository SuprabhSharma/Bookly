export const formatCurrency = (value) => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(Number(value || 0))
export const formatDate = (value) => value ? new Intl.DateTimeFormat('en-IN', { dateStyle: 'medium' }).format(new Date(value)) : '—'
export const discountPercent = (price, mrp) => mrp && Number(mrp) > Number(price) ? Math.round((1 - Number(price) / Number(mrp)) * 100) : 0
export const productImage = (product, index = 0) => product?.images?.[index]?.url || `https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=640&q=80&auto=format&fit=crop`
