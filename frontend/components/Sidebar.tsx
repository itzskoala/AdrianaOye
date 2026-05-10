'use client'
import { useState } from 'react'
import { LayoutDashboard, Search, TrendingUp, BarChart2, Settings, Radio } from 'lucide-react'
import clsx from 'clsx'

const navItems = [
  { icon: LayoutDashboard, label: 'Dashboard', active: true },
  { icon: Search,          label: 'Search',    active: false },
  { icon: TrendingUp,      label: 'Trending',  active: false },
  { icon: BarChart2,       label: 'Analytics', active: false },
  { icon: Settings,        label: 'Settings',  active: false },
]

export default function Sidebar() {
  const [active, setActive] = useState('Dashboard')

  return (
    <aside className="w-[72px] h-full flex flex-col items-center py-6 bg-white border-r border-black/[0.07] shrink-0">
      {/* Logo */}
      <div className="mb-8 flex flex-col items-center gap-1">
        <div className="w-9 h-9 rounded-xl bg-brand-blue flex items-center justify-center shadow-sm">
          <Radio className="w-5 h-5 text-white" />
        </div>
      </div>

      {/* Nav */}
      <nav className="flex flex-col gap-1 flex-1">
        {navItems.map(({ icon: Icon, label }) => (
          <button
            key={label}
            onClick={() => setActive(label)}
            title={label}
            className={clsx(
              'w-11 h-11 rounded-xl flex items-center justify-center transition-all duration-200',
              active === label
                ? 'bg-brand-blue-soft text-brand-blue'
                : 'text-black/30 hover:text-black/60 hover:bg-black/[0.04]'
            )}
          >
            <Icon className="w-[18px] h-[18px]" />
          </button>
        ))}
      </nav>

      {/* Avatar */}
      <div className="mt-auto">
        <div className="w-9 h-9 rounded-full bg-gradient-to-br from-purple-400 to-brand-blue flex items-center justify-center text-white text-xs font-bold shadow-sm">
          T
        </div>
      </div>
    </aside>
  )
}
