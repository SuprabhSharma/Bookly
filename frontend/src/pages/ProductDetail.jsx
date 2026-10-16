import { useState } from "react";
import {
  Check,
  Heart,
  MapPin,
  ShoppingBag,
  Store,
  Zap,
} from "lucide-react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate, useParams } from "react-router-dom";
import { getProduct, listProducts, listReviews } from "../api/catalog";
import {
  addCartItem,
  addWishlist,
  getCart,
  getAddresses,
  getWishlist,
  removeCartItem,
  removeWishlist,
} from "../api/shop";
import { BackLink } from "../components/Page";
import ProductCard from "../components/ProductCard";
import ProductPrice from "../components/ProductPrice";
import { Badge, Button, ErrorState, Rating, Skeleton } from "../components/ui";
import { productImage } from "../lib/formatters";
import { useAuthStore } from "../store/authStore";
import { getErrorMessage } from "../lib/errors";

export default function ProductDetail() {
  const { slug } = useParams();
  const navigate = useNavigate();
  const [selectedImage, setSelectedImage] = useState(0);
  const [cartAdded, setCartAdded] = useState(false);
  const [cartError, setCartError] = useState("");
  const [cartMessage, setCartMessage] = useState("");
  const [wishlistMessage, setWishlistMessage] = useState("");
  const isLoggedIn = Boolean(useAuthStore((state) => state.accessToken));
  const productQuery = useQuery({
    queryKey: ["product", slug],
    queryFn: () => getProduct(slug),
  });
  const wishlistQuery = useQuery({
    queryKey: ["wishlist"],
    queryFn: getWishlist,
    enabled: isLoggedIn,
  });
  const addresses = useQuery({
    queryKey: ["addresses"],
    queryFn: getAddresses,
    enabled: isLoggedIn,
  });
  const cartQuery = useQuery({
    queryKey: ["cart"],
    queryFn: getCart,
    enabled: isLoggedIn,
  });
  const reviews = useQuery({
    queryKey: ["reviews", slug],
    queryFn: () => listReviews(slug),
    enabled: Boolean(productQuery.data),
  });
  const related = useQuery({
    queryKey: [
      "products",
      { vendor: productQuery.data?.vendor?.slug, page_size: 4 },
    ],
    queryFn: () =>
      listProducts({ vendor: productQuery.data.vendor.slug, page_size: 4 }),
    enabled: Boolean(productQuery.data?.vendor?.slug),
  });
  const queryClient = useQueryClient();
  const cart = useMutation({
    mutationFn: () => addCartItem(productQuery.data.uid),
    onSuccess: () => {
      setCartError("");
      setCartMessage("Product added to cart");
      setCartAdded(true);
      queryClient.invalidateQueries({ queryKey: ["cart"] });
    },
    onError: (error) => {
      setCartAdded(false);
      setCartError(getErrorMessage(error));
    },
  });
  const removeCart = useMutation({
    mutationFn: () => {
      const item = cartQuery.data?.items?.find(
        (cartItem) => cartItem.product_id === productQuery.data.uid,
      );
      return item ? removeCartItem(item.uid) : Promise.resolve();
    },
    onSuccess: () => {
      setCartAdded(false);
      setCartMessage("Product removed from cart");
      setCartError("");
      queryClient.invalidateQueries({ queryKey: ["cart"] });
    },
    onError: (error) => setCartError(getErrorMessage(error)),
  });
  const buyNow = useMutation({
    mutationFn: () => addCartItem(productQuery.data.uid),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cart"] });
      navigate(isLoggedIn ? "/checkout" : "/account?next=/checkout");
    },
    onError: (error) => setCartError(getErrorMessage(error)),
  });
  const wishlist = useMutation({
    mutationFn: (saved) =>
      saved
        ? removeWishlist(productQuery.data.uid)
        : addWishlist(productQuery.data.uid),
    onSuccess: (_, wasSaved) => {
      queryClient.invalidateQueries({ queryKey: ["wishlist"] });
      setWishlistMessage(
        wasSaved
          ? "Product removed from wishlist"
          : "Product added to wishlist",
      );
    },
    onError: (error) => setWishlistMessage(getErrorMessage(error)),
  });
  if (productQuery.isLoading)
    return (
      <div className="mx-auto max-w-7xl px-4 py-8">
        <Skeleton className="h-5 w-20" />
        <div className="mt-8 grid gap-8 md:grid-cols-2">
          <Skeleton className="aspect-square" />
          <div>
            <Skeleton className="h-8 w-3/4" />
            <Skeleton className="mt-5 h-12 w-1/3" />
          </div>
        </div>
      </div>
    );
  if (productQuery.isError)
    return (
      <div className="mx-auto max-w-7xl px-4 py-10">
        <ErrorState onRetry={productQuery.refetch} />
      </div>
    );
  const product = productQuery.data;
  const inCart =
    cartAdded ||
    Boolean(
      cartQuery.data?.items?.some((item) => item.product_id === product.uid),
    );
  const saved = Boolean(
    wishlistQuery.data?.items?.some((item) => item.product_id === product.uid),
  );
  const toggleWishlist = () => {
    if (!isLoggedIn) {
      navigate(`/account?next=${encodeURIComponent(`/p/${slug}`)}`);
      return;
    }
    setWishlistMessage("");
    wishlist.mutate(saved);
  };
  const images = product.images?.length ? product.images : [{}];
  const add = () => {
    setCartError("");
    setCartMessage("");
    if (!isLoggedIn) {
      navigate(`/account?next=${encodeURIComponent(`/p/${slug}`)}`);
      return;
    }
    if (inCart) {
      removeCart.mutate();
      return;
    }
    cart.mutate();
  };
  const buy = () => {
    setCartError("");
    setCartMessage("");
    if (!isLoggedIn) {
      navigate("/account?next=/checkout");
      return;
    }
    buyNow.mutate();
  };
  const defaultAddress =
    addresses.data?.find((address) => address.is_default) ||
    addresses.data?.[0];
  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <BackLink />
      <div className="grid gap-8 lg:grid-cols-[1fr_1fr]">
        <div className="grid gap-3 sm:grid-cols-[80px_1fr]">
          <div className="order-2 flex gap-2 overflow-auto sm:order-1 sm:flex-col">
            {images.map((image, index) => (
              <button
                key={image.uid || index}
                onClick={() => setSelectedImage(index)}
                className={`shrink-0 overflow-hidden rounded-lg border-2 ${selectedImage === index ? "border-brand-600" : "border-transparent"}`}
              >
                <img
                  src={image.url || productImage(product)}
                  alt=""
                  width="72"
                  height="72"
                  className="h-16 w-16 object-cover"
                />
              </button>
            ))}
          </div>
          <div className="order-1 overflow-hidden rounded-card bg-slate-100 sm:order-2">
            <img
              src={images[selectedImage]?.url || productImage(product)}
              alt={product.title}
              width="800"
              height="800"
              className="aspect-square w-full object-cover"
            />
          </div>
        </div>
        <div>
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="text-sm text-muted">{product.vendor?.store_name}</p>
              <h1 className="mt-2 text-2xl font-bold tracking-tight text-ink sm:text-3xl">
                {product.title}
              </h1>
            </div>
            <button
              aria-label={saved ? "Remove from wishlist" : "Add to wishlist"}
              title={saved ? "Remove from wishlist" : "Add to wishlist"}
              onClick={toggleWishlist}
              disabled={wishlist.isPending}
              className={`grid h-11 w-11 shrink-0 place-items-center rounded-full border transition ${
                saved
                  ? "border-red-200 bg-red-50 text-red-500"
                  : "border-line text-muted hover:border-red-200 hover:bg-red-50 hover:text-red-500"
              } disabled:opacity-40`}
            >
              <Heart size={21} fill={saved ? "currentColor" : "none"} />
            </button>
          </div>
          {wishlistMessage && (
            <p className="mt-2 text-sm text-muted" role="status">
              {wishlistMessage}
            </p>
          )}
          <div className="mt-4 flex items-center gap-3">
            <Rating value={product.rating_avg} count={product.rating_count} />
            {product.stock > 0 ? (
              <Badge tone="success">In stock</Badge>
            ) : (
              <Badge tone="danger">Out of stock</Badge>
            )}
          </div>
          <ProductPrice
            price={product.price}
            mrp={product.mrp}
            inline
            className="mt-6"
          />
          <div className="mt-5 rounded-lg border border-line bg-slate-50 p-4">
            <div className="flex items-center gap-2 text-sm font-semibold">
              <MapPin size={17} className="text-brand-600" />
              Delivery
            </div>
            {defaultAddress ? (
              <p className="mt-2 text-sm text-muted">
                Deliver to <strong className="text-ink">{defaultAddress.name}</strong>{" "}
                · {defaultAddress.city}, {defaultAddress.pincode}
              </p>
            ) : (
              <p className="mt-2 text-sm text-muted">
                Sign in at checkout to add or select a delivery address.
              </p>
            )}
            <Link
              to={isLoggedIn ? "/checkout" : "/account?next=/checkout"}
              className="mt-2 inline-block text-sm font-semibold text-brand-600"
            >
              {defaultAddress ? "Change address" : "Add delivery address"}
            </Link>
          </div>
          <div className="my-7 h-px bg-line" />
          <p className="whitespace-pre-line text-sm leading-7 text-muted">
            {product.description ||
              "A carefully selected product from one of our trusted Tavilo stores."}
          </p>
          {product.attributes && (
            <div className="mt-6 grid grid-cols-2 gap-3">
              {Object.entries(product.attributes).map(([key, value]) => (
                <div key={key} className="rounded-lg bg-slate-50 p-3">
                  <p className="text-xs capitalize text-muted">
                    {key.replace("_", " ")}
                  </p>
                  <p className="mt-1 text-sm font-semibold">{String(value)}</p>
                </div>
              ))}
            </div>
          )}
          <div className="mt-8 flex flex-wrap items-center gap-3">
            <Button
              className={`flex-1 sm:flex-none ${inCart ? "bg-emerald-600 hover:bg-emerald-700" : "bg-brand-600 hover:bg-brand-700"}`}
              disabled={
                (!product.stock && !inCart) ||
                cart.isPending ||
                removeCart.isPending
              }
              loading={cart.isPending || removeCart.isPending}
              onClick={add}
            >
              {inCart ? <Check size={19} strokeWidth={3} /> : <ShoppingBag size={19} strokeWidth={2.25} />}
              {inCart ? "In cart" : "Add to cart"}
            </Button>
            <Button
              className="flex-1 sm:flex-none"
              disabled={!product.stock || buyNow.isPending}
              loading={buyNow.isPending}
              onClick={buy}
            >
              <Zap size={17} />
              Buy now
            </Button>
          </div>
          {cartMessage && (
            <p className="mt-3 text-sm font-semibold text-emerald-700" role="status">
              {cartMessage}
            </p>
          )}
          {cartError && (
            <p className="mt-3 text-sm text-red-600">{cartError}</p>
          )}
          <Link
            to={`/store/${product.vendor?.slug}`}
            className="mt-7 flex items-center gap-3 rounded-card border border-line p-4 hover:border-brand-100"
          >
            <span className="grid h-10 w-10 place-items-center rounded-full bg-brand-50 text-brand-600">
              <Store size={18} />
            </span>
            <div>
              <p className="text-xs text-muted">Sold by</p>
              <p className="text-sm font-semibold">
                {product.vendor?.store_name}
              </p>
            </div>
            <span className="ml-auto text-sm font-semibold text-brand-600">
              Visit store
            </span>
          </Link>
        </div>
      </div>
      {reviews.data?.length > 0 && (
        <section className="mt-14 border-t border-line pt-10">
          <h2 className="text-xl font-bold">Customer reviews</h2>
          <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {reviews.data.slice(0, 6).map((review) => (
              <div
                key={review.uid}
                className="rounded-card border border-line bg-white p-4"
              >
                <Rating value={review.rating} />
                <p className="mt-3 text-sm leading-6 text-muted">
                  {review.review_text}
                </p>
              </div>
            ))}
          </div>
        </section>
      )}
      {related.data?.items?.length > 0 && (
        <section className="mt-14 border-t border-line pt-10">
          <h2 className="mb-5 text-xl font-bold">
            More from {product.vendor?.store_name}
          </h2>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            {related.data.items
              .filter((item) => item.uid !== product.uid)
              .map((item) => (
                <ProductCard key={item.uid} product={item} />
              ))}
          </div>
        </section>
      )}
    </div>
  );
}
