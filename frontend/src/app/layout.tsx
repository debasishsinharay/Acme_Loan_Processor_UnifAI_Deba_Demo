import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Acme Loan Processor',
  description: 'AI loan assistant demo for UnifAI',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
