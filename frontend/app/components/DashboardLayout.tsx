import { ReactNode } from 'react'

interface DashboardLayoutProps {
  children: ReactNode
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="w-64 bg-white shadow-md">
        <div className="p-4 border-b">
          <h1 className="text-xl font-bold">Dashboard</h1>
        </div>
        <nav className="mt-4">
          <ul>
            <li className="p-3 hover:bg-gray-100">Dashboard</li>
            <li className="p-3 hover:bg-gray-100">Users</li>
            <li className="p-3 hover:bg-gray-100">Settings</li>
          </ul>
        </nav>
      </aside>

      <main className="flex-1 p-6">
        <header className="bg-white p-4 shadow-sm mb-6">
          <h2 className="text-2xl font-semibold">Analytics Overview</h2>
        </header>
        <div className="grid gap-6">{children}</div>
      </main>
    </div>
  )
}
