// frontend/app/(routes)/dashboard/layout.tsx
import React from 'react'

export default function DashboardLayout({
  children
}: {
  children: React.ReactNode
}) {
  return <>{children}</>
}


// import type { Metadata } from 'next'

// export const metadata: Metadata = {
//   title: 'BETS Dashboard',
//   description: 'Bio-Event Tracking System'
// }
