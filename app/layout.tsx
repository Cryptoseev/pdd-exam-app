import type { Metadata, Viewport } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin', 'cyrillic'] });

export const metadata: Metadata = {
  title: 'ПДД — Нина Леонидовна',
  description: 'Тренажёр ПДД для Нины Леонидовны — подготовка к экзамену ГИБДД',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'default',
    title: 'ПДД — Нина Леонидовна',
  },
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  themeColor: '#1A56DB',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ru" suppressHydrationWarning>
      <head>
        <link rel="apple-touch-icon" href="/icons/icon-192.png" />
      </head>
      <body className={`${inter.className} min-h-screen`}>
        <div className="max-w-lg mx-auto min-h-screen flex flex-col">
          {children}
        </div>
      </body>
    </html>
  );
}
