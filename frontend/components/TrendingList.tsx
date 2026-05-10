import clsx from 'clsx'

const sourceColors: Record<string, { bg: string; text: string; label: string }> = {
  instagram: { bg: '#fdefff', text: '#f258bf', label: 'Instagram' },
  reddit:    { bg: '#fff2ee', text: '#FF4500', label: 'Reddit'    },
  news:      { bg: '#ebfaff', text: '#0d7fd1', label: 'News'      },
  facebook:  { bg: '#eef3ff', text: '#1877F2', label: 'Facebook'  },
}

const sentimentBadge: Record<string, { bg: string; text: string }> = {
  positive: { bg: '#eeffe7', text: '#23a312' },
  neutral:  { bg: '#f0f0f0', text: '#666'    },
  mixed:    { bg: '#fffbe8', text: '#b07c10' },
  negative: { bg: '#fff0f0', text: '#e03030' },
}

interface Topic {
  id: number
  keywords: string[]
  velocity: number
  spike: number
  engagement: number
  sentiment: 'positive' | 'neutral' | 'mixed' | 'negative'
  source: string
  delta: string
}

export default function TrendingList({ topics }: { topics: Topic[] }) {
  return (
    <div className="bg-white rounded-2xl border border-black/[0.07] shadow-card overflow-hidden animate-slide-up" style={{ animationDelay: '100ms' }}>
      <div className="flex items-center justify-between px-5 pt-5 pb-4 border-b border-black/[0.05]">
        <div>
          <h2 className="font-semibold text-[15px]">Trending Topics</h2>
          <p className="text-xs text-black/40 mt-0.5">Updated just now</p>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="live-dot" />
          <span className="text-xs font-semibold text-[#23a312]">LIVE</span>
        </div>
      </div>

      <div className="divide-y divide-black/[0.05]">
        {topics.map((topic, i) => {
          const src = sourceColors[topic.source]
          const sent = sentimentBadge[topic.sentiment]
          const barW = Math.round(topic.velocity * 222)

          return (
            <div
              key={topic.id}
              className="px-5 py-3.5 flex items-center gap-4 hover:bg-black/[0.015] transition-colors cursor-pointer animate-slide-up"
              style={{ animationDelay: `${120 + i * 40}ms` }}
            >
              {/* Rank */}
              <span className="text-sm font-bold text-black/20 w-4 shrink-0">{i + 1}</span>

              {/* Info */}
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-[13px] truncate">{topic.keywords[0]}</p>
                <div className="flex items-center gap-1.5 mt-1">
                  <span className="text-[11px] px-2 py-0.5 rounded-full font-medium" style={{ background: src.bg, color: src.text }}>
                    {src.label}
                  </span>
                  <span className="text-[11px] px-2 py-0.5 rounded-full font-medium" style={{ background: sent.bg, color: sent.text }}>
                    {topic.sentiment}
                  </span>
                </div>
                {/* Velocity bar */}
                <div className="mt-2 h-1 rounded-full bg-black/[0.06] overflow-hidden">
                  <div
                    className="velocity-bar"
                    style={{ '--bar-w': `${barW}%` } as React.CSSProperties}
                  />
                </div>
              </div>

              {/* Engagement + delta */}
              <div className="text-right shrink-0">
                <p className="text-[13px] font-semibold">{topic.engagement.toLocaleString()}</p>
                <p className="text-[11px] font-semibold text-[#23a312]">{topic.delta}</p>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
