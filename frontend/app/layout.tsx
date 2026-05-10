import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Adriana — Social Intelligence',
  description: 'Real-time social listening powered by Adriana',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
