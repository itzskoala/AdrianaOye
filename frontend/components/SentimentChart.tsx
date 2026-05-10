'use client'
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

interface DataPoint {
  day: string
  positive: number
  neutral: number
  negative: number
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-white border border-black/[0.08] rounded-xl shadow-float px-3 py-2.5 text-[12px]">
      <p className="font-semibold text-black/60 mb-1.5">{label}</p>
      {payload.map((p: any) => (
        <p key={p.name} className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full inline-block" style={{ background: p.color }} />
          <span className="capitalize text-black/70">{p.name}</span>
          <span className="font-semibold ml-auto pl-4">{p.value}%</span>
        </p>
      ))}
    </div>
  )
}

export default function SentimentChart({ data }: { data: DataPoint[] }) {
  return (
    <div className="bg-white rounded-2xl border border-black/[0.07] shadow-card p-5 animate-slide-up" style={{ animationDelay: '150ms' }}>
      <div className="mb-4">
        <h2 className="font-semibold text-[15px]">Sentiment Trend</h2>
        <p className="text-xs text-black/40 mt-0.5">Last 7 days</p>
      </div>

      {/* Legend */}
      <div className="flex items-center gap-4 mb-4">
        {[
          { label: 'Positive', color: '#1483F3' },
          { label: 'Neutral',  color: '#d1d5db' },
          { label: 'Negative', color: '#f258bf' },
        ].map(({ label, color }) => (
          <div key={label} className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full" style={{ background: color }} />
            <span className="text-[11px] text-black/50 font-medium">{label}</span>
          </div>
        ))}
      </div>

      <ResponsiveContainer width="100%" height={160}>
        <AreaChart data={data} margin={{ top: 4, right: 0, left: -24, bottom: 0 }}>
          <defs>
            <linearGradient id="gPos" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor="#1483F3" stopOpacity={0.15} />
              <stop offset="95%" stopColor="#1483F3" stopOpacity={0}    />
            </linearGradient>
            <linearGradient id="gNeu" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor="#d1d5db" stopOpacity={0.15} />
              <stop offset="95%" stopColor="#d1d5db" stopOpacity={0}    />
            </linearGradient>
            <linearGradient id="gNeg" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor="#f258bf" stopOpacity={0.15} />
              <stop offset="95%" stopColor="#f258bf" stopOpacity={0}    />
            </linearGradient>
          </defs>
          <XAxis dataKey="day" tick={{ fontSize: 11, fill: '#00000066' }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fontSize: 11, fill: '#00000066' }} axisLine={false} tickLine={false} unit="%" />
          <Tooltip content={<CustomTooltip />} cursor={{ stroke: '#00000010', strokeWidth: 1 }} />
          <Area type="monotone" dataKey="positive" stroke="#1483F3" strokeWidth={2} fill="url(#gPos)" />
          <Area type="monotone" dataKey="neutral"  stroke="#d1d5db" strokeWidth={2} fill="url(#gNeu)" />
          <Area type="monotone" dataKey="negative" stroke="#f258bf" strokeWidth={2} fill="url(#gNeg)" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
