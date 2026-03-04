import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Truth Engine - AI Cyber-Defense Dashboard',
  description: 'High-fidelity provenance analysis and fact-checking for the digital age.',
}

import { ErrorBoundary } from '../components/ErrorBoundary'

import { TruthStoreProvider } from "@/lib/TruthStore";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-deep-black text-white selection:bg-neon-lime selection:text-deep-black antialiased`}>
        <div className="fixed inset-0 bg-[radial-gradient(circle_at_top_right,rgba(193,255,0,0.05),transparent_40%),radial-gradient(circle_at_bottom_left,rgba(193,255,0,0.05),transparent_40%)] pointer-events-none" />
        <TruthStoreProvider>
          <ErrorBoundary>
            {children}
          </ErrorBoundary>
        </TruthStoreProvider>
      </body>
    </html>
  );
}