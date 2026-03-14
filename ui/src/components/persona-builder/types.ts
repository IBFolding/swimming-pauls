/**
 * Paul Persona Types
 * TypeScript interfaces for Paul persona builder
 */

export interface PaulPersona {
  id: string;
  name: string;
  codename: string;
  emoji: string;
  
  // Core traits
  profession: ProfessionType;
  bias: number; // -1 to 1 (bearish to bullish)
  confidence: number; // 0 to 1
  
  // Background
  backstory: string;
  catchphrase: string;
  
  // Specialties
  specialties: Specialty[];
  
  // Traits
  traits: Trait[];
  
  // Meta
  isCustom: boolean;
  createdAt: string;
  updatedAt: string;
}

export type ProfessionType = 
  | 'swing_trader'
  | 'scalper'
  | 'position_trader'
  | 'algorithmic'
  | 'quantitative'
  | 'event_driven'
  | 'contrarian'
  | 'momentum'
  | 'value'
  | 'macro_analyst'
  | 'technical_analyst'
  | 'fundamental_analyst'
  | 'sentiment_analyst'
  | 'onchain_analyst'
  | 'defi_specialist'
  | 'nft_expert'
  | 'memecoin_hunter'
  | 'arbitrageur';

export interface ProfessionOption {
  value: ProfessionType;
  label: string;
  description: string;
  emoji: string;
}

export type Specialty =
  | 'defi'
  | 'nft'
  | 'layer1'
  | 'layer2'
  | 'memecoins'
  | 'gaming'
  | 'dao'
  | 'equities'
  | 'forex'
  | 'commodities'
  | 'bonds'
  | 'macro'
  | 'policy'
  | 'geopolitics'
  | 'onchain'
  | 'derivatives'
  | 'arbitrage'
  | 'mev'
  | 'tech'
  | 'biotech'
  | 'energy'
  | 'real_estate'
  | 'technical_analysis'
  | 'sentiment_analysis';

export interface SpecialtyOption {
  value: Specialty;
  label: string;
  emoji: string;
}

export type Trait =
  | 'risk_averse'
  | 'creative'
  | 'analytical'
  | 'aggressive'
  | 'patient'
  | 'impulsive'
  | 'cautious'
  | 'innovative'
  | 'methodical'
  | 'intuitive'
  | 'data_driven'
  | 'contrarian'
  | 'trend_following'
  | 'adaptive'
  | 'disciplined'
  | 'opportunistic'
  | 'skeptical'
  | 'optimistic'
  | 'pessimistic'
  | 'volatile';

export interface TraitOption {
  value: Trait;
  label: string;
  description: string;
  emoji: string;
  color: string;
}

export interface PaulFormData {
  name: string;
  emoji: string;
  profession: ProfessionType;
  bias: number;
  confidence: number;
  backstory: string;
  specialties: Specialty[];
  traits: Trait[];
}

export interface BuiltInPaul extends PaulPersona {
  isBuiltIn: true;
}

// Available emojis for picker
export const PAUL_EMOJIS = [
  '🐟', '🐠', '🐡', '🦈', '🐙', '🦑', '🦀', '🦞', '🦐', '🐬',
  '🐳', '🐋', '🦭', '🐊', '🐢', '🦎', '🐍', '🐲', '🐉', '🦕',
  '🦖', '🦜', '🦚', '🦩', '🐦', '🐧', '🐤', '🐣', '🐥', '🦅',
  '🦉', '🦇', '🐺', '🐗', '🐴', '🦄', '🐝', '🐛', '🦋', '🐌',
  '🐞', '🐜', '🦟', '🦗', '🕷️', '🦂', '🐢', '🐍', '🦎', '🦖',
  '🤖', '👾', '👽', '👻', '💀', '☠️', '🎃', '🤡', '💩', '🤠',
  '🤑', '😎', '🤓', '🧐', '🤯', '🤪', '😵', '🥴', '😷', '🤒',
  '👑', '💎', '🔮', '💰', '💵', '💸', '📈', '📉', '📊', '⚡',
  '🔥', '💧', '❄️', '🌊', '🌪️', '⛈️', '🌈', '⭐', '🌟', '✨',
  '🎯', '🎲', '🎰', '🎪', '🎨', '🎭', '🎪', '🎬', '🎤', '🎧',
];

