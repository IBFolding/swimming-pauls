// Token data with specific analysis
const memeCoins = [
    { 
        name: 'BONK', ticker: 'BONK', price: 0.000012, change: 23.4, mc: '890M', age: '2h', image: '🐕',
        entry: ['Volume up 450% in 1h', 'Twitter trending #1', 'Dev active in Discord', 'New CEX listing rumor'],
        exit: ['Sell 50% at 2x', 'Sell 25% at 5x', 'Hold 25% for 10x+', 'Set stop at -10%'],
        flags: ['High volatility', 'Whale wallets moving', 'Copycat contracts'],
        analysis: "Strong community momentum. High risk but potential for 5-10x if CEX rumors true."
    },
    { 
        name: 'Dogwifhat', ticker: 'WIF', price: 2.34, change: 15.7, mc: '2.3B', age: '5h', image: '🎩',
        entry: ['Consolidation breakout', 'Celebrity mentions', 'Strong holder growth', 'Low sell pressure'],
        exit: ['Take profits at $3', 'Scale out on spikes', 'Core position to $5', 'Trailing stop 15%'],
        flags: ['Already up 200%', 'Large market cap', 'Early whales selling'],
        analysis: "Proven meme with staying power. Lower risk, steady growth expected."
    },
    { 
        name: 'Book of Meme', ticker: 'BOME', price: 0.0087, change: -8.2, mc: '450M', age: '1d', image: '📖',
        entry: ['Dip buying opportunity', 'Support holding', 'Accumulation phase', 'Dev wallet clean'],
        exit: ['Sell 40% at recovery', 'Hold through chop', 'Target 50% gain', 'Cut if -15% more'],
        flags: ['Down 20% from peak', 'Liquidity thinning', 'Fading interest'],
        analysis: "Experienced dip. Could recover or dump more. High risk entry."
    },
    { 
        name: 'Popcat', ticker: 'POPCAT', price: 0.67, change: 31.2, mc: '670M', age: '3d', image: '🐱',
        entry: ['Viral TikTok trend', 'Volume surge 800%', 'Strong Asian community', 'No major sells'],
        exit: ['Sell 30% at $1', 'Sell 30% at $1.5', 'Moon bag to $3+', 'Stop at $0.40'],
        flags: ['Hype cycle peak', 'New holders overleveraged', 'FOMO exhaustion soon'],
        analysis: "Viral momentum play. Ride the wave but take profits aggressively."
    },
    { 
        name: 'SLERF', ticker: 'SLERF', price: 0.23, change: 45.8, mc: '120M', age: '4h', image: '🦥',
        entry: ['Just launched', 'Dev burned liquidity', 'Organic growth', 'No paid shills'],
        exit: ['Sell 50% at 3x', 'Sell 25% at 10x', 'Hold 25% moon', 'Stop at breakeven'],
        flags: ['Very new, unproven', 'Low liquidity', 'Could rug'],
        analysis: "Fresh launch, risky but early. Small position only."
    },
    { 
        name: 'MEW', ticker: 'MEW', price: 0.0045, change: 12.3, mc: '280M', age: '6h', image: '🐱',
        entry: ['Steady accumulation', 'Cat meta trending', 'Strong holder base', 'No whale dumps'],
        exit: ['Scale out on 2x', 'Keep moon bag', 'Add on dips', 'Stop -20%'],
        flags: ['Slow momentum', 'Needs catalyst', 'Boring price action'],
        analysis: "Slow and steady. Good for small position while waiting for catalyst."
    },
    { 
        name: 'MICHI', ticker: 'MICHI', price: 0.56, change: -5.4, mc: '190M', age: '12h', image: '🐈',
        entry: ['Pullback to support', 'Oversold bounce', 'Low volume drop', 'Whales accumulating'],
        exit: ['Sell on 30% bounce', 'Dont marry the bag', 'Quick flip only', 'Tight stop -8%'],
        flags: ['Dead chat', 'No new buyers', 'Stagnant price'],
        analysis: "Potential dead cat bounce. Quick flip only, don't hold long."
    },
    { 
        name: 'GIGA', ticker: 'GIGA', price: 0.012, change: 67.2, mc: '85M', age: '30m', image: '💪',
        entry: ['Just launched', 'Gym bro meta', 'Strong initial volume', 'Dev doxxed'],
        exit: ['Take 50% at 2x', 'Take 25% at 5x', 'Let 25% moon', 'Stop at -30%'],
        flags: ['EXTREME risk', 'Minutes old', 'Could go to zero', 'FOMO price'],
        analysis: "Brand new, extreme risk/reward. Tiny position only, be ready to lose it all."
    },
];

function renderPumpFunTokens() {
    const container = document.getElementById('pumpfun-tokens');
    container.innerHTML = memeCoins.map((coin, index) => `
        <div class="p-4 bg-white/5 rounded-xl border border-white/10 hover:border-purple-500/50 transition-colors cursor-pointer" onclick="showTokenDetail(${index})">
            <div class="flex items-center gap-3 mb-3">
                <div class="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-xl">${coin.image}</div>
                <div>
                    <div class="font-bold">${coin.name}</div>
                    <div class="text-xs text-gray-500">$${coin.ticker}</div>
                </div>
            </div>
            <div class="flex items-center justify-between mb-2">
                <span class="text-lg font-bold">$${coin.price < 0.01 ? coin.price.toFixed(6) : coin.price.toFixed(2)}</span>
                <span class="text-sm ${coin.change >= 0 ? 'text-green-400' : 'text-red-400'}">${coin.change >= 0 ? '+' : ''}${coin.change}%</span>
            </div>
            <div class="flex items-center justify-between text-xs text-gray-500">
                <span>MC: $${coin.mc}</span>
                <span class="flex items-center gap-1"><span class="w-1.5 h-1.5 rounded-full bg-green-400"></span>${coin.age}</span>
            </div>
            <div class="mt-2 text-xs text-cyan-400">Click for analysis →</div>
        </div>
    `).join('');
}

function showTokenDetail(index) {
    const coin = memeCoins[index];
    document.getElementById('default-strategy').classList.add('hidden');
    document.getElementById('token-detail').classList.remove('hidden');
    
    document.getElementById('detail-icon').textContent = coin.image;
    document.getElementById('detail-name').textContent = coin.name;
    document.getElementById('detail-ticker').textContent = '$' + coin.ticker + ' • $' + (coin.price < 0.01 ? coin.price.toFixed(6) : coin.price.toFixed(2)) + ' • ' + (coin.change >= 0 ? '+' : '') + coin.change + '%';
    
    document.getElementById('detail-entry').innerHTML = coin.entry.map(e => `<li class="flex items-start gap-2"><span class="text-green-400 mt-1">✓</span><span>${e}</span></li>`).join('');
    document.getElementById('detail-exit').innerHTML = coin.exit.map(e => `<li class="flex items-start gap-2"><span class="text-yellow-400 mt-1">→</span><span>${e}</span></li>`).join('');
    document.getElementById('detail-flags').innerHTML = coin.flags.map(f => `<li class="flex items-start gap-2"><span class="text-red-400 mt-1">⚠</span><span>${f}</span></li>`).join('');
    document.getElementById('detail-analysis').textContent = coin.analysis;
}

function closeTokenDetail() {
    document.getElementById('token-detail').classList.add('hidden');
    document.getElementById('default-strategy').classList.remove('hidden');
}
