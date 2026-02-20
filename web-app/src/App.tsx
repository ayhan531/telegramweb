import React, { useEffect, useState, useCallback } from 'react';
import WebApp from '@twa-dev/sdk';
import { Search, BarChart3, Users, PieChart, Activity, TrendingUp, X } from 'lucide-react';
import axios from 'axios';

const API_BASE = '/api'; // Relative path for production

interface Holder { kurum: string; toplam_lot: string; pay: string; }
interface Broker { kurum: string; lot: string; pay: string; }
interface StockData {
  name: string; price: number; open: number; high: number; low: number;
  volume: number; change: number; currency: string;
}

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState('derinlik');
  const [symbol, setSymbol] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [stockData, setStockData] = useState<StockData | null>(null);
  const [akdData, setAkdData] = useState<{ buyers: Broker[], sellers: Broker[] } | null>(null);
  const [takasData, setTakasData] = useState<{ holders: Holder[] } | null>(null);

  useEffect(() => {
    WebApp.ready();
    WebApp.expand();
    const primaryColor = WebApp.themeParams.button_color || '#00f2ff';
    document.documentElement.style.setProperty('--accent-color', primaryColor);
  }, []);

  const fetchData = useCallback(async (sym: string) => {
    if (!sym) return;
    setLoading(true);
    try {
      const { data: stock } = await axios.get(`${API_BASE}/stock/${sym}`);
      setStockData(stock);

      const { data: akd } = await axios.get(`${API_BASE}/akd/${sym}`);
      setAkdData(akd);

      const { data: takas } = await axios.get(`${API_BASE}/takas/${sym}`);
      setTakasData(takas);

      setSymbol(sym.toUpperCase());
    } catch (err) {
      console.error("Veri çekme hatası:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery) fetchData(searchQuery);
  };

  return (
    <div className="flex flex-col h-screen bg-black text-white overflow-hidden font-sans">
      {/* Search Header */}
      <header className="p-4 bg-zinc-950/80 backdrop-blur-md border-b border-zinc-900 sticky top-0 z-10">
        <form onSubmit={handleSearch} className="relative group">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500 w-4 h-4 group-focus-within:text-cyan-400 transition-colors" />
          <input
            type="text"
            placeholder="Hisse sembolü girin (örn: THYAO)"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-zinc-900 border border-zinc-800 rounded-xl py-2.5 pl-10 pr-10 text-sm focus:ring-2 focus:ring-cyan-500/50 outline-none transition-all placeholder:text-zinc-600"
          />
          {searchQuery && (
            <button
              type="button"
              onClick={() => setSearchQuery('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-500 hover:text-white"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </form>
      </header>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto pb-24 px-4 pt-4">
        {!symbol && !loading && (
          <div className="flex flex-col items-center justify-center py-20 text-center animate-fade-in">
            <div className="w-20 h-20 bg-cyan-500/10 rounded-3xl flex items-center justify-center border border-cyan-500/20 mb-6">
              <TrendingUp className="w-10 h-10 text-cyan-400" />
            </div>
            <h2 className="text-2xl font-bold bg-gradient-to-r from-white to-zinc-500 bg-clip-text text-transparent">Analiz Başlatın</h2>
            <p className="text-sm text-zinc-500 mt-2 max-w-[280px]">Borsa İstanbul hisselerini anlık derinlik, AKD ve takas verileriyle inceleyin.</p>
          </div>
        )}

        {loading && (
          <div className="flex flex-col items-center justify-center py-20">
            <div className="w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin"></div>
            <p className="text-xs text-cyan-500 mt-4 font-mono uppercase tracking-widest">Veriler Yükleniyor...</p>
          </div>
        )}

        {symbol && !loading && stockData && (
          <div className="space-y-6 animate-fade-in">
            {/* Stock Summary Card */}
            <div className="bg-zinc-900/50 rounded-2xl p-4 border border-zinc-800">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h1 className="text-2xl font-black tracking-tight">{symbol}</h1>
                  <p className="text-[10px] text-zinc-500 uppercase font-bold tracking-widest">{stockData.name}</p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold font-mono text-cyan-400">{stockData.price?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })}</p>
                  <p className={`text-xs font-bold ${stockData.change >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                    {stockData.change >= 0 ? '▲' : '▼'} %{Math.abs(stockData.change || 0).toFixed(2)}
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3 pt-4 border-t border-zinc-800/50">
                <DataRow label="Düşük" value={stockData.low} />
                <DataRow label="Yüksek" value={stockData.high} />
                <DataRow label="Açılış" value={stockData.open} />
                <DataRow label="Hacim" value={stockData.volume?.toLocaleString('tr-TR')} />
              </div>
            </div>

            {/* Content Tabs */}
            <div className="flex bg-zinc-900 rounded-lg p-1 border border-zinc-800">
              <TabButton id="derinlik" label="Derinlik" active={activeTab} onClick={setActiveTab} />
              <TabButton id="akd" label="AKD" active={activeTab} onClick={setActiveTab} />
              <TabButton id="takas" label="Takas" active={activeTab} onClick={setActiveTab} />
              <TabButton id="grafik" label="Grafik" active={activeTab} onClick={setActiveTab} />
            </div>

            {/* Tab Views */}
            <div className="space-y-4">
              {activeTab === 'derinlik' && <DerinlikView symbol={symbol} />}
              {activeTab === 'akd' && <AKDView data={akdData} />}
              {activeTab === 'takas' && <TakasView data={takasData} />}
              {activeTab === 'grafik' && <GrafikView symbol={symbol} />}
            </div>
          </div>
        )}
      </main>

      {/* Bottom Navbar */}
      <footer className="fixed bottom-0 left-0 right-0 glass border-t border-white/5 px-2 pb-8 pt-2">
        <div className="flex justify-around items-center max-w-md mx-auto">
          <NavButton icon={Activity} label="Piyasa" active={true} />
          <NavButton icon={PieChart} label="Cüzdan" />
          <NavButton icon={Users} label="Topluluk" />
          <NavButton icon={BarChart3} label="Haberler" />
        </div>
      </footer>
    </div>
  );
};

// UI Components
const DataRow = ({ label, value }: { label: string, value: string | number }) => (
  <div className="flex justify-between items-center group">
    <span className="text-[10px] text-zinc-500 font-bold uppercase">{label}</span>
    <span className="text-sm font-mono font-medium">{value}</span>
  </div>
);

const TabButton = ({ id, label, active, onClick }: any) => (
  <button
    onClick={() => onClick(id)}
    className={`flex-1 py-1.5 text-[11px] font-bold rounded-md transition-all ${active === id ? 'bg-zinc-800 text-cyan-400 shadow-lg' : 'text-zinc-500 hover:text-zinc-300'
      }`}
  >
    {label}
  </button>
);

const NavButton = ({ icon: Icon, label, active = false }: any) => (
  <button className={`flex flex-col items-center p-2 rounded-xl transition-all ${active ? 'text-cyan-400' : 'text-zinc-600'}`}>
    <Icon className={`w-5 h-5 ${active ? 'stroke-[2.5px]' : ''}`} />
    <span className="text-[9px] font-bold mt-1 uppercase tracking-tighter">{label}</span>
  </button>
);

// Tab Content Views
const DerinlikView = ({ symbol }: { symbol: string }) => (
  <div className="bg-zinc-900/30 rounded-xl border border-zinc-800/50 overflow-hidden">
    <div className="grid grid-cols-2 divide-x divide-zinc-800/50">
      <div className="p-3">
        <p className="text-[10px] text-green-500 font-black mb-2 flex items-center gap-1">🟢 ALIŞ <span className="text-zinc-600 font-normal ml-auto">Lot</span></p>
        {[...Array(5)].map((_, i) => (
          <div key={i} className="flex justify-between items-center mb-1.5">
            <span className="text-xs font-mono text-zinc-300">{(285.5 - i * 0.05).toFixed(2)}</span>
            <span className="text-xs font-mono text-zinc-500">{(Math.random() * 50000).toFixed(0)}</span>
          </div>
        ))}
      </div>
      <div className="p-3">
        <p className="text-[10px] text-red-500 font-black mb-2 flex items-center gap-1 text-right">🔴 SATIŞ <span className="text-zinc-600 font-normal ml-auto">Lot</span></p>
        {[...Array(5)].map((_, i) => (
          <div key={i} className="flex justify-between items-center mb-1.5 direction-rtl">
            <span className="text-xs font-mono text-zinc-500">{(Math.random() * 50000).toFixed(0)}</span>
            <span className="text-xs font-mono text-zinc-300">{(285.55 + i * 0.05).toFixed(2)}</span>
          </div>
        ))}
      </div>
    </div>
  </div>
);

const AKDView = ({ data }: { data: any }) => (
  <div className="space-y-3">
    <div className="grid grid-cols-1 gap-3">
      <AKDTable title="EN ÇOK ALANLAR" color="green" brokers={data?.buyers || []} />
      <AKDTable title="EN ÇOK SATANLAR" color="red" brokers={data?.sellers || []} />
    </div>
  </div>
);

const AKDTable = ({ title, color, brokers }: any) => (
  <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl overflow-hidden">
    <div className="px-3 py-2 border-b border-zinc-800 flex justify-between">
      <h4 className="text-[9px] font-black text-zinc-400 tracking-wider uppercase">{title}</h4>
      <span className="text-[9px] font-bold text-zinc-600">PAY (%)</span>
    </div>
    <div className="p-2 space-y-1">
      {brokers.length > 0 ? brokers.map((b: any, i: number) => {
        const payVal = i === 0 ? 80 : Math.max(10, 100 - i * 20); // Dummy bar width if no real pay
        return (
          <div key={i} className="space-y-1">
            <div className="flex justify-between items-center px-1">
              <span className="text-[11px] font-medium text-zinc-200">{b.kurum}</span>
              <span className="text-[11px] font-mono text-zinc-400">{b.lot}</span>
            </div>
            <div className="h-1 bg-zinc-800/50 rounded-full overflow-hidden">
              <div
                className={`h-full ${color === 'green' ? 'bg-green-500' : 'bg-red-500'}`}
                style={{ width: `${payVal}%` }}
              ></div>
            </div>
          </div>
        );
      }) : <p className="text-center py-4 text-[11px] text-zinc-600">Veri bulunamadı.</p>}
    </div>
  </div>
);

const TakasView = ({ data }: { data: any }) => (
  <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl overflow-hidden">
    <table className="w-full text-left text-[11px]">
      <thead className="bg-zinc-950/50 text-zinc-500 uppercase font-black text-[9px] tracking-wider">
        <tr>
          <th className="px-4 py-2 border-b border-zinc-800">KURUM</th>
          <th className="px-4 py-2 border-b border-zinc-800 text-right">TOPLAM LOT</th>
          <th className="px-4 py-2 border-b border-zinc-800 text-right">% PAY</th>
        </tr>
      </thead>
      <tbody className="divide-y divide-zinc-800/30">
        {data?.holders?.map((h: any, i: number) => (
          <tr key={i} className="hover:bg-zinc-800/20 transition-colors">
            <td className="px-4 py-2 text-zinc-200 font-medium">{h.kurum}</td>
            <td className="px-4 py-2 font-mono text-zinc-400 text-right">{h.toplam_lot}</td>
            <td className="px-4 py-2 font-mono text-cyan-500 text-right">{h.pay}</td>
          </tr>
        ))}
      </tbody>
    </table>
    {(!data?.holders || data.holders.length === 0) && <p className="text-center py-6 text-[11px] text-zinc-600 italic">Takas verisi yüklenemedi.</p>}
  </div>
);

const GrafikView = ({ symbol }: { symbol: string }) => (
  <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl overflow-hidden aspect-video relative">
    {/* TradingView Widget Simülasyonu ya da Iframe */}
    <div className="absolute inset-0 flex items-center justify-center bg-[#131722]">
      <iframe
        src={`https://s.tradingview.com/widgetembed/?frameElementId=tradingview_762ae&symbol=BIST%3A${symbol}&interval=D&hidesidetoolbar=1&symboledit=1&saveimage=1&toolbarbg=f1f3f6&studies=[]&theme=dark&style=1&timezone=Etc%2FUTC&studies_overrides={}&overrides={}&enabled_features=[]&disabled_features=[]&locale=tr`}
        style={{ width: '100%', height: '100%', border: 'none' }}
      ></iframe>
    </div>
  </div>
);

export default App;
