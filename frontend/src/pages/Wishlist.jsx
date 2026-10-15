import { Heart, Trash2 } from "lucide-react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { getWishlist, removeWishlist } from "../api/shop";
import { Button, EmptyState, ErrorState, Skeleton } from "../components/ui";

export default function Wishlist() {
  const queryClient = useQueryClient();
  const query = useQuery({ queryKey: ["wishlist"], queryFn: getWishlist });
  const remove = useMutation({
    mutationFn: removeWishlist,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["wishlist"] }),
  });
  if (query.isLoading)
    return (
      <div className="mx-auto max-w-5xl px-4 py-8">
        <Skeleton className="h-8 w-40" />
        <Skeleton className="mt-8 h-40" />
      </div>
    );
  if (query.isError)
    return (
      <div className="mx-auto max-w-5xl px-4 py-8">
        <ErrorState onRetry={query.refetch} />
      </div>
    );
  return (
    <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6">
      <div className="flex items-center gap-3">
        <Heart className="text-brand-600" />
        <h1 className="text-2xl font-bold">Wishlist</h1>
      </div>
      {!query.data.items.length ? (
        <div className="mt-8">
          <EmptyState
            title="Your wishlist is empty"
            description="Save products you want to come back to."
            action={
              <Link to="/products">
                <Button>Explore products</Button>
              </Link>
            }
          />
        </div>
      ) : (
        <div className="mt-7 divide-y divide-line rounded-card border border-line bg-white">
          {query.data.items.map((item) => (
            <div
              key={item.uid}
              className="flex items-center justify-between gap-4 p-4"
            >
              <Link to={`/p/${item.product_slug}`} className="min-w-0">
                <p className="truncate text-sm font-semibold hover:text-brand-600">
                  {item.product_title}
                </p>
                <p className="mt-1 text-xs text-muted">
                  Saved on{" "}
                  {new Date(item.created_at).toLocaleDateString("en-IN")}
                </p>
              </Link>
              <button
                aria-label={`Remove ${item.product_title}`}
                onClick={() => remove.mutate(item.product_id)}
                className="grid h-10 w-10 shrink-0 place-items-center rounded-lg text-muted hover:bg-red-50 hover:text-red-600"
              >
                <Trash2 size={17} />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
