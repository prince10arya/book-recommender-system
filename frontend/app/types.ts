export interface Book {
  isbn13: string;
  isbn10: string;
  title: string;
  title_and_subtitle: string;
  authors: string;
  categories: string;
  thumbnail: string;
  description: string;
  published_year: number | null;
  average_rating: number | null;
  num_pages: number | null;
  ratings_count: number | null;
  similarity_score: number;
}

export interface RecommendResponse {
  query: string;
  results: Book[];
  total: number;
}
