import React, { useState, useEffect } from 'react';
import { useWallet, useConnection } from '@solana/wallet-adapter-react';
import { WalletMultiButton } from '@solana/wallet-adapter-react-ui';
import { QRCodeSVG } from 'qrcode.react';
import { PublicKey } from '@solana/web3.js';
import { getAssociatedTokenAddress, getAccount } from '@solana/spl-token';

const PAUL_TOKEN_MINT = 'YOUR_PAUL_TOKEN_MINT_HERE'; // Replace with actual mint

export default function Home() {
  const { publicKey, connected } = useWallet();
  const { connection } = useConnection();
  const [paulBalance, setPaulBalance] = useState(0);
  const [agentConnected, setAgentConnected] = useState(false);
  const [connectionUrl, setConnectionUrl] = useState('');

  useEffect(() => {
    if (connected && publicKey) {
      checkPaulBalance();
      generateConnectionUrl();
    }
  }, [connected, publicKey]);

  const checkPaulBalance = async () => {
    try {
      const mintPubkey = new PublicKey(PAUL_TOKEN_MINT);
      const ata = await getAssociatedTokenAddress(mintPubkey, publicKey!);
      const account = await getAccount(connection, ata);
      setPaulBalance(Number(account.amount) / 1e9);
    } catch {
      setPaulBalance(0);
    }
  };

  const generateConnectionUrl = () => {
    const id = Math.random().toString(36).substring(7);
    setConnectionUrl(`ws://localhost:8765/${id}`);
  };

  const hasAccess = paulBalance >= 10000; // 10K PAUL for dashboard access

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white">
      {/* Hero Section */}
      <section className="relative overflow-hidden py-20 px-4">
        <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-20"></div>
        <div className="max-w-6xl mx-auto text-center relative z-10">
          <h1 className="text-6xl md:text-8xl font-bold mb-6 bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
            🐟 Swimming Pauls
          </h1>
          <p className="text-2xl md:text-3xl text-white/80 mb-4">
            "When MiroFish is too hard, ask Paul. And his multiples."
          </p>
          <p className="text-lg text-white/60 mb-8 max-w-2xl mx-auto">
            Many Pauls from many universes and many professions contemplate the future of your question.
          </p>
          
          <div className="flex flex-wrap justify-center gap-4">
            <WalletMultiButton className="!bg-gradient-to-r !from-cyan-500 !to-purple-600 !rounded-xl !px-8 !py-4 !text-lg !font-bold" />
            <a href="https://pump.fun" target="_blank" className="bg-gradient-to-r from-pink-500 to-orange-500 px-8 py-4 rounded-xl font-bold text-lg hover:scale-105 transition-transform">
              Buy $PAUL 🚀
            </a>
          </div>

          {connected && (
            <div className="mt-6 text-cyan-400">
              Balance: {paulBalance.toLocaleString()} $PAUL
              {hasAccess ? (
                <span className="ml-2 text-green-400">✅ Dashboard Access</span>
              ) : (
                <span className="ml-2 text-yellow-400">⚠️ Need 10K $PAUL for access</span>
              )}
            </div>
          )}
        </div>
      </section>

      {/* Origin Story */}
      <section className="py-20 px-4 bg-black/20">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-4xl font-bold text-center mb-12 text-cyan-400">📖 Origin Story</h2>
          
          <div className="space-y-8">
            {[
              { icon: '🚗', title: 'Sunset Boulevard', desc: 'Born on a drive down Sunset Boulevard, in a self-driving car, listening to Swimming Paul.' },
              { icon: '💡', title: 'The Realization', desc: 'Single-agent AI is like asking one person for advice. Real decisions need multiple perspectives.' },
              { icon: '🐟', title: 'The Pool', desc: 'Analysts, skeptics, visionaries, and hedges all debating until truth emerges.' },
              { icon: '🔒', title: '100% Local', desc: 'When MiroFish felt too heavy, Swimming Pauls was built lightweight, local, and private.' }
            ].map((step, i) => (
              <div key={i} className="flex items-start gap-6 p-6 rounded-2xl bg-white/5 backdrop-blur">
                <div className="text-4xl">{step.icon}</div>
                <div>
                  <h3 className="text-xl font-bold mb-2">{step.title}</h3>
                  <p className="text-white/70">{step.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Token-Gated Dashboard */}
      {connected && hasAccess && (
        <section className="py-20 px-4">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-4xl font-bold text-center mb-12 text-cyan-400">🎛️ Dashboard</h2>
            
            <div className="grid md:grid-cols-2 gap-8">
              {/* QR Code */}
              <div className="p-8 rounded-2xl bg-white/5 backdrop-blur text-center">
                <h3 className="text-xl font-bold mb-4">🔗 Connect Local Agent</h3>
                <div className="bg-white p-4 rounded-xl inline-block mb-4">
                  <QRCodeSVG value={connectionUrl} size={200} />
                </div>
                <p className="text-sm text-white/60 mb-4">Scan with your phone or copy URL</p>
                
                <div className="flex gap-2">
                  <input 
                    type="text" 
                    value={connectionUrl} 
                    readOnly 
                    className="flex-1 bg-black/30 px-4 py-2 rounded-lg text-sm"
                  />
                  <button 
                    onClick={() => navigator.clipboard.writeText(connectionUrl)}
                    className="bg-cyan-600 px-4 py-2 rounded-lg hover:bg-cyan-500"
                  >
                    Copy
                  </button>
                </div>
              </div>

              {/* Agent Status */}
              <div className="p-8 rounded-2xl bg-white/5 backdrop-blur">
                <h3 className="text-xl font-bold mb-4">📡 Agent Status</h3>
                
                <div className={`p-4 rounded-xl mb-4 ${agentConnected ? 'bg-green-500/20' : 'bg-red-500/20'}`}>
                  <div className="flex items-center gap-3">
                    <div className={`w-3 h-3 rounded-full ${agentConnected ? 'bg-green-400' : 'bg-red-400'}`}></div>
                    <span>{agentConnected ? 'Connected' : 'Disconnected'}</span>
                  </div>
                </div>

                <div className="space-y-2 text-sm text-white/60">
                  <p>1. Run <code className="bg-black/30 px-2 py-1 rounded">python local_agent.py</code></p>
                  <p>2. Scan QR code or paste connection URL</p>
                  <p>3. Start casting the pool from your machine</p>
                </div>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Features */}
      <section className="py-20 px-4 bg-black/20">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-4xl font-bold text-center mb-12 text-cyan-400">✨ Features</h2>
          
          <div className="grid md:grid-cols-3 gap-6">
            {[
              { icon: '🐟', title: 'Multi-Agent', desc: '40+ Pauls with unique perspectives' },
              { icon: '💻', title: 'Local First', desc: 'Your machine, your Pauls, your data' },
              { icon: '🔒', title: 'Token Gated', desc: 'Hold $PAUL to access dashboard' },
              { icon: '📊', title: 'Rich Results', desc: 'Monte Carlo, sentiment, consensus' },
              { icon: '🔗', title: 'WebSocket', desc: 'Connect local agent to web UI' },
              { icon: '🎵', title: 'Immersive', desc: 'Swimming Paul audio + animations' }
            ].map((f, i) => (
              <div key={i} className="p-6 rounded-2xl bg-white/5 backdrop-blur hover:bg-white/10 transition-colors">
                <div className="text-3xl mb-3">{f.icon}</div>
                <h3 className="text-lg font-bold mb-2">{f.title}</h3>
                <p className="text-white/60 text-sm">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-4 text-center border-t border-white/10">
        <p className="text-white/60">🐟 Swimming Pauls v2.0 • Built by HOWARD</p>
        <p className="text-white/40 text-sm mt-2">Named while listening to Swimming Paul driving down Sunset</p>
      </footer>
    </div>
  );
}