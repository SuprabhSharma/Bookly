import { Heart, ShoppingBag } from "lucide-react";
import { Link } from "react-router-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { addCartItem, addWishlist } from "../api/shop";
import {
  formatCurrency,
  discountPercent,
  productImage,
} from "../lib/formatters";
import { useAuthStore } from "../store/authStore";
import { useCartStore } from "../store/cartStore";
import { Button, Rating } from "./ui";

export default function ProductCard({ product }) {
  const isLoggedIn = Boolean(useAuthStore((state) => state.accessToken));
  const addGuest = useCartStore((state) => state.add);
  const queryClient = useQueryClient();
  const cartMutation = useMutation({
    mutationFn: () => addCartItem(product.uid),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["cart"] }),
  });
  const wishlistMutation = useMutation({
    mutationFn: () => addWishlist(product.uid),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["wishlist"] }),
  });
  const addToCart = () =>
    isLoggedIn ? cartMutation.mutate() : addGuest(product);
  return (
    <article className="group flex min-w-0 flex-col rounded-card border border-line bg-white p-2.5 shadow-card transition hover:-translate-y-0.5 hover:shadow-float sm:p-3">
      <Link
        to={`/p/${product.slug}`}
        className="relative block overflow-hidden rounded-lg bg-slate-100"
      >
        <img
          src={productImage(product)}
          alt={product.title}
          width="640"
          height="640"
          loading="lazy"
          decoding="async"
          className="aspect-square w-full object-cover transition duration-300 group-hover:scale-105"
        />
        {product.stock === 0 && (
          <span className="absolute left-2 top-2 rounded bg-slate-900/80 px-2 py-1 text-xs text-white">
            Sold out
          </span>
        )}
      </Link>
      <div className="flex flex-1 flex-col px-1 pt-3">
        {" "}
        <p className="mb-1 truncate text-xs text-muted">
          {product.vendor?.store_name || "Tavilo store"}
        </p>
        <Link
          to={`/p/${product.slug}`}
          className="line-clamp-2 min-h-10 text-sm font-semibold leading-5 text-ink hover:text-brand-600"
        >
          {product.title}
        </Link>
        <div className="mt-2">
          <Rating value={product.rating_avg} count={product.rating_count} />
        </div>
        <div className="mt-auto flex items-end justify-between gap-2 pt-3">
          <div>
            <p className="font-bold text-ink">
              {formatCurrency(product.price)}
            </p>
            {product.mrp && Number(product.mrp) > Number(product.price) && (
              <p className="text-xs text-muted line-through">
                {formatCurrency(product.mrp)}{" "}
                <span className="ml-1 text-emerald-600 no-underline">
                  {discountPercent(product.price, product.mrp)}% off
                </span>
              </p>
            )}
          </div>
          <div className="flex gap-1">
            <button
              aria-label="Add to wishlist"
              onClick={() => isLoggedIn && wishlistMutation.mutate()}
              className="grid h-9 w-9 place-items-center rounded-lg border border-line text-muted hover:bg-red-50 hover:text-red-500 disabled:opacity-40"
              disabled={!isLoggedIn || wishlistMutation.isPending}
            >
              <Heart size={16} />
            </button>
            <Button
              aria-label="Add to cart"
              className="h-9 min-h-9 w-9 px-0"
              onClick={addToCart}
              disabled={product.stock === 0 || cartMutation.isPending}
            >
              <ShoppingBag size={16} />
            </Button>
          </div>
        </div>
      </div>
    </article>
  );
}
