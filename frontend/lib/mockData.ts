export const stats = [
  {
    label: 'Total Mentions',
    value: '34,891',
    change: '+12.3%',
    trend: 'up' as const,
    accent: '#1483F3',
    accentBg: '#ebfaff',
    icon: 'mentions',
  },
  {
    label: 'Positive Sentiment',
    value: '67%',
    change: '+5.2pts',
    trend: 'up' as const,
    accent: '#23a312',
    accentBg: '#eeffe7',
    icon: 'sentiment',
  },
  {
    label: 'Trending Topics',
    value: '12',
    change: '+3 today',
    trend: 'up' as const,
    accent: '#6a60dd',
    accentBg: '#f0efff',
    icon: 'topics',
  },
]

export const trendingTopics = [
  {
    id: 1,
    keywords: ['Telemundo Noticias', 'breaking news', 'live'],
    velocity: 0.45,
    spike: 3.2,
    engagement: 12450,
    sentiment: 'neutral' as const,
    source: 'news',
    delta: '+45%',
  },
  {
    id: 2,
    keywords: ['La Voz Kids', 'season finale', 'winner'],
    velocity: 0.38,
    spike: 2.8,
    engagement: 8920,
    sentiment: 'positive' as const,
    source: 'instagram',
    delta: '+38%',
  },
  {
    id: 3,
    keywords: ['Exatlón', 'competition', 'finale'],
    velocity: 0.22,
    spike: 2.1,
    engagement: 6730,
    sentiment: 'positive' as const,
    source: 'reddit',
    delta: '+22%',
  },
  {
    id: 4,
    keywords: ['Telemundo 51', 'Miami', 'local news'],
    velocity: 0.18,
    spike: 1.9,
    engagement: 4560,
    sentiment: 'mixed' as const,
    source: 'facebook',
    delta: '+18%',
  },
  {
    id: 5,
    keywords: ['telenovela', 'drama', 'novelas'],
    velocity: 0.15,
    spike: 1.7,
    engagement: 3890,
    sentiment: 'positive' as const,
    source: 'instagram',
    delta: '+15%',
  },
]

export const sentimentHistory = [
  { day: 'Mon', positive: 42, neutral: 35, negative: 23 },
  { day: 'Tue', positive: 48, neutral: 32, negative: 20 },
  { day: 'Wed', positive: 45, neutral: 38, negative: 17 },
  { day: 'Thu', positive: 51, neutral: 30, negative: 19 },
  { day: 'Fri', positive: 58, neutral: 28, negative: 14 },
  { day: 'Sat', positive: 62, neutral: 25, negative: 13 },
  { day: 'Sun', positive: 55, neutral: 33, negative: 12 },
]

export const sourceData = [
  { name: 'Instagram', value: 32, color: '#E1306C' },
  { name: 'Reddit',    value: 28, color: '#FF4500' },
  { name: 'News',      value: 25, color: '#1483F3' },
  { name: 'Facebook',  value: 15, color: '#1877F2' },
]

export const insights = [
  {
    id: 1,
    topic: 'La Voz Kids',
    keywords: ['la voz', 'kids', 'season'],
    summary: 'Fans are highly engaged with the Season 7 finale, praising the young contestants\' performances. Viewer loyalty is strong.',
    sentiment: 'positive' as const,
    keyInsight: 'Post a behind-the-scenes reel of contestants before the finale airs — this drives 3× more saves than standard posts.',
    engagement: 8920,
    source: 'instagram',
  },
  {
    id: 2,
    topic: 'Telemundo Noticias',
    keywords: ['noticias', 'breaking', 'live'],
    summary: 'News coverage around immigration policy is generating high traffic. Audience sentiment is cautious but engaged.',
    sentiment: 'neutral' as const,
    keyInsight: 'Live Spanish-language coverage is the main traffic driver — consider more live updates during peak news cycles (6–9pm ET).',
    engagement: 12450,
    source: 'news',
  },
]

export const initialMessages = [
  {
    id: '1',
    role: 'adriana' as const,
    text: '¡Hola! I\'m Adriana, your social intelligence analyst. I\'m actively monitoring Telemundo\'s presence across Instagram, Reddit, Facebook, and the news in real time.',
    ts: new Date(Date.now() - 60000),
    showPrompts: true,
  },
]

export const quickPrompts = [
  'What\'s trending right now?',
  'How is our sentiment this week?',
  'Ideas for our next Instagram post?',
  'Who\'s talking about us on Reddit?',
]

export const adrianaReplies: Record<string, string> = {
  'What\'s trending right now?':
    '📈 Right now **La Voz Kids** is your fastest-growing topic — up 38% in velocity with 8,920 engagements in the last 6 hours. The Season 7 finale is driving conversation on Instagram. **Telemundo Noticias** is also spiking (3.2×) due to breaking immigration coverage. Want me to run a full analysis on either of these?',
  'How is our sentiment this week?':
    '💬 This week\'s sentiment is trending **positive** — up to 67% from 62% last week. Your best day was Saturday (62% positive) after the La Voz Kids promo dropped. The only friction point is some neutral-to-negative chatter on Reddit around scheduling changes. Overall, you\'re in a good spot.',
  'Ideas for our next Instagram post?':
    '✨ Based on what\'s trending for your audience right now:\n\n1. **La Voz Kids BTS** — a behind-the-scenes reel before the finale. Posts like this get 3× more saves.\n2. **"Which contestant are you?" quiz** — polls drive 4× higher comment rates.\n3. **Countdown to the finale** — a 3-post story series building anticipation.\n\nWant me to draft caption copy for any of these?',
  'Who\'s talking about us on Reddit?':
    '🔍 On Reddit, Telemundo mentions are concentrated in r/television, r/LatinoPeopleTwitter, and r/exatlon. The tone is mostly positive around show content, with some criticism about subtitle quality on streaming. The r/exatlon community is the most active — 230 posts this week.',
}
