import Link from "next/link";

type FoodItem = {
  id: number;
  name: string;
  description: string | null;
  price: string | null;
  currency: string;
  is_available: boolean;
  average_rating: string;
  review_count: number;
  restaurant: {
    id: number;
    name: string;
    city: string;
  };
};

async function searchFood(query: string): Promise<FoodItem[]> {
  const response = await fetch(
    `${process.env.API_URL}/food-items?search=${encodeURIComponent(query)}&limit=20`,
    {
      cache: "no-store",
    },
  );

  if (!response.ok) {
    throw new Error("Failed to search food");
  }

  return response.json();
}

export default async function SearchPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>;
}) {
  const params = await searchParams;
  const query = params.q?.trim() ?? "";

  const foodItems = query ? await searchFood(query) : [];

  return (
    <main className="min-h-screen bg-white">
      {/* Header */}
      <header className="border-b border-gray-200">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-5">
          <Link href="/" className="text-2xl font-bold text-gray-900">
            Foodie
          </Link>

          <button className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50">
            Log in
          </button>
        </div>
      </header>

      {/* Search */}
      <section className="bg-gray-50">
        <div className="mx-auto max-w-6xl px-6 py-12">
          <Link
            href="/"
            className="mb-4 inline-flex items-center text-sm font-medium text-gray-600 hover:text-gray-900"
          >
            ← Back to home
          </Link>

          <h2 className="text-3xl font-bold text-gray-900">Search food</h2>

          <form action="/search" className="mt-6 flex max-w-2xl">
            ...
          </form>
        </div>
      </section>

      {/* Results */}
      <section className="mx-auto max-w-6xl px-6 py-12">
        {query && (
          <div className="mb-8">
            <h3 className="text-2xl font-bold text-gray-900">
              Results for &quot;{query}&quot;
            </h3>

            <p className="mt-2 text-gray-600">
              {foodItems.length} {foodItems.length === 1 ? "result" : "results"}{" "}
              found
            </p>
          </div>
        )}

        {!query && (
          <p className="text-gray-600">Enter a food name to search.</p>
        )}

        {query && foodItems.length === 0 && (
          <div className="rounded-2xl border border-gray-200 p-10 text-center">
            <p className="text-lg font-medium text-gray-900">No food found</p>

            <p className="mt-2 text-gray-500">
              Try searching for something else.
            </p>
          </div>
        )}

        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {foodItems.map((food) => (
            <FoodCard key={food.id} food={food} />
          ))}
        </div>
      </section>
    </main>
  );
}

function FoodCard({ food }: { food: FoodItem }) {
  const hasReviews = food.review_count > 0;

  return (
    <div className="overflow-hidden rounded-2xl border border-gray-200 bg-white transition hover:-translate-y-1 hover:shadow-lg">
      <div className="flex h-48 items-center justify-center bg-gray-100">
        <span className="text-5xl">🍛</span>
      </div>

      <div className="p-5">
        <h4 className="text-xl font-bold text-gray-900">{food.name}</h4>

        <p className="mt-1 text-gray-500">{food.restaurant.name}</p>

        <p className="text-sm text-gray-500">{food.restaurant.city}</p>

        <div className="mt-4">
          {hasReviews ? (
            <span className="font-semibold text-gray-900">
              ⭐ {food.average_rating} · {food.review_count}{" "}
              {food.review_count === 1 ? "review" : "reviews"}
            </span>
          ) : (
            <span className="text-sm text-gray-500">No reviews yet</span>
          )}
        </div>

        {food.price !== null && (
          <p className="mt-4 font-medium text-gray-700">₹{food.price}</p>
        )}

        {food.description && (
          <p className="mt-3 line-clamp-2 text-sm text-gray-600">
            {food.description}
          </p>
        )}
      </div>
    </div>
  );
}
