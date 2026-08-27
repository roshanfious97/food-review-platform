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

async function getFoodItems(): Promise<FoodItem[]> {
  const response = await fetch(
    `${process.env.API_URL}/food-items?limit=20`,
    {
      cache: "no-store",
    }
  );

  if (!response.ok) {
    throw new Error("Failed to fetch food items");
  }

  return response.json();
}

export default async function Home() {
  const foodItems = await getFoodItems();

  return (
    <main className="min-h-screen bg-white">
      {/* Header */}
      <header className="border-b border-gray-200">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-5">
          <h1 className="text-2xl font-bold text-gray-900">
            Foodie
          </h1>

          <button className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50">
            Log in
          </button>
        </div>
      </header>

      {/* Hero */}
      <section className="bg-gray-50">
        <div className="mx-auto max-w-6xl px-6 py-20">
          <div className="max-w-3xl">
            <p className="mb-4 text-sm font-semibold uppercase tracking-wide text-gray-500">
              Discover food, not just restaurants
            </p>

            <h2 className="text-5xl font-bold tracking-tight text-gray-900">
              Find out what&apos;s actually worth eating.
            </h2>

            <p className="mt-6 text-lg leading-8 text-gray-600">
              Discover dishes people love, read reviews from real diners,
              and find your next favorite meal.
            </p>

            <div className="mt-8 flex max-w-2xl">
              <input
                type="text"
                placeholder="Search for biryani, dosa, pizza..."
                className="w-full rounded-l-xl border border-gray-300 bg-white px-5 py-4 text-gray-900 outline-none focus:border-gray-500"
              />

              <button className="rounded-r-xl bg-gray-900 px-7 py-4 font-medium text-white hover:bg-gray-800">
                Search
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Food */}
      <section className="mx-auto max-w-6xl px-6 py-16">
        <div className="mb-8">
          <h3 className="text-2xl font-bold text-gray-900">
            Popular food in Chennai
          </h3>

          <p className="mt-2 text-gray-600">
            See what people are eating and reviewing.
          </p>
        </div>

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
        <h4 className="text-xl font-bold text-gray-900">
          {food.name}
        </h4>

        <p className="mt-1 text-gray-500">
          {food.restaurant.name}
        </p>

        <p className="text-sm text-gray-500">
          {food.restaurant.city}
        </p>

        <div className="mt-4">
          {hasReviews ? (
            <span className="font-semibold text-gray-900">
              ⭐ {food.average_rating} · {food.review_count}{" "}
              {food.review_count === 1 ? "review" : "reviews"}
            </span>
          ) : (
            <span className="text-sm text-gray-500">
              No reviews yet
            </span>
          )}
        </div>

        {food.price !== null && (
          <p className="mt-4 font-medium text-gray-700">
            ₹{food.price}
          </p>
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