// Profession options
export const PROFESSION_OPTIONS: ProfessionOption[] = [
  { value: 'swing_trader', label: 'Swing Trader', description: 'Holds positions for days to weeks, capturing medium-term trends', emoji: '📊' },
  { value: 'scalper', label: 'Scalper', description: 'Makes rapid trades for small profits, high frequency', emoji: '⚡' },
  { value: 'position_trader', label: 'Position Trader', description: 'Long-term holds based on fundamental analysis', emoji: '📈' },
  { value: 'algorithmic', label: 'Algorithmic Trader', description: 'Uses automated systems and trading bots', emoji: '🤖' },
  { value: 'quantitative', label: 'Quant Analyst', description: 'Mathematical models and statistical arbitrage', emoji: '📐' },
  { value: 'event_driven', label: 'Event Driven', description: 'Trades on news, earnings, and catalysts', emoji: '📰' },
  { value: 'contrarian', label: 'Contrarian', description: 'Goes against market sentiment', emoji: '🔄' },
  { value: 'momentum', label: 'Momentum Trader', description: 'Follows trends and price momentum', emoji: '🚀' },
  { value: 'value', label: 'Value Investor', description: 'Seeks undervalued assets with strong fundamentals', emoji: '💎' },
  { value: 'macro_analyst', label: 'Macro Analyst', description: 'Focuses on global economic trends', emoji: '🌍' },
  { value: 'technical_analyst', label: 'Technical Analyst', description: 'Chart patterns and technical indicators', emoji: '📉' },
  { value: 'fundamental_analyst', label: 'Fundamental Analyst', description: 'Deep dive into project fundamentals', emoji: '🔍' },
  { value: 'sentiment_analyst', label: 'Sentiment Analyst', description: 'Social metrics and market psychology', emoji: '🧠' },
  { value: 'onchain_analyst', label: 'On-Chain Analyst', description: 'Blockchain data and wallet analysis', emoji: '⛓️' },
  { value: 'defi_specialist', label: 'DeFi Specialist', description: 'DeFi protocols, yields, and liquidity', emoji: '🌾' },
  { value: 'nft_expert', label: 'NFT Expert', description: 'Digital collectibles and NFT markets', emoji: '🎨' },
  { value: 'memecoin_hunter', label: 'Memecoin Hunter', description: 'Early memecoin identification', emoji: '🐸' },
  { value: 'arbitrageur', label: 'Arbitrageur', description: 'Exploits price differences across markets', emoji: '⚖️' },
];

// Specialty options
export const SPECIALTY_OPTIONS: SpecialtyOption[] = [
  { value: 'defi', label: 'DeFi', emoji: '🌾' },
  { value: 'nft', label: 'NFTs', emoji: '🎨' },
  { value: 'layer1', label: 'Layer 1s', emoji: '⛓️' },
  { value: 'layer2', label: 'Layer 2s', emoji: '🔷' },
  { value: 'memecoins', label: 'Memecoins', emoji: '🐸' },
  { value: 'gaming', label: 'Gaming', emoji: '🎮' },
  { value: 'dao', label: 'DAOs', emoji: '🏛️' },
  { value: 'equities', label: 'Equities', emoji: '📈' },
  { value: 'forex', label: 'Forex', emoji: '💱' },
  { value: 'commodities', label: 'Commodities', emoji: '🛢️' },
  { value: 'bonds', label: 'Bonds', emoji: '📜' },
  { value: 'macro', label: 'Macro', emoji: '🌍' },
  { value: 'policy', label: 'Policy', emoji: '📋' },
  { value: 'geopolitics', label: 'Geopolitics', emoji: '🗺️' },
  { value: 'onchain', label: 'On-Chain', emoji: '🔍' },
  { value: 'derivatives', label: 'Derivatives', emoji: '📊' },
  { value: 'arbitrage', label: 'Arbitrage', emoji: '⚖️' },
  { value: 'mev', label: 'MEV', emoji: '⛏️' },
  { value: 'tech', label: 'Tech', emoji: '💻' },
  { value: 'biotech', label: 'Biotech', emoji: '🧬' },
  { value: 'energy', label: 'Energy', emoji: '⚡' },
  { value: 'real_estate', label: 'Real Estate', emoji: '🏘️' },
  { value: 'technical_analysis', label: 'Technical Analysis', emoji: '📉' },
  { value: 'sentiment_analysis', label: 'Sentiment Analysis', emoji: '🧠' },
];

