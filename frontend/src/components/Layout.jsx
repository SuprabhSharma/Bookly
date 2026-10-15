import { useEffect, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Link,
  NavLink,
  Outlet,
  useLocation,
  useNavigate,
} from "react-router-dom";
import {
  Heart,
  Home,
  Menu,
  Search,
  ShoppingBag,
  Store,
  UserRound,
  X,
} from "lucide-react";
import { brand } from "../config/brand";
import { useAuthStore } from "../store/authStore";
import { api } from "../lib/apiClient";
import { getCart } from "../api/shop";

const nav = [
  { to: "/", label: "Home", icon: Home },
  { to: "/products", label: "Shop", icon: Store },
  { to: "/wishlist", label: "Wishlist", icon: Heart },
  { to: "/cart", label: "Cart", icon: ShoppingBag },
  { to: "/account", label: "Account", icon: UserRound },
];
export default function ShopLayout() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [query, setQuery] = useState("");
  const navigate = useNavigate();
  const location = useLocation();
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);
  const loggedIn = Boolean(useAuthStore((state) => state.accessToken));
  const cart = useQuery({
    queryKey: ["cart"],
    queryFn: getCart,
    enabled: loggedIn,
  });
  const queryClient = useQueryClient();
  useEffect(() => {
    setMenuOpen(false);
  }, [location.pathname]);
  const submitSearch = (event) => {
    event.preventDefault();
    if (query.trim()) navigate(`/search?q=${encodeURIComponent(query.trim())}`);
  };
  const signOut = async () => {
    try {
      await api.post("/auth/logout", {
        refresh_token: useAuthStore.getState().refreshToken,
      });
    } catch {
      /* session is cleared locally */
    }
    queryClient.clear();
    logout();
    navigate("/");
  };
  const count = loggedIn
    ? cart.data?.items?.reduce((sum, item) => sum + item.quantity, 0) || 0
    : 0;
  return (
    <div className="min-h-screen bg-slate-50 pb-20 text-ink md:pb-0">
      <header className="sticky top-0 z-30 border-b border-line bg-white">
        <div className="mx-auto flex h-16 max-w-7xl items-center gap-3 px-4 sm:px-6 lg:px-8">
          <button
            aria-label="Open menu"
            onClick={() => setMenuOpen(true)}
            className="grid h-11 w-11 place-items-center rounded-lg text-ink hover:bg-slate-100 md:hidden"
          >
            <Menu size={21} />
          </button>
          <Link to="/" className="flex w-28 shrink-0 items-center sm:w-32">
            <img
              src={brand.logo}
              alt={brand.logoAlt}
              className="h-auto w-full object-contain"
              decoding="async"
            />
          </Link>
          <form
            onSubmit={submitSearch}
            className="ml-auto flex max-w-xl flex-1 items-center rounded-lg bg-slate-100 px-3 focus-within:ring-2 focus-within:ring-brand-100"
          >
            <Search size={18} className="shrink-0 text-muted" />
            <input
              aria-label="Search products"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search for products, brands and more"
              className="h-11 w-full bg-transparent px-2 text-sm outline-none placeholder:text-muted"
            />
          </form>
          <nav className="hidden items-center gap-1 md:flex">
            <NavLink
              to="/account"
              className="rounded-lg px-3 py-2 text-sm font-medium hover:bg-slate-100"
            >
              {user
                ? `Hi, ${user.first_name || user.email?.split("@")[0]}`
                : "Sign in"}
            </NavLink>
            {user && (
              <button
                onClick={signOut}
                className="rounded-lg px-3 py-2 text-sm text-muted hover:bg-slate-100"
              >
                Log out
              </button>
            )}
            <Link
              to="/cart"
              className="relative grid h-11 w-11 place-items-center rounded-lg hover:bg-slate-100"
            >
              <ShoppingBag size={20} />
              {count > 0 && (
                <span className="absolute right-0 top-0 grid h-5 min-w-5 place-items-center rounded-full bg-brand-600 px-1 text-[10px] font-bold text-white">
                  {count}
                </span>
              )}
            </Link>
          </nav>
        </div>
        <div className="hidden border-t border-line md:block">
          <div className="mx-auto flex h-11 max-w-7xl items-center gap-6 px-4 text-sm text-muted sm:px-6 lg:px-8">
            <Link to="/products" className="font-medium hover:text-brand-600">
              All products
            </Link>
            <Link to="/products?sort=rating" className="hover:text-brand-600">
              Top rated
            </Link>
            <Link to="/products?sort=newest" className="hover:text-brand-600">
              New arrivals
            </Link>
          </div>
        </div>
      </header>
      {menuOpen && (
        <div className="fixed inset-0 z-50 md:hidden">
          <button
            aria-label="Close menu"
            className="absolute inset-0 bg-slate-900/40"
            onClick={() => setMenuOpen(false)}
          />
          <aside className="relative h-full w-80 max-w-[85vw] bg-white p-5 shadow-float">
            <div className="flex items-center justify-between">
              <Link to="/" className="flex w-32 items-center">
                <img
                  src={brand.logo}
                  alt={brand.logoAlt}
                  className="h-auto w-full object-contain"
                  decoding="async"
                />
              </Link>
              <button aria-label="Close" onClick={() => setMenuOpen(false)}>
                <X />
              </button>
            </div>
            <div className="mt-8 space-y-2">
              {nav.map(({ to, label, icon: Icon }) => (
                <NavLink
                  key={to}
                  to={to}
                  className="flex min-h-11 items-center gap-3 rounded-lg px-3 text-sm font-medium hover:bg-slate-100"
                >
                  <Icon size={18} />
                  {label}
                </NavLink>
              ))}
            </div>
          </aside>
        </div>
      )}
      <main>
        <Outlet />
      </main>
      <nav className="fixed inset-x-0 bottom-0 z-30 flex h-[calc(4rem+env(safe-area-inset-bottom))] items-start justify-around border-t border-line bg-white px-2 pt-2 md:hidden">
        {nav.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `relative flex min-w-14 flex-col items-center gap-1 text-[11px] ${isActive ? "font-semibold text-brand-600" : "text-muted"}`
            }
          >
            <Icon size={19} />
            <span>{label}</span>
            {to === "/cart" && count > 0 && (
              <span className="absolute right-1 top-[-4px] grid h-4 min-w-4 items-center rounded-full bg-brand-600 px-1 text-[9px] text-white">
                {count}
              </span>
            )}
          </NavLink>
        ))}
      </nav>
    </div>
  );
}
