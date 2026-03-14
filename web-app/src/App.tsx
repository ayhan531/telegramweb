import React, { useEffect, useState } from 'react';
import { Search, Building2, MoreHorizontal, Briefcase, Home, Star, Activity, ArrowLeft, RefreshCw, ChevronDown, Bell, ArrowUpRight, ArrowDownRight, Copy, Zap } from 'lucide-react';
import axios from 'axios';
import Chart from 'react-apexcharts';
import { io } from 'socket.io-client';
import logo from './assets/logo.png';

const API_BASE = '/api';

declare global {
  interface Window { Telegram: { WebApp: any; }; }
}

const App: React.FC = () => {
  const [currentView, setCurrentView] = useState('anasayfa');
  const [symbol, setSymbol] = useState('');
  const [akdData, setAkdData] = useState<any>(null);
  const [user, setUser] = useState<any>(null);
  const [bultenData, setBultenData] = useState<any>(null);
  const [fonData, setFonData] = useState<any>(null);
  const [favorites, setFavorites] = useState<string[]>([]);
  const [alarms, setAlarms] = useState<any[]>([]);
  const [bultenLoading, setBultenLoading] = useState(false);
  const [fonLoading, setFonLoading] = useState(false);
  const [showSplash, setShowSplash] = useState(true);
  const [fadingSplash, setFadingSplash] = useState(false);
  const [livePrices, setLivePrices] = useState<Record<string, any>>({});
  const [marketSignals, setMarketSignals] = useState<any[]>([]);

  useEffect(() => {
    // Socket.io Connection
    const socket = io();
    
    socket.on('price_update', (data) => {
      setLivePrices(prev => ({ ...prev, [data.symbol]: data }));
    });

    socket.on('market_signals', (signals) => {
      setMarketSignals(signals);
      // Optional: Show a toast/notification if the user is not on signals view
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  useEffect(() => {
    try {
      const WebApp = window.Telegram?.WebApp;
      if (WebApp) {
        WebApp.ready();
        WebApp.expand();
        WebApp.setHeaderColor('#000000');
        WebApp.setBackgroundColor('#000000');

        axios.interceptors.request.use(config => {
          config.headers['x-telegram-init-data'] = WebApp.initData;
          return config;
        });

        if (WebApp.initDataUnsafe?.user) {
          setUser(WebApp.initDataUnsafe.user);
        }
      }
    } catch (err) {
      console.error(err);
    }

    const fetchGlobalData = () => {
      setBultenLoading(false); // First load handles initial screen, polling should be silent
      setFonLoading(false);

      axios.get(`${API_BASE}/akd/THYAO`).then((res: any) => setAkdData(res.data)).catch(console.error);
      axios.get(`${API_BASE}/bulten`).then((res: any) => setBultenData(res.data)).catch(console.error).finally(() => setBultenLoading(false));
      axios.get(`${API_BASE}/fon`).then((res: any) => setFonData(res.data)).catch(console.error).finally(() => setFonLoading(false));
    };

    setBultenLoading(true);
    setFonLoading(true);
    fetchGlobalData();

    const interval = setInterval(fetchGlobalData, 30000); // 30 saniyede bir ana verileri yenile

    // Splash Screen Timer
    const splashTimer = setTimeout(() => {
      setFadingSplash(true);
      setTimeout(() => setShowSplash(false), 800);
    }, 2800);

    return () => {
      clearInterval(interval);
      clearTimeout(splashTimer);
    };
  }, []);

  useEffect(() => {
    if (user?.id) {
      axios.get(`${API_BASE}/favorites/${user.id}`).then((res: any) => setFavorites(res.data)).catch(console.error);
      axios.get(`${API_BASE}/alarms/${user.id}`).then((res: any) => setAlarms(res.data)).catch(console.error);
    }
  }, [user]);

  const refreshAlarms = () => {
    if (user?.id) axios.get(`${API_BASE}/alarms/${user.id}`).then(res => setAlarms(res.data)).catch(console.error);
  };

  const toggleFavorite = async (s: string) => {
    if (!user?.id) return;
    const isFav = favorites.includes(s.toUpperCase());
    try {
      if (isFav) {
        await axios.delete(`${API_BASE}/favorites`, { data: { userId: user.id, symbol: s } });
        setFavorites((prev: string[]) => prev.filter((f: string) => f !== s.toUpperCase()));
      } else {
        await axios.post(`${API_BASE}/favorites`, { userId: user.id, symbol: s });
        setFavorites((prev: string[]) => [...prev, s.toUpperCase()]);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const renderContent = () => {
    if (symbol) {
      return <SymbolDetail symbol={symbol} favorites={favorites} onToggleFavorite={toggleFavorite} onBack={() => setSymbol('')} user={user} />;
    }

    switch (currentView) {
      case 'anasayfa': return <Anasayfa user={user} bultenData={bultenData} favorites={favorites} onSearch={(s: string) => setSymbol(s)} onToggleFavorite={toggleFavorite} livePrices={livePrices} marketSignals={marketSignals} />;
      case 'kurumsal': return <Kurumsal akdData={akdData} />;
      case 'bulten': return bultenLoading ? <LoadingView label="Bülten hazırlanıyor..." /> : <Bulten data={bultenData} user={user} />;
      case 'fon': return fonLoading ? <LoadingView label="Fonlar listeleniyor..." /> : <Fon data={fonData} />;
      case 'diger': return <Diger signals={marketSignals} />;
      case 'alarm': return <AlarmView user={user} alarms={alarms} onRefresh={refreshAlarms} />;
      default: return <Anasayfa user={user} bultenData={bultenData} favorites={favorites} onSearch={(s: string) => setSymbol(s)} onToggleFavorite={toggleFavorite} />;
    }
  };

  return (
    <div className="flex flex-col h-screen bg-black text-white font-sans overflow-hidden">
      <div className="flex-1 overflow-y-auto pb-28">
        {renderContent()}
      </div>

      {!symbol && (
        <>
          <footer className="fixed bottom-4 left-4 right-4 bg-[#0a0a0c] border border-white/10 rounded-[28px] p-2 flex justify-between items-center z-50 shadow-2xl shadow-black/50">
            <NavButton id="anasayfa" icon={Home} label="Anasayfa" active={currentView === 'anasayfa'} onClick={setCurrentView} />
            <NavButton id="kurumsal" icon={Building2} label="Kurumsal" active={currentView === 'kurumsal'} onClick={setCurrentView} />
            <NavButton id="diger" icon={MoreHorizontal} label="Diğer" active={currentView === 'diger'} onClick={setCurrentView} />
            <NavButton id="fon" icon={Briefcase} label="Fon" active={currentView === 'fon'} onClick={setCurrentView} />
            <NavButton id="alarm" icon={Bell} label="Alarm" active={currentView === 'alarm'} onClick={setCurrentView} badge={alarms.length} />
          </footer>
          <div className="fixed bottom-0 left-0 right-0 text-center py-1 bg-black/80 backdrop-blur-sm z-40">
             <span className="text-[9px] font-black text-zinc-600 uppercase tracking-[0.2em]">PARİBU MENKUL DEĞER — PROFESYONEL VERİ TERMİNALİ</span>
          </div>
        </>
      )}

      {showSplash && (
        <div className={`splash-overlay ${fadingSplash ? 'splash-exit' : ''}`}>
          <div className="splash-bg-glow" />
          <div className="splash-logo-container">
            <img src={logo} alt="Logo" className="splash-logo" />
            <h1 className="splash-title">PARİBU</h1>
            <p className="splash-subtitle">MENKUL DEĞER</p>
            <div className="splash-progress-container">
              <div className="splash-progress-bar" />
            </div>
          </div>
          <div className="splash-footer text-[10px] opacity-20">PROFESYONEL VERİ TERMİNALİ v1.0</div>
        </div>
      )}
    </div>
  );
};

const LoadingView = ({ label }: { label: string }) => (
  <div className="flex flex-col items-center justify-center pt-40 animate-fade-in text-center px-10">
    <div className="relative mb-6">
      <RefreshCw className="w-12 h-12 text-cyan-400 animate-spin" />
      <Zap className="w-5 h-5 text-yellow-400 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 animate-pulse" />
    </div>
    <div className="text-white font-black text-xl tracking-tight mb-2">{label}</div>
    <div className="text-[12px] text-zinc-500 font-medium">Foreks (Bigpara) altyapısı ile gerçek zamanlı veriler işleniyor...</div>
  </div>
);

// ======================== NAVIGATION ========================
const NavButton = ({ id, icon: Icon, label, active, onClick, badge }: any) => (
  <button onClick={() => onClick(id)} className="flex flex-col items-center flex-1 py-1 relative">
    <div className={`p-2.5 rounded-[14px] mb-1 transition-all ${active ? 'bg-[#222226] text-white' : 'text-zinc-500'}`}>
      <Icon className={`w-5 h-5 ${active ? 'stroke-[2.5px]' : 'stroke-2'}`} />
      {badge > 0 && (
        <span className="absolute top-0 right-1 w-4 h-4 bg-red-500 text-white text-[9px] font-black rounded-full flex items-center justify-center">{badge > 9 ? '9+' : badge}</span>
      )}
    </div>
    <span className={`text-[10px] ${active ? 'font-bold text-white' : 'font-medium text-zinc-500'}`}>{label}</span>
  </button>
);

// ======================== VIEWS ========================

const HeaderBar = ({ title }: { title: string }) => (
  <div className="flex items-center gap-3 p-4 border-b border-white/5 pb-3">
    <ArrowLeft className="w-5 h-5 text-white" />
    <div className="w-8 h-8 bg-[#0a0a0c] border border-white/10 rounded-full flex items-center justify-center">
      <Activity className="w-4 h-4 text-white" />
    </div>
    <span className="font-medium text-[15px] text-zinc-100">{title}</span>
  </div>
);

const Anasayfa = ({ user, bultenData, favorites, onSearch, onToggleFavorite, livePrices, marketSignals }: any) => {
  const [marketTab, setMarketTab] = useState('BIST');
  const [val, setVal] = useState('');

  const handleSearchKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && val.trim()) {
      onSearch(val.trim().toUpperCase());
    }
  };

  const filteredFavorites = favorites.filter((f: any) => f.includes(val.toUpperCase()));

  return (
    <div className="animate-fade-in animate-duration-200">
      <div className="p-4">
        {/* Search Header */}
        <form onSubmit={(e) => { e.preventDefault(); if (val) onSearch(val); }} className="flex gap-3 mb-6 items-center">
          <div className="w-[46px] h-[46px] flex-shrink-0 rounded-[14px] overflow-hidden border border-white/10">
            <img src={logo} alt="Logo" className="w-full h-full object-cover" />
          </div>
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500 w-4 h-4" />
            <input
              type="text"
              placeholder="Hisse ara..."
              value={val}
              onChange={e => setVal(e.target.value)}
              onKeyDown={handleSearchKeyPress}
              className="w-full bg-[#141417] border border-white/5 rounded-2xl py-3 pl-10 pr-4 text-[15px] focus:outline-none focus:border-white/10 text-white placeholder:text-zinc-600 transition-all font-medium"
            />
          </div>
          <div className="w-[46px] h-[46px] flex-shrink-0 rounded-[14px] bg-[#222226] text-white flex items-center justify-center font-bold text-lg shadow-sm border border-white/5 uppercase">
            {user?.first_name ? user.first_name.charAt(0) : 'P'}
          </div>
        </form>

        <div className="flex justify-between items-end mb-4">
          <div>
            <h2 className="text-[22px] font-bold tracking-tight text-white flex items-center gap-2">
              {user?.first_name ? `Hoş geldin ${user.first_name}` : 'Hoş geldiniz'}
              {new Date().getDay() === 0 ? <Briefcase className="w-5 h-5 text-zinc-500" /> : <Activity className="w-5 h-5 text-[#30d158]" />}
            </h2>
            <div className="text-zinc-500 text-[11px] font-bold uppercase tracking-wider mt-1">{bultenData?.date || 'PIYASA ÖZETİ'}</div>
          </div>
          <div className="text-right">
            <div className="text-zinc-500 text-[10px] font-black uppercase mb-1">{bultenData?.index_name || 'BIST 100'}</div>
            <div className="flex items-center gap-2 justify-end font-black">
              <span className="text-lg">{bultenData?.price || '---'}</span>
              <span className={`text-[11px] px-1.5 py-0.5 rounded ${bultenData?.change?.includes('+') ? 'bg-[#00ff88]/10 text-[#00ff88]' : 'bg-[#ff3b30]/10 text-[#ff3b30]'}`}>
                {bultenData?.change || '0.00%'}
              </span>
            </div>
          </div>
        </div>

        {/* Market Quick Overview */}
        <div className="flex gap-2 overflow-x-auto no-scrollbar py-2 -mx-4 px-4">
          <QuickStat title="ALTIN (GRAM)" value={bultenData?.commodity_summary?.[0]?.price} change={bultenData?.commodity_summary?.[0]?.change} />
          <QuickStat title="BITCOIN" value={bultenData?.crypto_summary?.[0]?.price} change={bultenData?.crypto_summary?.[0]?.change} color="text-orange-400" />
          <QuickStat title="DOLAR" value={bultenData?.commodity_summary?.[1]?.price} change={bultenData?.commodity_summary?.[1]?.change} color="text-cyan-400" />
        </div>

        {/* Robot Eye Signals (Live) */}
        {marketSignals && marketSignals.length > 0 && (
          <div className="mt-4 animate-fade-in">
            <div className="text-[10px] font-black text-zinc-600 uppercase tracking-widest mb-3 flex items-center gap-2">
              <span className="w-2 h-2 bg-cyan-400 rounded-full animate-ping"></span> 🤖 ROBOT GÖZÜ CANLI SİNYALLER
            </div>
            <div className="flex gap-3 overflow-x-auto no-scrollbar pb-2">
              {marketSignals.map((sig: any, i: number) => (
                <div key={i} onClick={() => onSearch(sig.symbol)} className="min-w-[200px] soft-card p-3 border-l-4" style={{ borderColor: sig.signals[0].color }}>
                  <div className="flex justify-between items-center mb-1">
                    <span className="font-black text-[14px]">{sig.symbol}</span>
                    <span className="text-[9px] font-bold text-zinc-500">{sig.time}</span>
                  </div>
                  <div className="text-[11px] font-bold" style={{ color: sig.signals[0].color }}>{sig.signals[0].label}</div>
                  <div className="text-[10px] text-zinc-500 mt-1 uppercase font-bold tracking-tight">Fiyat: {sig.price} • RSI: {sig.rsi}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="w-full h-[1px] bg-white/5"></div>

      {/* Mini Active Lists */}
      <div className="px-4 py-4 grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <div className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider mb-2 flex items-center gap-1.5 overflow-hidden">
            <span className="w-1 h-3 bg-[#00ff88] rounded-full"></span> EN ÇOK ARTANLAR
          </div>
          {bultenData?.gainers?.slice(0, 5).map((g: any, i: number) => (
            <div key={i} onClick={() => onSearch(g.symbol)} className="soft-card p-3 flex justify-between items-center active:bg-white/5 transition-all">
              <span className="font-bold text-[14px]">{g.symbol}</span>
              <span className="metric-up text-[12px] font-bold">{g.change}</span>
            </div>
          ))}
        </div>
        <div className="space-y-2">
          <div className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider mb-2 flex items-center gap-1.5 overflow-hidden">
            <span className="w-1 h-3 bg-[#ff3b30] rounded-full"></span> EN ÇOK DÜŞENLER
          </div>
          {bultenData?.losers?.slice(0, 5).map((l: any, i: number) => (
            <div key={i} onClick={() => onSearch(l.symbol)} className="soft-card p-3 flex justify-between items-center active:bg-white/5 transition-all">
              <span className="font-bold text-[14px]">{l.symbol}</span>
              <span className="metric-down text-[12px] font-bold">{l.change}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="px-4 mb-6">
        <div className="soft-card p-4 bg-gradient-to-br from-[#111114] to-[#0a0a0c] border border-white/5">
          <h4 className="text-[10px] font-black text-zinc-600 uppercase tracking-widest mb-3">BIST 100 ANALİZ ÖZETİ</h4>
          <div className="grid grid-cols-3 gap-2">
            <div className="text-center">
              <div className="text-[10px] text-zinc-500 font-bold mb-1">ENDEKS</div>
              <div className="text-[15px] font-black text-white">{bultenData?.price || '---'}</div>
            </div>
            <div className="text-center border-x border-white/5">
              <div className="text-[10px] text-zinc-500 font-bold mb-1">DEĞİŞİM</div>
              <div className={`text-[15px] font-black ${bultenData?.change?.includes('+') ? 'text-[#00ff88]' : 'text-[#ff3b30]'}`}>{bultenData?.change || '---'}</div>
            </div>
            <div className="text-center">
              <div className="text-[10px] text-zinc-500 font-bold mb-1">DURUM</div>
              <div className={`text-[13px] font-black ${bultenData?.status === 'POZİTİF' ? 'text-[#00ff88]' : 'text-[#ff3b30]'}`}>{bultenData?.status || '---'}</div>
            </div>
          </div>
        </div>
      </div>

      <div className="w-full h-[1px] bg-white/5 mb-6"></div>

      {/* Market Tabs */}
      <div className="flex px-4 gap-2">
        {['BIST', 'KRİPTO', 'EMTİA'].map((t: string) => (
          <button
            key={t}
            onClick={() => setMarketTab(t)}
            className={`px-4 py-2 rounded-xl text-[13px] font-bold transition-all border ${marketTab === t ? 'bg-white/10 border-white/20 text-white' : 'border-transparent text-zinc-500'}`}
          >
            {t}
          </button>
        ))}
      </div>

      <div className="p-4 pt-4">
        <div className="flex justify-between items-center mb-4 px-1">
          <h3 className="text-sm font-bold text-zinc-500 uppercase tracking-widest">{marketTab} Favoriler</h3>
          <span className="text-[11px] font-bold text-zinc-600 bg-white/5 px-2 py-0.5 rounded-full">{filteredFavorites.length}/50</span>
        </div>

        {filteredFavorites.length === 0 ? (
          <div className="flex flex-col items-center justify-center pt-10 pb-20 text-center px-6">
            <Star className="w-14 h-14 text-[#222226] mb-4" strokeWidth={1} />
            <h3 className="text-[17px] font-bold tracking-wide">{val ? 'Sonuç Bulunamadı' : '"Favoriler" Listesi Boş'}</h3>
            <p className="text-zinc-500 text-[13px] mt-2 leading-relaxed max-w-[280px]">
              {val ? 'Aradığınız kritere uygun favori hisse bulunamadı.' : 'Hisse ararken yıldız butonuna tıklayarak bu listeye hisse ekleyebilirsiniz.'}
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-3">
            {filteredFavorites.map((fav: string) => (
              <FavoriteCard key={fav} symbol={fav} onSelect={onSearch} onRemove={() => onToggleFavorite(fav)} livePrice={livePrices[fav]} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

const QuickStat = ({ title, value, change, color = 'text-white' }: any) => (
  <div className="min-w-[130px] soft-card p-3.5 flex flex-col justify-between">
    <div className="text-[11px] font-semibold text-zinc-500 mb-2">{title}</div>
    <div className={`text-[17px] font-bold truncate ${color}`}>{value || '---'}</div>
    <div className={`text-[12px] font-semibold mt-1 ${change?.includes('+') ? 'metric-up' : 'metric-down'}`}>
      {change || '0.00%'}
    </div>
  </div>
);

const FavoriteCard = ({ symbol, onSelect, onRemove, livePrice }: any) => {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    const fetchData = () => {
      axios.get(`${API_BASE}/stock/${symbol}`).then((res: any) => setData(res.data)).catch(console.error);
    };

    fetchData();
  }, [symbol]);

  // Use live price if available, fallback to static data
  const displayPrice = livePrice?.price || data?.price || '---';
  const displayChange = livePrice?.change !== undefined ? livePrice.change : (data?.change || 0);

  return (
    <div onClick={() => onSelect(symbol)} className="soft-card p-4 active:scale-[0.98] transition-all relative group cursor-pointer border border-white/5 hover:border-white/20">
      <div className="flex justify-between items-start mb-2">
        <span className="font-bold text-[15px]">{symbol}</span>
        <button onClick={(e) => { e.stopPropagation(); onRemove(); }} className="text-[#ff9d00]">
          <Star className="w-4 h-4 fill-[#ff9d00]" />
        </button>
      </div>
      <div className="flex justify-between items-end">
        <div className={`text-[18px] font-bold ${livePrice ? 'text-cyan-400 animate-pulse-fast' : ''}`}>{displayPrice}</div>
        <div className={`text-[11px] font-bold ${displayChange >= 0 ? 'text-[#00ff88]' : 'text-[#ff3b30]'}`}>
          {displayChange >= 0 ? '+' : ''}{displayChange?.toFixed(2)}%
        </div>
      </div>
    </div>
  );
};

// 2. KURUMSAL (AKD Equivalent)
const Kurumsal = ({ akdData: initialAkdData }: { akdData: any }) => {
  const [tab, setTab] = useState('alanlar');
  const [akdData, setAkdData] = useState(initialAkdData);
  const [searchSymbol, setSearchSymbol] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setAkdData(initialAkdData);
  }, [initialAkdData]);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchSymbol) return;
    setLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/akd/${searchSymbol.toUpperCase()}`);
      setAkdData(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const generateBrokerRow = (b: any, index: number, isSeller: boolean) => {
    const letters = b.kurum.substring(0, 2).toUpperCase();
    const isBofa = b.kurum.toLowerCase().includes('bank of');
    const color = isSeller ? '#ff3b30' : '#00ff88';
    const bgBadge = isSeller ? '#350f0c' : '#002f1a';
    const borderBadge = isSeller ? '#5c1713' : '#00502a';

    return (
      <div key={index} className="flex justify-between items-center py-3 border-b border-white/5 last:border-0 hover:bg-white/[0.02] active:bg-white/[0.05] transition-colors -mx-4 px-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-white flex items-center justify-center overflow-hidden flex-shrink-0">
            {isBofa ? (
              <div className="w-full h-full bg-white text-red-600 font-extrabold text-xl flex items-center justify-center border-2 border-red-600">B</div>
            ) : (
              <span className="text-black font-black text-sm">{letters}</span>
            )}
          </div>
          <div>
            <div className="font-bold text-[15px] text-white leading-tight">{b.kurum}</div>
            <div className="text-[12px] text-zinc-500 mt-0.5">{b.kurum} Yatırım</div>
          </div>
        </div>
        <div className="text-right flex flex-col items-end">
          <div className="flex items-center gap-2">
            <span className={`font-bold text-[15px]`} style={{ color }}>{b.lot}</span>
            <span className="px-1.5 py-0.5 rounded flex items-center justify-center text-[11px] font-bold"
              style={{ backgroundColor: bgBadge, color: color, borderColor: borderBadge, borderWidth: '1px' }}>
              %{(b.pay || (40 - index * 5)).toFixed(2)}
            </span>
            <ChevronDown className="w-3 h-3 text-zinc-600 -rotate-90 ml-1" />
          </div>
          <div className="text-[11px] text-zinc-500 mt-1">{b.maliyet !== '---' ? `Mal: ${b.maliyet}` : `${(80 - index * 10).toFixed(1)} Mr ₺`}</div>
        </div>
      </div>
    );
  };

  return (
    <div className="animate-fade-in pb-10">
      <HeaderBar title={`AKD Terminali ${akdData?.symbol ? `— ${akdData.symbol}` : ''}`} />

      {/* Selectors */}
      <div className="p-4 pt-2">
        <form onSubmit={handleSearch} className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500 w-4 h-4" />
            <input
              type="text"
              placeholder="Hisse sembolü (örn: THYAO)..."
              value={searchSymbol}
              onChange={e => setSearchSymbol(e.target.value)}
              className="w-full soft-card-inner py-3 pl-10 pr-3 text-[13px] focus:outline-none text-white transition-all font-medium"
            />
          </div>
          <button type="submit" className="w-11 h-11 flex-shrink-0 soft-card-inner flex items-center justify-center cursor-pointer active:scale-95 transition-transform">
            {loading ? <RefreshCw className="w-4 h-4 text-cyan-400 animate-spin" /> : <Activity className="w-4 h-4 text-zinc-400" />}
          </button>
        </form>
      </div>

      <div className="flex gap-2 px-4 mb-2 overflow-x-auto no-scrollbar">
        <div className="relative flex-1 soft-card-inner flex items-center px-3 py-2 cursor-pointer whitespace-nowrap">
          <span className="text-[11px] font-medium text-zinc-400">{akdData?.date || 'Bugün'}</span>
        </div>
        <div className="relative flex-1 soft-card-inner flex items-center px-3 py-2 cursor-pointer whitespace-nowrap">
          <span className="text-[11px] font-medium text-zinc-400">{akdData?.status || 'Güncel'}</span>
        </div>
        <div className="relative flex-1 soft-card-inner flex items-center px-3 py-2 cursor-pointer whitespace-nowrap">
          <span className="text-[11px] font-medium text-zinc-200">{akdData?.source || 'İş Yatırım'}</span>
        </div>
      </div>

      {/* Header Tabs */}
      <div className="flex px-4 mt-2">
        <button onClick={() => setTab('alanlar')} className={`flex-1 pb-3 text-[14px] font-bold border-b-2 transition-colors ${tab === 'alanlar' ? 'border-[#00ff88] text-[#00ff88] bg-[#00ff88]/[0.05] rounded-t-xl pt-2' : 'border-white/5 text-zinc-500 pt-2'}`}>
          Alanlar
        </button>
        <button onClick={() => setTab('satanlar')} className={`flex-1 pb-3 text-[14px] font-bold border-b-2 transition-colors ${tab === 'satanlar' ? 'border-[#ff3b30] text-[#ff3b30] bg-[#ff3b30]/[0.05] rounded-t-xl pt-2' : 'border-white/5 text-zinc-500 pt-2'}`}>
          Satanlar
        </button>
        <button onClick={() => setTab('toplam')} className={`flex-1 pb-3 text-[14px] font-bold border-b-2 transition-colors ${tab === 'toplam' ? 'border-zinc-100 text-zinc-100 bg-white/[0.05] rounded-t-xl pt-2' : 'border-white/5 text-zinc-500 pt-2'}`}>
          Diğer
        </button>
      </div>

      <div className="px-4 py-2 mt-1">
        {loading ? (
          <div className="flex flex-col items-center justify-center pt-20">
            <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin mb-3" />
            <div className="text-zinc-500 font-medium">Veriler çekiliyor...</div>
          </div>
        ) : (
          (!akdData || akdData.error || (akdData.buyers?.length === 0 && akdData.sellers?.length === 0)) ? (
            <div className="flex flex-col items-center justify-center pt-20 text-center px-6">
              <Activity className="w-12 h-12 text-zinc-800 mb-4" />
              <div className="text-zinc-500 font-medium">Bu sembol için AKD verisi şu an mevcut değil. Lütfen başka bir sembol deneyin.</div>
            </div>
          ) : (
            tab === 'toplam' ? (
              <div className="space-y-4">
                <div className="p-4 bg-white/5 rounded-2xl border border-white/5">
                  <h4 className="text-[11px] font-bold text-zinc-500 uppercase mb-3">İşlem Özeti</h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="text-[10px] text-zinc-600 font-bold uppercase">Kaynak</div>
                      <div className="text-[13px] font-bold text-zinc-300">{akdData.source}</div>
                    </div>
                    <div>
                      <div className="text-[10px] text-zinc-600 font-bold uppercase">Durum</div>
                      <div className="text-[13px] font-bold text-[#00ff88]">{akdData.status}</div>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              (tab === 'alanlar' ? akdData?.buyers : akdData?.sellers)?.map((b: any, i: number) => generateBrokerRow(b, i, tab === 'satanlar'))
            )
          )
        )}
      </div>
    </div>
  );
};

// 3. BULTEN
const Bulten = ({ data, user }: { data: any, user: any }) => (
  <div className="animate-fade-in">
    <HeaderBar title="Veri Terminali" />

    <div className="px-5 py-2">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-black text-[#ffb04f] tracking-tight">Bülten</h1>
        <div className="flex items-center gap-3 relative top-2">
          <span className="text-zinc-400 text-sm font-medium">{data?.date || '22 Şubat Pazar'}</span>
          <span className="bg-[#002f1a] text-[#00ff88] text-[11px] font-black px-2.5 py-1 rounded border border-[#00502a] tracking-wider">{data?.status || 'POZİTİF'}</span>
          <button className="w-8 h-8 rounded-lg bg-[#111114] border border-white/10 flex items-center justify-center disabled:opacity-50">
            <Copy className="w-4 h-4 text-zinc-400" />
          </button>
        </div>
      </div>

      <div className="flex justify-between items-start mb-4">
        <h2 className="text-xl font-bold tracking-tight">{data?.index_name || 'BIST 100'}</h2>
        <div className="text-right">
          <div className="text-[22px] font-black leading-none">{data?.price || '13934,06'}</div>
          <div className={`text-sm font-bold mt-1 ${data?.change?.includes('+') ? 'text-[#00ff88]' : 'text-[#ff3b30]'}`}>{data?.change || '+0.94%'}</div>
        </div>
      </div>

      <p className="text-zinc-400 text-[15px] leading-relaxed mb-6 font-medium">
        BIST 100 endeksi, günü <span className={`${data?.change?.includes('+') ? 'text-[#00ff88]' : 'text-[#ff3b30]'} font-bold`}>{data?.change || '%0.94'} yükselişle {data?.price || '13934,06'}</span> seviyesinden tamamladı. Gün içerisinde işlem hacmi <span className="text-[#ffb04f] font-bold">171.4 Milyar TL</span> olarak gerçekleşti.
      </p>

      <p className="text-white text-base mb-6 font-medium tracking-tight">
        Merhaba <span className="font-extrabold text-[#38bdf8]">{user?.first_name || 'Yatırımcı'}</span>, piyasa özetiniz hazır.
      </p>

      <div className="grid grid-cols-1 gap-4 mb-6">
        <div className="grid grid-cols-2 gap-3">
          <MarketSection title="Yükselenler" data={data?.gainers} color="#00ff88" />
          <MarketSection title="Düşenler" data={data?.losers} color="#ff3b30" />
        </div>
        <MarketSection title="BIST 100 Özet" data={data?.bist_summary} color="#60a5fa" />
        <MarketSection title="Kripto Para / Binance" data={data?.crypto_summary} color="#ffb04f" />
        <MarketSection title="Emtia / Forex (TradingView)" data={data?.commodity_summary} color="#818cf8" />
      </div>
    </div>
  </div>
);

const MarketSection = ({ title, data }: any) => (
  <div className="soft-card overflow-hidden">
    <div className="px-5 py-3.5 font-semibold border-b border-white/5 text-[15px]">{title}</div>
    <div className="flex flex-col">
      {(data && data.length > 0) ? data.map((item: any, i: number) => (
        <div key={i} className="flex justify-between items-center px-4 py-3 border-b border-white/5 last:border-0">
          <span className="font-bold text-[14px]">{item.symbol}</span>
          <div className="text-right">
            <div className="text-sm font-bold text-white">{item.price}</div>
            <div className={`text-[11px] font-bold ${item.change.includes('+') ? 'text-[#00ff88]' : 'text-[#ff3b30]'}`}>{item.change}</div>
          </div>
        </div>
      )) : (
        <div className="p-4 text-xs text-zinc-600 text-center">Veri Alınamadı</div>
      )}
    </div>
  </div>
);

// 4. DIGER
const Diger = ({ signals }: { signals: any[] }) => {
  const [selectedSubView, setSelectedSubView] = useState<string | null>(null);

  const handleMenuItemClick = (view: string) => {
    setSelectedSubView(view);
  };

  const handleBack = () => {
    setSelectedSubView(null);
  };

  if (selectedSubView) {
    return <SubViewDetail view={selectedSubView} onBack={handleBack} signals={signals} />;
  }

  return (
    <div className="animate-fade-in">
      <HeaderBar title="Veri Terminali" />

      <div className="mt-8 mb-4 relative">
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-8 h-1 bg-white/10 rounded-full absolute -top-5"></div>
        </div>
        <h3 className="text-center font-bold text-lg">Diğer</h3>
      </div>

      <div className="px-4 space-y-2 pb-10">
        {signals && signals.length > 0 && (
            <DigerMenuItem icon={Zap} title="Robot Gözü" subtitle={`${signals.length} Aktif Sinyal Bulundu`} color="text-yellow-400" bg="bg-yellow-400/10" onClick={() => handleMenuItemClick('Robot Gözü')} />
        )}
        <DigerMenuItem icon={Search} title="Hisse Radar" subtitle="Hisse tarama ve filtreleme" color="text-cyan-400" bg="bg-cyan-400/10" onClick={() => handleMenuItemClick('Hisse Radar')} />
        <DigerMenuItem icon={Activity} title="Teknik Tarama" subtitle="Teknik strateji taramaları" color="text-red-400" bg="bg-red-400/10" onClick={() => handleMenuItemClick('Teknik Tarama')} />
        <DigerMenuItem icon={Search} title="AKD Tarama" subtitle="Kurum alım/satım taraması" color="text-cyan-400" bg="bg-cyan-400/10" onClick={() => handleMenuItemClick('AKD Tarama')} />
        <DigerMenuItem icon={Briefcase} title="Takas Tarama" subtitle="Takas verisi tarama araçları" color="text-indigo-400" bg="bg-indigo-400/10" onClick={() => handleMenuItemClick('Takas Tarama')} />
        <DigerMenuItem icon={Bell} title="KAP Ajan" subtitle="KAP bildirim takip ajanı" color="text-orange-400" bg="bg-orange-400/10" onClick={() => handleMenuItemClick('KAP Ajan')} />
      </div>
    </div>
  );
};

const DigerMenuItem = ({ icon: Icon, title, subtitle, onClick }: any) => (
  <div className="flex items-center gap-4 soft-card p-4 active:bg-white/5 transition-colors cursor-pointer" onClick={onClick}>
    <div className={`w-12 h-12 rounded-[14px] soft-card-inner flex items-center justify-center`}>
      <Icon className={`w-5 h-5 text-white stroke-2`} />
    </div>
    <div className="flex-1">
      <div className="font-semibold text-[16px] text-white">{title}</div>
      <div className="text-[13px] text-zinc-500 mt-0.5">{subtitle}</div>
    </div>
    <ChevronDown className="w-5 h-5 text-zinc-600 -rotate-90" />
  </div>
);

// 5. FON
const Fon = ({ data }: { data: any }) => {
  const [val, setVal] = useState('');
  const [fonCategory, setFonCategory] = useState('Tümü');

  const handleSearchKeyPress = (e: React.KeyboardEvent) => {
    // Fon araması sadece filtreleme yaptığı için özel bir aksiyon gerekmez, 
    // ama Enter'a basıldığında klavyeyi kapatmak yararlı olabilir.
    if (e.key === 'Enter') (e.target as HTMLInputElement).blur();
  };

  const fonKeywords: Record<string, string[]> = {
    'Hisse Senedi': ['hisse', 'portföy', 'thyao', 'eregl', 'akbnk', 'garan', 'sahol'],
    'Altın': ['altın', 'gold', 'gldtr', 'gumus'],
  };

  const filteredFunds = data?.funds?.filter((f: any) => {
    const matchSearch = f.code.toUpperCase().includes(val.toUpperCase()) || f.name.toUpperCase().includes(val.toUpperCase());
    if (fonCategory === 'Tümü') return matchSearch;
    const keywords = fonKeywords[fonCategory] || [];
    const matchCat = keywords.some(k => f.code.toLowerCase().includes(k) || f.name.toLowerCase().includes(k));
    return matchSearch && matchCat;
  }) || [];

  return (
    <div className="animate-fade-in">
      <HeaderBar title="Veri Terminali" />

      <div className="px-4 mt-2">
        <div className="relative mb-6">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500 w-4 h-4" />
          <input
            type="text"
            placeholder="Kodu veya ismiyle ara..."
            value={val}
            onChange={(e) => setVal(e.target.value)}
            onKeyDown={handleSearchKeyPress}
            className="w-full bg-[#111114] border border-white/10 rounded-xl py-3 pl-10 pr-4 text-[15px] focus:outline-none focus:border-white/20 text-white placeholder:text-zinc-600"
          />
        </div>

        <div className="bg-[#0a0a0c] border border-white/5 rounded-2xl overflow-hidden mb-6">
          <h3 className="text-[17px] font-bold text-white p-4 pb-2">Popüler Fonlar</h3>

          <div className="flex px-4 py-2 gap-2 overflow-x-auto hide-scrollbar">
            {['Tümü', 'Hisse Senedi', 'Altın'].map(cat => (
              <button
                key={cat}
                onClick={() => setFonCategory(cat)}
                className={`whitespace-nowrap px-4 py-1.5 rounded-full font-medium text-sm border transition-all ${fonCategory === cat ? 'bg-white/10 border-white text-white' : 'border-white/10 text-zinc-400'
                  }`}
              >{cat}</button>
            ))}
          </div>

          <table className="w-full mt-2">
            <thead>
              <tr className="text-zinc-500 text-[10px] uppercase font-bold text-left border-b border-white/5">
                <th className="pl-4 py-3 font-bold tracking-wider">FON</th>
                <th className="py-3 font-bold tracking-wider">FON ADI</th>
                <th className="pr-4 py-3 text-right font-bold tracking-wider">GÜNLÜK DEĞİŞİM</th>
              </tr>
            </thead>
            <tbody>
              {filteredFunds.length > 0 ? filteredFunds.map((f: any, i: number) => (
                <FonRow key={i} code={f.code} name={f.name} val={f.change} color={f.color} icon={f.icon} />
              )) : (
                <tr><td colSpan={3} className="p-10 text-center text-zinc-600">Aranan kriterde fon bulunamadı</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

const FonRow = ({ code, name, val, color, icon }: any) => (
  <tr className="border-b border-white/[0.02] hover:bg-white/[0.02]">
    <td className="pl-4 py-3.5">
      <div className="flex items-center gap-3">
        {icon === 'INVEO' ? (
          <div className="w-7 h-7 bg-blue-600 rounded-full flex items-center justify-center text-[8px] font-black text-white italic">inveo</div>
        ) : (
          <div className={`w-7 h-7 ${color} rounded-full flex items-center justify-center text-[12px] font-black text-white`}>{icon}</div>
        )}
        <span className="font-bold text-white text-[15px]">{code}</span>
      </div>
    </td>
    <td className="py-3 text-[13px] text-zinc-400 font-medium">{name}</td>
    <td className="pr-4 py-3 text-right font-bold text-[#00ff88] text-[14px]">{val}</td>
  </tr>
);


// 6. SYMBOL DETAIL VIEW (Original Derinlik/Takas Logic)
const SymbolDetail = ({ symbol, favorites, onToggleFavorite, onBack, user }: { symbol: string, favorites: string[], onToggleFavorite: (s: string) => void, onBack: () => void, user?: any }) => {
  const [stock, setStock] = useState<any>(null);
  const [akd, setAkd] = useState<any>(null);
  const [takas, setTakas] = useState<any>(null);
  const [scan, setScan] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [tab, setTab] = useState('derinlik');

  useEffect(() => {
    const fetchAllData = () => {
      axios.get(`${API_BASE}/stock/${symbol}`).then(res => setStock(res.data)).catch(console.error);
      axios.get(`${API_BASE}/scan/${symbol}`).then(res => setScan(res.data)).catch(console.error);
    };

    const fetchStaticData = () => {
      axios.get(`${API_BASE}/akd/${symbol}`).then(res => setAkd(res.data)).catch(console.error);
      axios.get(`${API_BASE}/takas/${symbol}`).then(res => setTakas(res.data)).catch(console.error);
      axios.get(`${API_BASE}/history/${symbol}`).then(res => setHistory(res.data)).catch(console.error);
    };

    fetchAllData();
    fetchStaticData();

    const interval = setInterval(fetchAllData, 10000); // Fiyat ve teknik veriyi 10 saniyede bir güncelle
    return () => clearInterval(interval);
  }, [symbol]);

  return (
    <div className="animate-fade-in bg-black min-h-screen">
      <div className="flex items-center gap-3 p-4 border-b border-white/5 sticky top-0 bg-black/80 backdrop-blur-md z-10">
        <button onClick={onBack} className="p-2 -ml-2 rounded-full hover:bg-white/10 active:bg-white/20 transition-colors">
          <ArrowLeft className="w-6 h-6 text-white" />
        </button>
        <span className="font-bold text-lg text-white">{symbol.toUpperCase()} Detay</span>
      </div>

      {!stock && !stock?.error ? (
        <LoadingView label={`${symbol.toUpperCase()} verileri getiriliyor...`} />
      ) : (
        <div className="p-4 space-y-4 pb-20">
          {stock && (
            <div className="soft-card p-6">
              <div className="flex justify-between items-start mb-6">
                <div>
                  <div className="flex items-center gap-2">
                    <h1 className="text-3xl font-bold tracking-tight text-white">{symbol.toUpperCase()}</h1>
                    <button onClick={() => onToggleFavorite(symbol)}>
                      <Star className={`w-6 h-6 transition-colors ${favorites.includes(symbol.toUpperCase()) ? 'fill-white text-white' : 'text-zinc-600'}`} />
                    </button>
                  </div>
                  <p className="text-xs text-zinc-500 uppercase font-bold tracking-widest mt-1">{stock.name}</p>
                </div>
                <div className="text-right">
                  <p className="text-3xl font-bold font-mono text-white">{stock.price?.toLocaleString('tr-TR', { minimumFractionDigits: 2 })}</p>
                  <p className={`text-sm font-bold mt-1 inline-flex items-center gap-1 ${stock.change >= 0 ? 'text-[#00ff88]' : 'text-[#ff3b30]'}`}>
                    {stock.change >= 0 ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
                    %{Math.abs(stock.change || 0).toFixed(2)}
                  </p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3 pt-4 border-t border-white/5">
                <div className="flex justify-between items-center"><span className="text-[11px] text-zinc-500 font-bold uppercase">Düşük</span><span className="text-sm font-mono font-medium text-zinc-200">{stock.low}</span></div>
                <div className="flex justify-between items-center"><span className="text-[11px] text-zinc-500 font-bold uppercase">Yüksek</span><span className="text-sm font-mono font-medium text-zinc-200">{stock.high}</span></div>
                <div className="flex justify-between items-center"><span className="text-[11px] text-zinc-500 font-bold uppercase">Açılış</span><span className="text-sm font-mono font-medium text-zinc-200">{stock.open}</span></div>
                <div className="flex justify-between items-center"><span className="text-[11px] text-zinc-500 font-bold uppercase">Hacim</span><span className="text-sm font-mono font-medium text-zinc-200">{stock.volume?.toLocaleString('tr-TR')}</span></div>
              </div>
            </div>
          )}

          <div className="flex bg-[#111114] rounded-xl p-1.5 border border-white/5 justify-between gap-1 overflow-x-auto hide-scrollbar">
            <button onClick={() => setTab('derinlik')} className={`flex-1 py-1.5 px-3 text-[11px] font-bold rounded-lg transition-all whitespace-nowrap ${tab === 'derinlik' ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30' : 'text-zinc-500'}`}>Derinlik</button>
            {stock?.exchange === 'BIST' && (
              <>
                <button onClick={() => setTab('teknik')} className={`flex-1 py-1.5 px-3 text-[11px] font-bold rounded-lg transition-all whitespace-nowrap ${tab === 'teknik' ? 'bg-orange-500/20 text-orange-400 border border-orange-500/30' : 'text-zinc-500'}`}>Teknik</button>
                <button onClick={() => setTab('akd')} className={`flex-1 py-1.5 px-3 text-[11px] font-bold rounded-lg transition-all whitespace-nowrap ${tab === 'akd' ? 'bg-red-500/20 text-red-400 border border-red-500/30' : 'text-zinc-500'}`}>AKD</button>
                <button onClick={() => setTab('takas')} className={`flex-1 py-1.5 px-3 text-[11px] font-bold rounded-lg transition-all whitespace-nowrap ${tab === 'takas' ? 'bg-indigo-500/20 text-indigo-400 border border-indigo-500/30' : 'text-zinc-500'}`}>Takas</button>
              </>
            )}
            <button onClick={() => setTab('grafik')} className={`flex-1 py-1.5 px-3 text-[11px] font-bold rounded-lg transition-all whitespace-nowrap ${tab === 'grafik' ? 'bg-white/10 text-white' : 'text-zinc-500'}`}>Grafik</button>
          </div>

          {tab === 'derinlik' && (
            <DerinlikTab symbol={symbol} user={user} />
          )}

          {tab === 'akd' && akd && <Kurumsal akdData={akd} />}

          {tab === 'teknik' && (
            <div className="space-y-4">
              <div className="soft-card p-5">
                <h3 className="text-zinc-500 text-[11px] font-semibold uppercase tracking-wider mb-4">TradingView Önemli Göstergeler</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-black/40 p-3 rounded-xl border border-white/5 text-center">
                    <div className="text-[10px] text-zinc-500 font-bold uppercase mb-1">RSI (14)</div>
                    <div className={`text-lg font-black ${scan?.rsi_raw > 70 ? 'text-red-400' : scan?.rsi_raw < 30 ? 'text-[#00ff88]' : 'text-cyan-400'}`}>
                      {scan?.rsi || '---'}
                    </div>
                  </div>
                  <div className="bg-black/40 p-3 rounded-xl border border-white/5 text-center">
                    <div className="text-[10px] text-zinc-500 font-bold uppercase mb-1">MACD</div>
                    <div className="text-lg font-black text-white">{scan?.macd || '---'}</div>
                  </div>
                </div>

                {/* TV Technical Gauge Widget */}
                <div className="mt-6 bg-black/40 rounded-xl border border-white/5 overflow-hidden h-[280px]">
                  <iframe
                    src={`https://www.tradingview-widget.com/embed-widget/technical-analysis/?locale=tr&symbol=${stock?.exchange || 'BIST'}%3A${symbol}&interval=1D&width=100%25&height=100%25&isTransparent=true&theme=dark`}
                    style={{ width: '100%', height: '100%', border: 'none' }}
                  ></iframe>
                </div>
              </div>

              {history.length > 0 && (
                <div className="bg-[#111114] rounded-2xl p-3 border border-white/5 overflow-hidden">
                  <Chart
                    options={{
                      chart: { id: 'price-chart', toolbar: { show: false }, background: 'transparent' },
                      xaxis: { categories: history.map(h => h.date.split('-').slice(1).join('/')), labels: { style: { colors: '#71717a', fontSize: '10px' } }, axisBorder: { show: false } },
                      yaxis: { labels: { style: { colors: '#71717a', fontSize: '10px' } } },
                      grid: { borderColor: 'rgba(255,255,255,0.05)', strokeDashArray: 4 },
                      colors: ['#06b6d4'],
                      stroke: { curve: 'smooth', width: 3 },
                      fill: { type: 'gradient', gradient: { shadeIntensity: 1, opacityFrom: 0.4, opacityTo: 0, stops: [0, 90, 100] } },
                      tooltip: { theme: 'dark' },
                      theme: { mode: 'dark' }
                    }}
                    series={[{ name: 'Fiyat', data: history.map(h => h.price) }]}
                    type="area"
                    height={200}
                  />
                </div>
              )}

              <div className="premium-card p-5">
                <h3 className="text-zinc-500 text-[10px] font-black uppercase tracking-widest mb-4">Son KAP Bildirimleri</h3>
                <div className="space-y-4">
                  {scan?.kap_news?.map((news: any, i: number) => (
                    <div key={i} className="flex gap-3">
                      <div className="w-1.5 h-1.5 rounded-full bg-orange-500 mt-1.5 flex-shrink-0"></div>
                      <div>
                        <div className="text-[13px] font-bold text-zinc-200 leading-snug">{news.title}</div>
                        <div className="text-[10px] text-zinc-500 font-bold mt-1 uppercase tracking-tighter">{news.date} • KAP AJAN</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {tab === 'takas' && (
            <div className="bg-[#111114] border border-white/5 rounded-2xl overflow-hidden">
              <table className="w-full text-left text-[12px]">
                <thead className="bg-[#1a1a1d] text-zinc-400 uppercase font-bold text-[10px] tracking-wider border-b border-white/5">
                  <tr>
                    <th className="px-5 py-3 font-bold">KURUM</th>
                    <th className="px-5 py-3 text-right font-bold">TOPLAM LOT</th>
                    <th className="px-5 py-3 text-right font-bold">% PAY</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {takas?.holders?.map((h: any, i: number) => (
                    <tr key={i} className="hover:bg-white/[0.02]">
                      <td className="px-5 py-3.5 text-zinc-200 font-bold">{h.kurum}</td>
                      <td className="px-5 py-3.5 font-mono text-zinc-400 text-right">{h.toplam_lot}</td>
                      <td className="px-5 py-3.5 font-mono text-[#00ff88] text-right font-bold">{h.pay}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {tab === 'grafik' && (
            <div className="bg-[#111114] border border-white/5 rounded-2xl overflow-hidden aspect-[3/4] sm:aspect-square relative">
              <div className="absolute inset-0 flex items-center justify-center bg-[#0a0a0c]">
                <iframe
                  src={`https://www.tradingview-widget.com/embed-widget/advanced-chart/?locale=tr&symbol=${stock?.exchange === 'Hesaplanan' && symbol === 'GA' ? 'FX_IDC%3AXAUUSD' : `${stock?.exchange || 'BIST'}%3A${symbol}`
                    }&interval=D&timezone=Europe%2FIstanbul&theme=dark&style=1&withdateranges=true&hide_side_toolbar=false&allow_symbol_change=false&save_image=false&details=true&hotlist=true&calendar=true&hotlist=true&show_popup_button=true&popup_width=1000&popup_height=650`}
                  style={{ width: '100%', height: '100%', border: 'none' }}
                ></iframe>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

const SubViewDetail = ({ view, onBack, signals }: { view: string, onBack: () => void, signals?: any[] }) => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let category = '';
    if (view === 'Teknik Tarama') category = 'teknik';
    else if (view === 'AKD Tarama') category = 'akd';
    else if (view === 'KAP Ajan') category = 'kap';
    else if (view === 'Takas Tarama') category = 'takas';
    else if (view === 'Hisse Radar') category = 'radar';
    else if (view === 'Robot Gözü') {
      setData(signals);
      setLoading(false);
      return;
    }

    if (category) {
      setLoading(true);
      axios.get(`${API_BASE}/scan/${category}`)
        .then((res: any) => setData(res.data.results))
        .catch((err: any) => console.error(err))
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [view]);

  return (
    <div className="animate-fade-in pb-20">
      <div className="flex items-center gap-3 p-4 border-b border-white/5 sticky top-0 bg-black/80 backdrop-blur-md z-10">
        <button onClick={onBack} className="p-2 -ml-2 rounded-full hover:bg-white/10 active:bg-white/20 transition-colors">
          <ArrowLeft className="w-6 h-6 text-white" />
        </button>
        <span className="font-bold text-lg text-white">{view}</span>
      </div>

      <div className="p-4">
        {loading ? (
          <div className="flex flex-col items-center justify-center pt-20">
            <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin mb-4" />
            <div className="text-zinc-500 font-medium">Veriler güncelleniyor...</div>
          </div>
        ) : (
          <div className="space-y-4">
            {view === 'Hisse Radar' && (
              <div className="space-y-4">
                <div className="p-4 bg-[#111114] border border-white/5 rounded-2xl">
                  <h4 className="font-bold mb-4 flex items-center gap-2">
                    <Activity className="w-4 h-4 text-cyan-400" />
                    Radar - Günün Raporu (Analiz)
                  </h4>
                  <div className="space-y-4">
                    {data?.map((r: any, i: number) => (
                      <div key={i} className="flex justify-between items-center p-3 bg-white/[0.03] rounded-xl border border-white/5">
                        <div>
                          <div className="font-bold text-[14px] flex items-center gap-2">
                            {r.symbol} <span className="text-[10px] font-bold text-zinc-500">• {r.title}</span>
                          </div>
                          <div className="text-[11px] text-zinc-500 font-medium">{r.detay}</div>
                        </div>
                        <div className="text-[14px] font-black" style={{ color: r.color }}>{r.value}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {view === 'Teknik Tarama' && data?.map((item: any, i: number) => (
              <div key={i} className="bg-[#111114] border border-white/5 p-4 rounded-2xl flex justify-between items-center hover:bg-white/[0.02] transition-colors group">
                <div>
                  <div className="flex items-center gap-2">
                    <div className="font-bold text-white text-[17px]">{item.symbol}</div>
                    {item.volume === 'Yüksek' && (
                      <div className="bg-orange-500/10 text-orange-500 text-[9px] font-black px-1.5 py-0.5 rounded border border-orange-500/20 uppercase tracking-widest flex items-center gap-1">
                        <Zap className="w-2 h-2 fill-orange-500" /> HACİM
                      </div>
                    )}
                  </div>
                  <div className="text-[11px] font-bold mt-1" style={{ color: item.color }}>{item.status}</div>
                </div>
                <div className="text-right">
                  <div className="text-[16px] font-black text-white">{item.price} ₺</div>
                  <div className="text-[11px] text-zinc-500 mt-1 font-mono font-bold">RSI: {item.rsi}</div>
                </div>
              </div>
            ))}

            {(view === 'AKD Tarama' || view === 'Takas Tarama') && data?.map((item: any, i: number) => (
              <div key={i} className="bg-[#111114] border border-white/5 p-4 rounded-2xl flex justify-between items-center hover:bg-white/[0.02] transition-colors">
                <div className="flex items-center gap-3">
                  <div className="w-11 h-11 rounded-xl bg-white/5 flex items-center justify-center text-zinc-400 font-black border border-white/5 text-lg shadow-inner">{item.kurum.substring(0, 1)}</div>
                  <div>
                    <div className="font-bold text-white text-[15px]">{item.kurum}</div>
                    <div className="text-[10px] text-zinc-500 font-bold uppercase tracking-tight mt-0.5">{item.detay}</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-black text-[17px] tracking-tight" style={{ color: item.color }}>{item.net_hacim}</div>
                  <div className="text-[9px] font-black text-zinc-500 uppercase tracking-widest mt-0.5 flex items-center justify-end gap-1">
                    <span style={{ color: item.color }}>{item.yon}</span>
                  </div>
                </div>
              </div>
            ))}

            {view === 'KAP Ajan' && (
              <div className="space-y-3 pb-10">
                {data?.map((item: any, i: number) => (
                  <div key={i} className={`p-4 rounded-2xl border transition-all active:scale-[0.99] ${item.urgent ? 'bg-red-500/5 border-red-500/20 shadow-[0_0_20px_rgba(239,68,68,0.05)]' : 'bg-[#111114] border-white/5'}`}>
                    <div className="flex justify-between items-center mb-3">
                      <span className={`text-[9px] font-black px-2 py-0.5 rounded border tracking-widest ${item.urgent ? 'bg-red-500 border-red-400 text-white' : 'bg-zinc-800 border-zinc-700 text-zinc-400'}`}>{item.source}</span>
                      <span className="text-[11px] text-zinc-500 font-mono font-bold flex items-center gap-1">
                        <RefreshCw className="w-3 h-3 text-zinc-700" /> {item.time}
                      </span>
                    </div>
                    <div className={`text-[15px] font-bold leading-snug ${item.urgent ? 'text-white' : 'text-zinc-200'}`}>{item.title}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

// ======================== DERINLIK TAB (Real Data) ========================
const DerinlikTab = ({ symbol }: { symbol: string, user?: any }) => {
  const [derinlik, setDerinlik] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    axios.get(`${API_BASE}/derinlik-cache/${symbol}`)
      .then((res: any) => { setDerinlik(res.data); setLoading(false); })
      .catch(() => setLoading(false));
  }, [symbol]);

  if (loading) return <div className="flex items-center justify-center py-10"><RefreshCw className="w-6 h-6 text-cyan-400 animate-spin" /></div>;

  if (!derinlik || derinlik.error) {
    return (
      <div className="premium-card p-5 text-center">
        <Activity className="w-10 h-10 text-zinc-700 mx-auto mb-3" />
        <div className="text-zinc-500 text-sm font-medium">Derinlik verisi şu an mevcut değil.</div>
        <div className="text-zinc-600 text-xs mt-1">Matriks Bridge bağlantısı gereklidir.</div>
      </div>
    );
  }

  const bids = derinlik.bids || [];
  const asks = derinlik.asks || [];

  return (
    <div className="premium-card overflow-hidden">
      <div className="flex justify-between items-center px-4 py-3 border-b border-white/5">
        <span className="text-[11px] font-black text-zinc-500 uppercase tracking-wider">25 Kademe Derinlik</span>
        <span className="text-[10px] text-zinc-600">{derinlik.age_seconds ? `${derinlik.age_seconds}s önce` : 'Canlı'}</span>
      </div>
      <div className="grid grid-cols-2 divide-x divide-white/5">
        <div className="p-3">
          <p className="text-[11px] text-[#10b981] font-black mb-3 flex items-center gap-1"><ArrowDownRight className="w-3.5 h-3.5" /> ALIŞ <span className="text-zinc-600 font-normal ml-auto">Lot</span></p>
          {bids.slice(0, 10).map((b: any, i: number) => (
            <div key={i} className="flex justify-between items-center mb-2">
              <span className="text-[12px] font-mono font-medium text-[#10b981]">{b.price}</span>
              <span className="text-[12px] font-mono text-zinc-400">{b.volume?.toLocaleString('tr-TR')}</span>
            </div>
          ))}
        </div>
        <div className="p-3">
          <p className="text-[11px] text-[#ef4444] font-black mb-3 flex items-center gap-1 flex-row-reverse"><ArrowUpRight className="w-3.5 h-3.5" /> SATIŞ <span className="text-zinc-600 font-normal mr-auto">Lot</span></p>
          {asks.slice(0, 10).map((a: any, i: number) => (
            <div key={i} className="flex justify-between items-center mb-2 flex-row-reverse">
              <span className="text-[12px] font-mono font-medium text-[#ef4444]">{a.price}</span>
              <span className="text-[12px] font-mono text-zinc-400">{a.volume?.toLocaleString('tr-TR')}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// ======================== ALARM VIEW ========================
const AlarmView = ({ user, alarms, onRefresh }: { user: any, alarms: any[], onRefresh: () => void }) => {
  const [symbol, setSymbol] = useState('');
  const [price, setPrice] = useState('');
  const [adding, setAdding] = useState(false);

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!symbol || !price || !user?.id) return;
    setAdding(true);
    try {
      const stockRes = await axios.get(`${API_BASE}/stock/${symbol.toUpperCase()}`);
      const currentPrice = stockRes.data?.price || 0;
      const targetPrice = parseFloat(price.replace(',', '.'));
      const condition = targetPrice > currentPrice ? 'ABOVE' : 'BELOW';
      await axios.post(`${API_BASE}/alarms`, { userId: user.id, symbol: symbol.toUpperCase(), targetPrice, condition });
      setSymbol(''); setPrice('');
      onRefresh();
    } catch (err) { console.error(err); }
    setAdding(false);
  };

  const handleDelete = async (alarmId: number) => {
    try {
      await axios.delete(`${API_BASE}/alarms/${alarmId}`, { data: { userId: user?.id } });
      onRefresh();
    } catch (err) { console.error(err); }
  };

  return (
    <div className="animate-fade-in pb-20">
      <div className="flex items-center gap-3 p-4 border-b border-white/5">
        <Bell className="w-5 h-5 text-orange-400" />
        <span className="font-bold text-[17px]">Fiyat Alarmları</span>
      </div>

      <div className="p-4">
        <form onSubmit={handleAdd} className="soft-card p-4 mb-4">
          <h3 className="text-[11px] font-black text-zinc-500 uppercase tracking-widest mb-3">Yeni Alarm Kur</h3>
          <div className="flex gap-2 mb-2">
            <input
              type="text" placeholder="Sembol (THYAO)" value={symbol}
              onChange={e => setSymbol(e.target.value.toUpperCase())}
              className="flex-1 soft-card-inner py-2.5 px-3 text-[14px] focus:outline-none text-white font-mono font-bold uppercase"
            />
            <input
              type="text" placeholder="Fiyat (275.50)" value={price}
              onChange={e => setPrice(e.target.value)}
              className="flex-1 soft-card-inner py-2.5 px-3 text-[14px] focus:outline-none text-white font-mono"
            />
          </div>
          <button type="submit" disabled={adding || !symbol || !price}
            className="w-full py-2.5 rounded-xl bg-orange-500/20 text-orange-400 border border-orange-500/30 font-bold text-[13px] active:scale-[0.98] transition-all disabled:opacity-50"
          >{adding ? 'Kuruluyor...' : '🔔 Alarm Kur'}</button>
        </form>

        {alarms.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <Bell className="w-14 h-14 text-zinc-800 mb-4" strokeWidth={1} />
            <h3 className="text-[16px] font-bold">Aktif Alarmınız Yok</h3>
            <p className="text-zinc-500 text-[13px] mt-2">Yukarıdan hisse fiyat alarmı kurabilirsiniz.</p>
          </div>
        ) : (
          <div className="space-y-2">
            <div className="text-[11px] font-black text-zinc-500 uppercase tracking-widest mb-3">Aktif Alarmlar ({alarms.length})</div>
            {alarms.map((a: any) => (
              <div key={a.id} className="soft-card p-4 flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-black text-[15px]">{a.symbol}</span>
                    <span className={`text-[10px] font-black px-1.5 py-0.5 rounded border ${a.condition === 'ABOVE' ? 'bg-[#00ff88]/10 text-[#00ff88] border-[#00ff88]/20' : 'bg-[#ff3b30]/10 text-[#ff3b30] border-[#ff3b30]/20'}`}>
                      {a.condition === 'ABOVE' ? '▲ Üstüne' : '▼ Altına'}
                    </span>
                  </div>
                  <div className="text-[13px] font-mono text-zinc-300 mt-0.5">{a.target_price} ₺</div>
                </div>
                <button onClick={() => handleDelete(a.id)} className="w-8 h-8 rounded-full bg-red-500/10 text-red-400 flex items-center justify-center text-lg font-bold">×</button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default App;
