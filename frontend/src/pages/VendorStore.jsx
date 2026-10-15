import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { getVendor, listProducts, listServices } from "../api/catalog";
import ProductCard from "../components/ProductCard";
import { BackLink, ProductGridSkeleton } from "../components/Page";
import { ErrorState } from "../components/ui";

export default function VendorStore() {
  const { slug } = useParams();
  const vendor = useQuery({
    queryKey: ["vendor", slug],
    queryFn: () => getVendor(slug),
  });
  const products = useQuery({
    queryKey: ["products", { vendor: slug }],
    queryFn: () => listProducts({ vendor: slug, page_size: 20 }),
  });
  const services = useQuery({
    queryKey: ["services", { vendor: slug }],
    queryFn: () => listServices({ vendor: slug, page_size: 20 }),
  });
  if (vendor.isLoading)
    return (
      <div className="mx-auto max-w-7xl px-4 py-8">
        <ProductGridSkeleton />
      </div>
    );
  if (vendor.isError)
    return (
      <div className="mx-auto max-w-7xl px-4 py-8">
        <ErrorState onRetry={vendor.refetch} />
      </div>
    );
  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <BackLink />
      <section className="rounded-card bg-brand-700 p-6 text-white sm:p-10">
        <div className="flex flex-col gap-5 sm:flex-row sm:items-center">
          <div className="grid h-20 w-20 shrink-0 place-items-center rounded-2xl bg-white text-3xl font-bold text-brand-600">
            {vendor.data.store_name?.[0]}
          </div>
          <div>
            <p className="text-sm text-blue-100">Tavilo store</p>
            <h1 className="mt-1 text-3xl font-bold">
              {vendor.data.store_name}
            </h1>
            <p className="mt-2 max-w-xl text-sm leading-6 text-blue-100">
              {vendor.data.description ||
                "A trusted independent store on Tavilo."}
            </p>
          </div>
        </div>
      </section>
      <div className="mt-10">
        {products.isLoading ? (
          <ProductGridSkeleton />
        ) : products.isError ? (
          <ErrorState onRetry={products.refetch} />
        ) : (
          <>
            <h2 className="mb-5 text-xl font-bold">
              Store products{" "}
              <span className="ml-2 text-sm font-normal text-muted">
                {products.data.total}
              </span>
            </h2>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
              {products.data.items.map((product) => (
                <ProductCard key={product.uid} product={product} />
              ))}
            </div>
          </>
        )}
        {services.isLoading ? (
          <div className="mt-10">
            <ProductGridSkeleton />
          </div>
        ) : services.isError ? null : services.data.total > 0 ? (
          <section className="mt-10">
            <h2 className="mb-5 text-xl font-bold">
              Services{" "}
              <span className="ml-2 text-sm font-normal text-muted">
                {services.data.total}
              </span>
            </h2>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {services.data.items.map((service) => (
                <article
                  key={service.uid}
                  className="rounded-card border border-line bg-white p-5"
                >
                  <h3 className="font-bold">{service.title}</h3>
                  <p className="mt-2 text-sm leading-6 text-muted">
                    {service.description || "Service offered by this store."}
                  </p>
                  <p className="mt-4 text-sm font-semibold text-brand-700">
                    {service.price} Â· {service.duration_minutes} minutes
                  </p>
                </article>
              ))}
            </div>
          </section>
        ) : null}
      </div>
    </div>
  );
}