// Trait options
export const TRAIT_OPTIONS: TraitOption[] = [
  { value: 'risk_averse', label: 'Risk-Averse', description: 'Prioritizes capital preservation over gains', emoji: '🛡️', color: '#10b981' },
  { value: 'creative', label: 'Creative', description: 'Thinks outside the box, finds unique opportunities', emoji: '🎨', color: '#8b5cf6' },
  { value: 'analytical', label: 'Analytical', description: 'Deep data analysis and logical reasoning', emoji: '📊', color: '#3b82f6' },
  { value: 'aggressive', label: 'Aggressive', description: 'High risk tolerance, seeks maximum returns', emoji: '🔥', color: '#ef4444' },
  { value: 'patient', label: 'Patient', description: 'Waits for the perfect setup, no FOMO', emoji: '🧘', color: '#10b981' },
  { value: 'impulsive', label: 'Impulsive', description: 'Acts quickly on instincts, may FOMO', emoji: '⚡', color: '#f59e0b' },
  { value: 'cautious', label: 'Cautious', description: 'Double-checks everything, minimizes mistakes', emoji: '🔍', color: '#6b7280' },
  { value: 'innovative', label: 'Innovative', description: 'Early adopter of new strategies and tech', emoji: '💡', color: '#06b6d4' },
  { value: 'methodical', label: 'Methodical', description: 'Follows strict process and rules', emoji: '📝', color: '#6366f1' },
  { value: 'intuitive', label: 'Intuitive', description: 'Trusts gut feelings and pattern recognition', emoji: '🔮', color: '#a855f7' },
  { value: 'data_driven', label: 'Data-Driven', description: 'Decisions based purely on metrics', emoji: '📈', color: '#0ea5e9' },
  { value: 'contrarian', label: 'Contrarian', description: 'Goes against the herd', emoji: '🔄', color: '#ec4899' },
  { value: 'trend_following', label: 'Trend-Following', description: 'Rides momentum and popular trends', emoji: '🌊', color: '#22d3ee' },
  { value: 'adaptive', label: 'Adaptive', description: 'Quickly adjusts to changing conditions', emoji: '🦎', color: '#84cc16' },
  { value: 'disciplined', label: 'Disciplined', description: 'Sticks to plan, cuts losses quickly', emoji: '⛓️', color: '#4b5563' },
  { value: 'opportunistic', label: 'Opportunistic', description: 'Pounces on any edge or mispricing', emoji: '👁️', color: '#f97316' },
  { value: 'skeptical', label: 'Skeptical', description: 'Questions everything, avoids hype', emoji: '🤔', color: '#64748b' },
  { value: 'optimistic', label: 'Optimistic', description: 'Bullish bias, sees opportunities', emoji: '🌞', color: '#fbbf24' },
  { value: 'pessimistic', label: 'Pessimistic', description: 'Bearish bias, anticipates problems', emoji: '🌧️', color: '#475569' },
  { value: 'volatile', label: 'Volatile', description: 'Unpredictable, adapts style to mood', emoji: '🎲', color: '#d946ef' },
];

