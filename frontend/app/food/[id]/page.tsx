import Link from "next/link";

type FoodItem = {
  id: number;
  name: string;
  description: string | null;
  price: string | null;
  currency: string;
  is_available: boolean;
  restaurant_id: number;
  average_rating: string;
  review_count: number;
  restaurant: {
    id: number;
    name: string;
    city: string;
  };
};

type Review = {
  id: number;
  rating: number;
  body: string | null;
  would_order_again: boolean | null;
  user_id: number;
  food_item_id: number;
  created_at: string;
  updated_at: string;
  user: {
    id: number;
    username: string;
    display_name: string;
  };
};

async function getFoodItem(id: string): Promise<FoodItem> {
  const response = await fetch(`${process.env.API_URL}/food-items/${id}`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Food item not found");
  }

  return response.json();
}

async function getReviews(id: string): Promise<Review[]> {
  const response = await fetch(
    `${process.env.API_URL}/food-items/${id}/reviews`,
    {
      cache: "no-store",
    }
  );

  if (!response.ok) {
    throw new Error("Failed to fetch reviews");
  }

  const data = await response.json();

  console.log("REVIEWS FROM API:", JSON.stringify(data, null, 2));

  return data;
}
export default async function FoodPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  const [food, reviews] = await Promise.all([getFoodItem(id), getReviews(id)]);

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

      {/* Food details */}
      <section className="mx-auto max-w-6xl px-6 py-12">
        <Link
          href="/search"
          className="inline-flex text-sm font-medium text-gray-600 hover:text-gray-900"
        >
          ← Back to search
        </Link>

        <div className="mt-8 grid gap-10 md:grid-cols-2">
          {/* Image */}
          <div className="flex min-h-[400px] items-center justify-center rounded-3xl bg-gray-100">
            <span className="text-8xl">🍛</span>
          </div>

          {/* Information */}
          <div className="flex flex-col justify-center">
            <p className="text-sm font-semibold uppercase tracking-wide text-gray-500">
              Food item
            </p>

            <h1 className="mt-3 text-4xl font-bold tracking-tight text-gray-900">
              {food.name}
            </h1>

            <p className="mt-3 text-gray-500">
              {food.restaurant.name} · {food.restaurant.city}
            </p>

            <div className="mt-6 flex items-center gap-4">
              {food.review_count > 0 ? (
                <>
                  <span className="text-xl font-semibold text-gray-900">
                    ⭐ {food.average_rating}
                  </span>

                  <span className="text-gray-500">
                    {food.review_count}{" "}
                    {food.review_count === 1 ? "review" : "reviews"}
                  </span>
                </>
              ) : (
                <span className="text-gray-500">No reviews yet</span>
              )}
            </div>

            {food.price !== null && (
              <p className="mt-6 text-2xl font-semibold text-gray-900">
                ₹{food.price}
              </p>
            )}

            {food.description && (
              <p className="mt-6 max-w-xl leading-7 text-gray-600">
                {food.description}
              </p>
            )}

            {!food.is_available && (
              <p className="mt-6 font-medium text-red-600">
                Currently unavailable
              </p>
            )}

            <button className="mt-8 w-fit rounded-xl bg-gray-900 px-6 py-3 font-medium text-white hover:bg-gray-800">
              Write a review
            </button>
          </div>
        </div>
      </section>

      {/* Reviews */}
      <section className="border-t border-gray-200">
        <div className="mx-auto max-w-6xl px-6 py-12">
          <h2 className="text-2xl font-bold text-gray-900">Reviews</h2>

          <div className="mt-8 space-y-6">
            {reviews.length === 0 ? (
              <div className="rounded-2xl border border-gray-200 p-8 text-center">
                <p className="font-medium text-gray-900">No reviews yet</p>

                <p className="mt-2 text-gray-500">
                  Be the first person to review this food.
                </p>
              </div>
            ) : (
              reviews.map((review) => (
                <ReviewCard key={review.id} review={review} />
              ))
            )}
          </div>
        </div>
      </section>
    </main>
  );
}

function ReviewCard({ review }: { review: Review }) {
  return (
    <article className="rounded-2xl border border-gray-200 p-6">
      <div className="flex items-center justify-between">
        <div className="font-semibold text-gray-900">
          {"⭐".repeat(review.rating)}
        </div>

        {review.would_order_again !== null && (
          <span className="text-sm text-gray-500">
            {review.would_order_again
              ? "Would order again"
              : "Wouldn't order again"}
          </span>
        )}
      </div>

      {review.body && (
        <p className="mt-4 leading-7 text-gray-700">
          {review.body}
        </p>
      )}

      <p className="mt-4 text-sm font-medium text-gray-700">
        {review.user.display_name}
      </p>
    </article>
  );
}
