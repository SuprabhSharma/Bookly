import { useState } from "react";
import { Check, Heart, ShoppingBag } from "lucide-react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  addCartItem,
  addWishlist,
  getCart,
  getWishlist,
  removeCartItem,
  removeWishlist,
} from "../api/shop";
import {
  formatCurrency,
  discountPercent,
  productImage,
} from "../lib/formatters";
import { useAuthStore } from "../store/authStore";
import { getErrorMessage } from "../lib/errors";
import { Button, Rating } from "./ui";

export default function ProductCard({ product, showCart = true }) {
  const isLoggedIn = Boolean(useAuthStore((state) => state.accessToken));
  const navigate = useNavigate();
  const location = useLocation();
  const [message, setMessage] = useState("");
  const [cartAdded, setCartAdded] = useState(false);
  const queryClient = useQueryClient();
  const cart = useQuery({
    queryKey: ["cart"],
    queryFn: getCart,
    enabled: isLoggedIn,
  });
  const wishlist = useQuery({
    queryKey: ["wishlist"],
    queryFn: getWishlist,
    enabled: isLoggedIn,
  });
  const saved = Boolean(
    wishlist.data?.items?.some((item) => item.product_id === product.uid),
  );
  const wishlistMutation = useMutation({
    mutationFn: () =>
      saved ? removeWishlist(product.uid) : addWishlist(product.uid),
    onSuccess: (_, wasSaved) => {
      queryClient.invalidateQueries({ queryKey: ["wishlist"] });
      setMessage(
        wasSaved
          ? "Product removed from wishlist"
          : "Product added to wishlist",
      );
    },
    onError: (error) => setMessage(getErrorMessage(error)),
  });
  const toggleWishlist = () => {
    if (!isLoggedIn) {
      navigate(`/account?next=${encodeURIComponent(location.pathname)}`);
      return;
    }
    setMessage("");
    wishlistMutation.mutate(saved);
  };
  const cartMutation = useMutation({
    mutationFn: () => addCartItem(product.uid),
    onSuccess: () => {
      setCartAdded(true);
      setMessage("Product added to cart");
      queryClient.invalidateQueries({ queryKey: ["cart"] });
    },
    onError: (error) => setMessage(getErrorMessage(error)),
  });
  const removeCartMutation = useMutation({
    mutationFn: async () => {
      const latestCart = isLoggedIn ? await getCart() : null;
      const item = latestCart?.items?.find(
        (cartItem) => cartItem.product_id === product.uid,
      );
      if (!item) return Promise.resolve();
      return removeCartItem(item.uid);
    },
    onSuccess: () => {
      setCartAdded(false);
      setMessage("Product removed from cart");
      queryClient.invalidateQueries({ queryKey: ["cart"] });
    },
    onError: (error) => setMessage(getErrorMessage(error)),
  });
  const inCart =
    cartAdded ||
    Boolean(cart.data?.items?.some((item) => item.product_id === product.uid));
  const addToCart = () => {
    setMessage("");
    if (!isLoggedIn) {
      navigate(`/account?next=${encodeURIComponent(location.pathname)}`);
      return;
    }
    if (inCart) {
      removeCartMutation.mutate();
      return;
    }
    cartMutation.mutate();
  };

  const discount = discountPercent(product.price, product.mrp);

  return (
    <article className="group flex min-w-0 flex-col overflow-hidden rounded-card border border-line bg-white p-2.5 shadow-card transition hover:-translate-y-0.5 hover:shadow-float sm:p-3">
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
          className="aspect-[1.05] w-full object-cover transition duration-300 group-hover:scale-105"
        />
        {product.stock === 0 && (
          <span className="absolute left-2 top-2 rounded bg-slate-900/80 px-2 py-1 text-xs text-white">
            Sold out
          </span>
        )}
      </Link>
      <div className="flex min-h-0 flex-1 flex-col px-1 pt-2">
        <p className="mb-1 truncate text-xs text-muted">
          {product.vendor?.store_name || "Tavilo store"}
        </p>
        <Link
          to={`/p/${product.slug}`}
          className="truncate text-sm font-semibold leading-5 text-ink hover:text-brand-600"
        >
          {product.title}
        </Link>
        <div className="mt-1">
          <Rating value={product.rating_avg} count={product.rating_count} compact />
        </div>
        <div className="flex items-end justify-between gap-2 pt-1">
          <div className="min-w-0">
            <p className="truncate font-bold text-ink">
              {formatCurrency(product.price)}
            </p>
            {discount > 0 && (
              <p className="truncate text-xs text-muted">
                <span className="line-through">
                  {formatCurrency(product.mrp)}
                </span>{" "}
                <span className="font-semibold text-emerald-600">
                  {discount}% off
                </span>
              </p>
            )}
          </div>
          <div className="flex shrink-0 items-center gap-1">
            {showCart && (
              <Button
                aria-label={inCart ? "Remove from cart" : "Add to cart"}
                title={inCart ? "Remove from cart" : "Add to cart"}
                className={`h-9 min-h-9 w-9 px-0 ${
                  inCart
                    ? "bg-emerald-600 text-white shadow-[0_0_0_3px_rgba(16,185,129,0.18)] hover:bg-emerald-700"
                    : ""
                }`}
                onClick={addToCart}
                disabled={
                  (!product.stock && !inCart) ||
                  cartMutation.isPending ||
                  removeCartMutation.isPending
                }
              >
                {inCart ? (
                  <Check size={20} strokeWidth={3} />
                ) : (
                  <ShoppingBag size={16} />
                )}
              </Button>
            )}
            <button
              aria-label={saved ? "Remove from wishlist" : "Add to wishlist"}
              title={saved ? "Remove from wishlist" : "Add to wishlist"}
              onClick={toggleWishlist}
              className={`grid h-9 w-9 shrink-0 place-items-center rounded-full border transition ${
                saved
                  ? "border-red-200 bg-red-50 text-red-500"
                  : "border-line text-muted hover:border-red-200 hover:bg-red-50 hover:text-red-500"
              } disabled:opacity-40`}
              disabled={wishlistMutation.isPending}
            >
              <Heart size={17} fill={saved ? "currentColor" : "none"} />
            </button>
          </div>
        </div>
        {message && (
          <p className="mt-1 truncate text-[11px] text-muted" role="status">
            {message}
          </p>
        )}
      </div>
    </article>
  );
}
