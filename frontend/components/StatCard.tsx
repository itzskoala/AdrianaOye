import clsx from 'clsx'
import { MessageSquare, Smile, Zap } from 'lucide-react'

const icons = {
  mentions:  MessageSquare,
  sentiment: Smile,
  topics:    Zap,
}

interface Props {
  label: string
  value: string
  change: string
  trend: 'up' | 'down'
  accent: string
  accentBg: string
  icon: keyof typeof icons
  delay?: number
}

export default function StatCard({ label, value, change, trend, accent, accentBg, icon, delay = 0 }: Props) {
  const Icon = icons[icon]
  return (
    <div
      className="bg-white rounded-2xl border border-black/[0.07] shadow-card p-5 flex flex-col gap-4 animate-slide-up"
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className="flex items-center justify-between">
        <div
          className="w-9 h-9 rounded-xl flex items-center justify-center"
          style={{ background: accentBg }}
        >
          <Icon className="w-[18px] h-[18px]" style={{ color: accent }} />
        </div>

        <span
          className="text-xs font-semibold px-2.5 py-1 rounded-full"
          style={{ background: accentBg, color: accent }}
        >
          {trend === 'up' ? '↑' : '↓'} {change}
        </span>
      </div>

      <div>
        <p className="text-[28px] font-bold tracking-tight leading-none">{value}</p>
        <p className="text-sm text-black/45 mt-1">{label}</p>
      </div>
    </div>
  )
}
