import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Prototyphers BETS App',
  description: 'Bio-Event Tracking System',
  generator: 'v0.dev & claude'
}

export default function RootLayout({
  children
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <>{children}</>
      </body>
    </html>
  )
}
