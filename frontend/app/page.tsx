import Sidebar from '@/components/Sidebar'
import StatCard from '@/components/StatCard'
import TrendingList from '@/components/TrendingList'
import SentimentChart from '@/components/SentimentChart'
import SourceDonut from '@/components/SourceDonut'
import { stats, trendingTopics, sentimentHistory, sourceData } from '@/lib/mockData'

export default function Dashboard() {
  return (
    <div className="flex h-screen overflow-hidden bg-[#f8f8f8]">
      <Sidebar />

      <main className="flex-1 overflow-y-auto p-6">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-sm text-black/40 mt-0.5">Social listening overview · Updated just now</p>
        </div>

        {/* Stat cards */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          {stats.map((s, i) => (
            <StatCard key={s.label} {...s} delay={i * 60} />
          ))}
        </div>

        {/* Main grid */}
        <div className="grid grid-cols-3 gap-4">
          {/* Trending — spans 2 cols */}
          <div className="col-span-2">
            <TrendingList topics={trendingTopics} />
          </div>

          {/* Source donut */}
          <div>
            <SourceDonut data={sourceData} total="34.9k" />
          </div>

          {/* Sentiment chart — full width */}
          <div className="col-span-3">
            <SentimentChart data={sentimentHistory} />
          </div>
        </div>
      </main>
    </div>
  )
}