// Built-in Pauls for comparison
export const BUILT_IN_PAULS: BuiltInPaul[] = [
  {
    id: 'builtin-1',
    name: 'Alpha Paul',
    codename: 'The Pioneer',
    emoji: '🦈',
    profession: 'swing_trader',
    bias: 0.2,
    confidence: 0.75,
    backstory: 'First of his kind, Alpha Paul combines technical precision with market intuition. He cut his teeth in the 2017 crypto bull run and never looked back.',
    catchphrase: "The trend is your friend until it bends.",
    specialties: ['technical_analysis', 'layer1', 'defi'],
    traits: ['analytical', 'disciplined', 'patient'],
    isCustom: false,
    isBuiltIn: true,
    createdAt: '2024-01-01',
    updatedAt: '2024-01-01',
  },
  {
    id: 'builtin-2',
    name: 'Beta Paul',
    codename: 'The Optimizer',
    emoji: '🐙',
    profession: 'quantitative',
    bias: 0.1,
    confidence: 0.85,
    backstory: 'A former quant at a major hedge fund, Beta Paul left tradfi for the wild west of crypto. He sees patterns where others see noise.',
    catchphrase: "In God we trust, all others bring data.",
    specialties: ['onchain', 'derivatives', 'arbitrage'],
    traits: ['data_driven', 'methodical', 'analytical'],
    isCustom: false,
    isBuiltIn: true,
    createdAt: '2024-01-01',
    updatedAt: '2024-01-01',
  },
  {
    id: 'builtin-3',
    name: 'Gamma Paul',
    codename: 'The Degenerate',
    emoji: '🦀',
    profession: 'memecoin_hunter',
    bias: 0.6,
    confidence: 0.45,
    backstory: 'Gamma Paul lives for the thrill of the next 100x. He aped into DOGE at $0.002 and has been chasing that high ever since.',
    catchphrase: "WAGMI or NGMI, there is no try.",
    specialties: ['memecoins', 'nft', 'gaming'],
    traits: ['impulsive', 'opportunistic', 'aggressive'],
    isCustom: false,
    isBuiltIn: true,
    createdAt: '2024-01-01',
    updatedAt: '2024-01-01',
  },
  {
    id: 'builtin-4',
    name: 'Delta Paul',
    codename: 'The Guardian',
    emoji: '🐢',
    profession: 'value',
    bias: -0.3,
    confidence: 0.9,
    backstory: 'Delta Paul survived three bear markets by being paranoid. He DCA\'s into BTC and ETH and laughs at leverage traders.',
    catchphrase: "Not your keys, not your coins.",
    specialties: ['layer1', 'macro', 'policy'],
    traits: ['risk_averse', 'cautious', 'patient'],
    isCustom: false,
    isBuiltIn: true,
    createdAt: '2024-01-01',
    updatedAt: '2024-01-01',
  },
  {
    id: 'builtin-5',
    name: 'Epsilon Paul',
    codename: 'The Oracle',
    emoji: '🔮',
    profession: 'sentiment_analyst',
    bias: 0.0,
    confidence: 0.7,
    backstory: 'Epsilon Paul reads Twitter sentiment like others read charts. He called the 2021 top by measuring euphoria in Discord servers.',
    catchphrase: "Fear is temporary, regret is forever.",
    specialties: ['sentiment_analysis', 'macro', 'gaming'],
    traits: ['intuitive', 'adaptive', 'creative'],
    isCustom: false,
    isBuiltIn: true,
    createdAt: '2024-01-01',
    updatedAt: '2024-01-01',
  },
  {
    id: 'builtin-6',
    name: 'Zeta Paul',
    codename: 'The Architect',
    emoji: '🤖',
    profession: 'algorithmic',
    bias: 0.1,
    confidence: 0.8,
    backstory: 'Zeta Paul writes smart contracts in his sleep. His trading bots execute thousands of transactions while you read this.',
    catchphrase: "Code is law, data is truth.",
    specialties: ['defi', 'mev', 'arbitrage'],
    traits: ['methodical', 'data_driven', 'innovative'],
    isCustom: false,
    isBuiltIn: true,
    createdAt: '2024-01-01',
    updatedAt: '2024-01-01',
  },
];

// Storage keys
export const STORAGE_KEYS = {
  CUSTOM_PAULS: 'swimming_pauls_custom',
  GITHUB_TOKEN: 'swimming_pauls_github_token',
  GITHUB_REPO: 'swimming_pauls_github_repo',
};
