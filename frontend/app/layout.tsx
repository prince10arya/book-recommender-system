import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'BookMind — AI-Powered Book Recommendations',
  description:
    'Describe the book you want in plain English and discover your next great read. Powered by semantic vector search using ChromaDB and Google Generative AI Embeddings.',
  keywords: ['book recommendations', 'AI', 'semantic search', 'reading list'],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
