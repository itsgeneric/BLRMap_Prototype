import type { Metadata, Viewport } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'BLR Router - Real-Time GPS Navigation',
  description: 'Bengaluru Two-Wheeler Real-Time Turn-by-Turn GPS Navigation Prototype built with Next.js',
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased bg-slate-950 text-slate-100 select-none">
        {children}
      </body>
    </html>
  );
}
