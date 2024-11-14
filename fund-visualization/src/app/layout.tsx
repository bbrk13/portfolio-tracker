import { Providers } from '@/store/provider';
import './globals.css';

export const metadata = {
  title: 'Fund Data Visualization',
  description: 'Investment fund data visualization and portfolio management',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-gray-100">
        <Providers>
          <nav className="bg-white shadow-sm">
            <div className="container mx-auto px-4">
              <div className="flex justify-between h-16 items-center">
                <a href="/" className="text-xl font-bold">Fund Visualization</a>
                <div className="flex space-x-4">
                  <a href="/" className="hover:text-blue-600">Home</a>
                  <a href="/portfolio" className="hover:text-blue-600">Portfolio</a>
                  <a href="/visualization" className="hover:text-blue-600">Visualization</a>
                </div>
              </div>
            </div>
          </nav>
          <main className="container mx-auto px-4 py-8">
            {children}
          </main>
        </Providers>
      </body>
    </html>
  );
} 