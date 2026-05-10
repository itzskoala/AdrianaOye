'use client'
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts'

interface Source { name: string; value: number; color: string }

const CustomTooltip = ({ active, payload }: any) => {
  if (!active || !payload?.length) return null
  const d = payload[0]
  return (
    <div className="bg-white border border-black/[0.08] rounded-xl shadow-float px-3 py-2 text-[12px]">
      <p className="font-semibold">{d.name}</p>
      <p className="text-black/50">{d.value}% of mentions</p>
    </div>
  )
}

export default function SourceDonut({ data, total }: { data: Source[]; total: string }) {
  return (
    <div className="bg-white rounded-2xl border border-black/[0.07] shadow-card p-5 animate-slide-up" style={{ animationDelay: '200ms' }}>
      <div className="mb-4">
        <h2 className="font-semibold text-[15px]">Source Breakdown</h2>
        <p className="text-xs text-black/40 mt-0.5">By mention volume</p>
      </div>

      <div className="flex items-center gap-4">
        {/* Donut */}
        <div className="relative w-36 h-36 shrink-0">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={data} cx="50%" cy="50%" innerRadius={42} outerRadius={64} paddingAngle={3} dataKey="value" startAngle={90} endAngle={-270}>
                {data.map((entry, i) => (
                  <Cell key={i} fill={entry.color} stroke="none" />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
          {/* Center label */}
          <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
            <p className="text-[17px] font-bold leading-none">{total}</p>
            <p className="text-[10px] text-black/40 mt-0.5">total</p>
          </div>
        </div>

        {/* Legend */}
        <div className="flex flex-col gap-2.5 flex-1">
          {data.map((src) => (
            <div key={src.name} className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full shrink-0" style={{ background: src.color }} />
                <span className="text-[13px] text-black/70 font-medium">{src.name}</span>
              </div>
              <span className="text-[13px] font-semibold">{src.value}%</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
