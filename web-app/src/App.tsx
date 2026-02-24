import React, { useEffect, useState } from 'react';
import { Search, Building2, MoreHorizontal, FileText, Briefcase, Home, Edit2, Star, Activity, ArrowLeft, RefreshCw, ChevronDown, Bell, ArrowUpRight, ArrowDownRight, Copy, Zap } from 'lucide-react';
import axios from 'axios';
import Chart from 'react-apexcharts';

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
  const [bultenLoading, setBultenLoading] = useState(false);
  const [fonLoading, setFonLoading] = useState(false);

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

      axios.get(`${API_BASE}/akd/THYAO`).then(res => setAkdData(res.data)).catch(console.error);
      axios.get(`${API_BASE}/bulten`).then(res => setBultenData(res.data)).catch(console.error).finally(() => setBultenLoading(false));
      axios.get(`${API_BASE}/fon`).then(res => setFonData(res.data)).catch(console.error).finally(() => setFonLoading(false));
    };

    setBultenLoading(true);
    setFonLoading(true);
    fetchGlobalData();

    const interval = setInterval(fetchGlobalData, 30000); // 30 saniyede bir ana verileri yenile
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (user?.id) {
      axios.get(`${API_BASE}/favorites/${user.id}`).then(res => setFavorites(res.data)).catch(console.error);
    }
  }, [user]);

  const toggleFavorite = async (s: string) => {
    if (!user?.id) return;
    const isFav = favorites.includes(s.toUpperCase());
    try {
      if (isFav) {
        await axios.delete(`${API_BASE}/favorites`, { data: { userId: user.id, symbol: s } });
        setFavorites(prev => prev.filter(f => f !== s.toUpperCase()));
      } else {
        await axios.post(`${API_BASE}/favorites`, { userId: user.id, symbol: s });
        setFavorites(prev => [...prev, s.toUpperCase()]);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const renderContent = () => {
    if (symbol) {
      return <SymbolDetail symbol={symbol} favorites={favorites} onToggleFavorite={toggleFavorite} onBack={() => setSymbol('')} />;
    }

    switch (currentView) {
      case 'anasayfa': return <Anasayfa user={user} favorites={favorites} onSearch={(s: string) => setSymbol(s)} onToggleFavorite={toggleFavorite} />;
      case 'kurumsal': return <Kurumsal akdData={akdData} />;
      case 'bulten': return bultenLoading ? <LoadingView label="Bülten hazırlanıyor..." /> : <Bulten data={bultenData} user={user} />;
      case 'fon': return fonLoading ? <LoadingView label="Fonlar listeleniyor..." /> : <Fon data={fonData} />;
      case 'diger': return <Diger bultenData={bultenData} />;
      default: return <Anasayfa user={user} favorites={favorites} onSearch={(s: string) => setSymbol(s)} onToggleFavorite={toggleFavorite} />;
    }
  };

  return (
    <div className="flex flex-col h-screen bg-black text-white font-sans overflow-hidden">
      <div className="flex-1 overflow-y-auto pb-28">
        {renderContent()}
      </div>

      {!symbol && (
        <footer className="fixed bottom-4 left-4 right-4 bg-[#0a0a0c] border border-white/10 rounded-[28px] p-2 flex justify-between items-center z-50">
          <NavButton id="anasayfa" icon={Home} label="Anasayfa" active={currentView === 'anasayfa'} onClick={setCurrentView} />
          <NavButton id="kurumsal" icon={Building2} label="Kurumsal" active={currentView === 'kurumsal'} onClick={setCurrentView} />
          <NavButton id="diger" icon={MoreHorizontal} label="Diğer" active={currentView === 'diger'} onClick={setCurrentView} />
          <NavButton id="bulten" icon={FileText} label="Bülten" active={currentView === 'bulten'} onClick={setCurrentView} />
          <NavButton id="fon" icon={Briefcase} label="Fon" active={currentView === 'fon'} onClick={setCurrentView} />
        </footer>
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
const NavButton = ({ id, icon: Icon, label, active, onClick }: any) => (
  <button onClick={() => onClick(id)} className="flex flex-col items-center flex-1 py-1">
    <div className={`p-2.5 rounded-[14px] mb-1 transition-all ${active ? 'bg-[#222226] text-white' : 'text-zinc-500'}`}>
      <Icon className={`w-5 h-5 ${active ? 'stroke-[2.5px]' : 'stroke-2'}`} />
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

const Anasayfa = ({ user, favorites, onSearch, onToggleFavorite }: { user: any, favorites: string[], onSearch: (s: string) => void, onToggleFavorite: (s: string) => void }) => {
  const [marketTab, setMarketTab] = useState('BIST');
  const [val, setVal] = useState('');

  const handleSearchKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && val.trim()) {
      onSearch(val.trim().toUpperCase());
    }
  };

  const filteredFavorites = favorites.filter(f => f.includes(val.toUpperCase()));

  return (
    <div className="animate-fade-in animate-duration-200">
      <div className="p-4">
        {/* Search Header */}
        <form onSubmit={(e) => { e.preventDefault(); if (val) onSearch(val); }} className="flex gap-3 mb-6">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500 w-4 h-4" />
            <input
              type="text"
              placeholder="Hisse ara..."
              value={val}
              onChange={e => setVal(e.target.value)}
              onKeyDown={handleSearchKeyPress}
              className="w-full bg-[#111114] border border-white/10 rounded-xl py-3 pl-10 pr-4 text-[15px] focus:outline-none focus:border-white/20 text-white placeholder:text-zinc-600"
            />
          </div>
          <button type="button" className="w-[46px] h-[46px] flex-shrink-0 flex items-center justify-center bg-[#111114] rounded-xl border border-white/10">
            <Edit2 className="w-4 h-4 text-zinc-400" />
          </button>
          <div className="w-[46px] h-[46px] flex-shrink-0 rounded-full bg-gradient-to-br from-red-400 to-red-500 flex items-center justify-center text-white font-bold text-lg border border-red-500/50 shadow-inner">
            {user?.first_name ? user.first_name.charAt(0).toUpperCase() : 'B'}
          </div>
        </form>

        <h2 className="text-[22px] font-bold mt-2 tracking-tight">
          {user?.first_name ? `Hoş geldin ${user.first_name}!` : 'Hoş geldiniz!'} {new Date().getDay() === 0 ? '☁️' : '🚀'}
        </h2>
      </div>

      <div className="w-full h-[1px] bg-white/5 mt-2"></div>

      {/* Market Tabs */}
      <div className="flex px-4 mt-6 gap-2">
        {['BIST', 'KRİPTO', 'EMTİA'].map(t => (
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
          <div className="flex flex-col items-center justify-center pt-20 text-center px-6">
            <Star className="w-14 h-14 text-[#222226] mb-4" strokeWidth={1} />
            <h3 className="text-[17px] font-bold tracking-wide">{val ? 'Sonuç Bulunamadı' : '"Favoriler" Listesi Boş'}</h3>
            <p className="text-zinc-500 text-[13px] mt-2 leading-relaxed max-w-[280px]">
              {val ? 'Aradığınız kritere uygun favori hisse bulunamadı.' : 'Hisse ararken yıldız butonuna tıklayarak bu listeye hisse ekleyebilirsiniz.'}
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-3">
            {filteredFavorites.map((fav) => (
              <FavoriteCard key={fav} symbol={fav} onSelect={onSearch} onRemove={() => onToggleFavorite(fav)} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

const FavoriteCard = ({ symbol, onSelect, onRemove }: any) => {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    const fetchData = () => {
      axios.get(`${API_BASE}/stock/${symbol}`).then(res => setData(res.data)).catch(console.error);
    };

    fetchData();
    const interval = setInterval(fetchData, 15000); // 15 saniyede bir güncelle
    return () => clearInterval(interval);
  }, [symbol]);

  return (
    <div onClick={() => onSelect(symbol)} className="bg-[#111114] border border-white/10 rounded-2xl p-4 active:scale-[0.98] transition-all relative group">
      <div className="flex justify-between items-start mb-2">
        <span className="font-bold text-[15px]">{symbol}</span>
        <button onClick={(e) => { e.stopPropagation(); onRemove(); }} className="text-[#ff9d00]">
          <Star className="w-4 h-4 fill-[#ff9d00]" />
        </button>
      </div>
      <div className="flex justify-between items-end">
        <div className="text-[18px] font-bold">{data?.price || '---'}</div>
        <div className={`text-[11px] font-bold ${data?.change >= 0 ? 'text-[#00ff88]' : 'text-[#ff3b30]'}`}>
          {data?.change >= 0 ? '+' : ''}{data?.change?.toFixed(2)}%
        </div>
      </div>
    </div>
  );
};

// 2. KURUMSAL (AKD Equivalent)
const Kurumsal = ({ akdData }: { akdData: any }) => {
  const [tab, setTab] = useState('alanlar');

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
              %{(40 - index * 5).toFixed(2)}
            </span>
            <ChevronDown className="w-3 h-3 text-zinc-600 -rotate-90 ml-1" />
          </div>
          <div className="text-[11px] text-zinc-500 mt-1">{(80 - index * 10).toFixed(1)} Mr ₺</div>
        </div>
      </div>
    );
  };

  return (
    <div className="animate-fade-in">
      <HeaderBar title="Veri Terminali" />

      {/* Selectors */}
      <div className="flex gap-2 p-4">
        <div className="relative flex-[1.2]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500 w-4 h-4" />
          <input type="text" placeholder="Kurum ara..." className="w-full bg-[#111114] border border-white/5 rounded-xl py-2.5 pl-9 pr-2 text-[13px] focus:outline-none text-white" />
        </div>
        <div className="relative flex-1 bg-[#111114] border border-white/5 rounded-xl flex items-center px-3">
          <span className="text-[13px] font-medium text-white">20 Şubat</span>
          <ChevronDown className="w-4 h-4 ml-auto text-zinc-500" />
        </div>
        <div className="relative flex-[0.9] bg-[#111114] border border-white/5 rounded-xl flex items-center px-3">
          <span className="text-[13px] font-medium text-white">Saat Seç</span>
          <ChevronDown className="w-4 h-4 ml-auto text-zinc-500" />
        </div>
        <button className="w-10 flex-shrink-0 bg-[#111114] border border-white/5 rounded-xl flex items-center justify-center">
          <RefreshCw className="w-4 h-4 text-zinc-400" />
        </button>
      </div>

      {/* Header Tabs */}
      <div className="flex px-4 mt-2">
        <button onClick={() => setTab('alanlar')} className={`flex-1 pb-3 text-[14px] font-bold border-b-2 transition-colors ${tab === 'alanlar' ? 'border-[#00ff88] text-[#00ff88] bg-[#00ff88]/[0.05] rounded-t-xl pt-2' : 'border-white/5 text-zinc-500 pt-2'}`}>
          Alanlar
        </button>
        <button onClick={() => setTab('satanlar')} className={`flex-1 pb-3 text-[14px] font-bold border-b-2 transition-colors ${tab === 'satanlar' ? 'border-[#ff3b30] text-[#ff3b30] bg-[#ff3b30]/[0.05] rounded-t-xl pt-2' : 'border-white/5 text-zinc-500 pt-2'}`}>
          Satanlar
        </button>
        <button onClick={() => setTab('toplam')} className={`flex-1 pb-3 text-[14px] font-bold border-b-2 transition-colors ${tab === 'toplam' ? 'border-white text-white bg-white/[0.05] rounded-t-xl pt-2' : 'border-white/5 text-zinc-500 pt-2'}`}>
          Toplam
        </button>
      </div>

      <div className="px-4 py-2 mt-1 pb-10">
        {(!akdData || akdData.error) ? (
          <div className="flex flex-col items-center justify-center pt-20 text-center px-6">
            <Activity className="w-12 h-12 text-zinc-800 mb-4" />
            <div className="text-zinc-500 font-medium">Bu sembol için AKD verisi şu an mevcut değil.</div>
          </div>
        ) : (
          tab === 'toplam' ? (
            akdData?.total?.map((t: any, i: number) => (
              <div key={i} className="flex justify-between items-center py-3 border-b border-white/5 last:border-0 px-1">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-[#111114] flex items-center justify-center border border-white/5 text-[10px] font-bold text-zinc-400">{t.kurum.substring(0, 2)}</div>
                  <span className="font-bold text-zinc-200">{t.kurum}</span>
                </div>
                <div className="text-right">
                  <div className="font-mono font-bold text-[#00ff88]" style={{ color: t.color }}>{t.lot}</div>
                  <div className="text-[10px] text-zinc-500 uppercase font-bold">{t.type}</div>
                </div>
              </div>
            ))
          ) : (
            (tab === 'alanlar' ? akdData?.buyers : akdData?.sellers)?.map((b: any, i: number) => generateBrokerRow(b, i, tab === 'satanlar'))
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
        Merhaba <span className="font-extrabold text-[#00ff88]">{user?.first_name || 'Cem'}</span>, iyi hafta sonları! 🎉
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

const MarketSection = ({ title, data, color }: any) => (
  <div className="border border-white/5 rounded-xl bg-gradient-to-b from-white/[0.02] to-transparent overflow-hidden">
    <div className="px-4 py-3 font-bold border-b border-white/5 text-[15px]" style={{ color }}>{title}</div>
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
const Diger = ({ bultenData }: { bultenData: any }) => {
  const [selectedSubView, setSelectedSubView] = useState<string | null>(null);

  const handleMenuItemClick = (view: string) => {
    setSelectedSubView(view);
  };

  const handleBack = () => {
    setSelectedSubView(null);
  };

  if (selectedSubView) {
    return <SubViewDetail view={selectedSubView} onBack={handleBack} bultenData={bultenData} />;
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
        <DigerMenuItem icon={Search} title="Hisse Radar" subtitle="Hisse tarama ve filtreleme" color="text-cyan-400" bg="bg-cyan-400/10" onClick={() => handleMenuItemClick('Hisse Radar')} />
        <DigerMenuItem icon={Activity} title="Teknik Tarama" subtitle="Teknik strateji taramaları" color="text-red-400" bg="bg-red-400/10" onClick={() => handleMenuItemClick('Teknik Tarama')} />
        <DigerMenuItem icon={Search} title="AKD Tarama" subtitle="Kurum alım/satım taraması" color="text-cyan-400" bg="bg-cyan-400/10" onClick={() => handleMenuItemClick('AKD Tarama')} />
        <DigerMenuItem icon={Briefcase} title="Takas Tarama" subtitle="Takas verisi tarama araçları" color="text-indigo-400" bg="bg-indigo-400/10" onClick={() => handleMenuItemClick('Takas Tarama')} />
        <DigerMenuItem icon={Bell} title="KAP Ajan" subtitle="KAP bildirim takip ajanı" color="text-orange-400" bg="bg-orange-400/10" onClick={() => handleMenuItemClick('KAP Ajan')} />
      </div>
    </div>
  );
};

const DigerMenuItem = ({ icon: Icon, title, subtitle, color, bg, onClick }: any) => (
  <div className="flex items-center gap-4 bg-[#0a0a0c] border border-white/5 p-4 rounded-2xl active:bg-white/5 transition-colors" onClick={onClick}>
    <div className={`w-12 h-12 rounded-2xl ${bg} flex items-center justify-center`}>
      <Icon className={`w-6 h-6 ${color}`} />
    </div>
    <div className="flex-1">
      <div className="font-bold text-[16px] text-white">{title}</div>
      <div className="text-sm text-zinc-500 mt-0.5">{subtitle}</div>
    </div>
    <ChevronDown className="w-5 h-5 text-zinc-600 -rotate-90" />
  </div>
);

// 5. FON
const Fon = ({ data }: { data: any }) => {
  const [val, setVal] = useState('');

  const handleSearchKeyPress = (e: React.KeyboardEvent) => {
    // Fon araması sadece filtreleme yaptığı için özel bir aksiyon gerekmez, 
    // ama Enter'a basıldığında klavyeyi kapatmak yararlı olabilir.
    if (e.key === 'Enter') (e.target as HTMLInputElement).blur();
  };

  const filteredFunds = data?.funds?.filter((f: any) =>
    f.code.toUpperCase().includes(val.toUpperCase()) ||
    f.name.toUpperCase().includes(val.toUpperCase())
  ) || [];

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
            <button className="whitespace-nowrap px-4 py-1.5 rounded-full border border-white text-white font-medium text-sm bg-white/10">Tümü</button>
            <button className="whitespace-nowrap px-4 py-1.5 rounded-full border border-white/10 text-zinc-400 font-medium text-sm">Hisse Senedi</button>
            <button className="whitespace-nowrap px-4 py-1.5 rounded-full border border-white/10 text-zinc-400 font-medium text-sm">Altın</button>
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
const SymbolDetail = ({ symbol, favorites, onToggleFavorite, onBack }: { symbol: string, favorites: string[], onToggleFavorite: (s: string) => void, onBack: () => void }) => {
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
            <div className="bg-[#111114] rounded-2xl p-5 border border-white/5">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <div className="flex items-center gap-2">
                    <h1 className="text-3xl font-black tracking-tight text-white">{symbol.toUpperCase()}</h1>
                    <button onClick={() => onToggleFavorite(symbol)}>
                      <Star className={`w-6 h-6 ${favorites.includes(symbol.toUpperCase()) ? 'fill-[#ff9d00] text-[#ff9d00]' : 'text-zinc-600'}`} />
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
            <div className="bg-[#111114] rounded-2xl border border-white/5 overflow-hidden">
              <div className="grid grid-cols-2 divide-x divide-white/5">
                <div className="p-4">
                  <p className="text-[11px] text-[#00ff88] font-black mb-3 flex items-center gap-1">🟢 ALIŞ <span className="text-zinc-600 font-normal ml-auto">Lot</span></p>
                  {[...Array(5)].map((_, i) => (
                    <div key={i} className="flex justify-between items-center mb-2.5">
                      <span className="text-[13px] font-mono font-medium text-zinc-100">{(285.5 - i * 0.05).toFixed(2)}</span>
                      <span className="text-[13px] font-mono text-zinc-500">{(Math.random() * 50000).toFixed(0)}</span>
                    </div>
                  ))}
                </div>
                <div className="p-4">
                  <p className="text-[11px] text-[#ff3b30] font-black mb-3 flex items-center gap-1 flex-row-reverse">🔴 SATIŞ <span className="text-zinc-600 font-normal mr-auto">Lot</span></p>
                  {[...Array(5)].map((_, i) => (
                    <div key={i} className="flex justify-between items-center mb-2.5 flex-row-reverse">
                      <span className="text-[13px] font-mono font-medium text-zinc-100">{(285.55 + i * 0.05).toFixed(2)}</span>
                      <span className="text-[13px] font-mono text-zinc-500">{(Math.random() * 50000).toFixed(0)}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {tab === 'akd' && akd && <Kurumsal akdData={akd} />}

          {tab === 'teknik' && (
            <div className="space-y-4">
              <div className="bg-[#111114] rounded-2xl p-5 border border-white/5">
                <h3 className="text-zinc-400 text-[10px] font-black uppercase tracking-widest mb-4">Teknik Göstergeler (Real-time)</h3>
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
                  <div className="col-span-2 bg-black/40 p-3 rounded-xl border border-white/5 flex justify-between items-center">
                    <div className="text-[10px] text-zinc-500 font-bold uppercase">Hareketli Ortalamalar</div>
                    <div className="bg-cyan-500/10 text-cyan-400 text-[11px] font-black px-3 py-1 rounded-full border border-cyan-500/20">{scan?.moving_averages || 'Güçlü Al'}</div>
                  </div>
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

              <div className="bg-[#111114] rounded-2xl p-5 border border-white/5">
                <h3 className="text-zinc-400 text-[10px] font-black uppercase tracking-widest mb-4">Son KAP Bildirimleri</h3>
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
            <div className="bg-[#111114] border border-white/5 rounded-2xl overflow-hidden aspect-square relative">
              <div className="absolute inset-0 flex items-center justify-center bg-[#0a0a0c]">
                <iframe
                  src={`https://s.tradingview.com/widgetembed/?frameElementId=tw&symbol=${stock?.exchange === 'Hesaplanan' && symbol === 'GA' ? 'FX_IDC%3AXAUUSD' : `${stock?.exchange || 'BIST'}%3A${symbol}`
                    }&interval=D&hidesidetoolbar=1&symboledit=1&saveimage=1&toolbarbg=1a1a1d&theme=dark`}
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

// ======================== SUB VIEW DETAIL ========================
const SubViewDetail = ({ view, onBack, bultenData }: { view: string, onBack: () => void, bultenData: any }) => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let category = '';
    if (view === 'Teknik Tarama') category = 'teknik';
    else if (view === 'AKD Tarama') category = 'akd';
    else if (view === 'KAP Ajan') category = 'kap';
    else if (view === 'Takas Tarama') category = 'takas';

    if (category) {
      setLoading(true);
      axios.get(`${API_BASE}/scan/${category}`)
        .then(res => setData(res.data.results))
        .catch(err => console.error(err))
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
                    Popüler Taramalar (Canlı)
                  </h4>
                  <div className="space-y-6">
                    <div>
                      <div className="text-[12px] font-bold text-zinc-500 mb-3 uppercase tracking-wider">Günün Yıldızları</div>
                      <div className="grid grid-cols-1 gap-2">
                        {bultenData?.gainers?.slice(0, 3).map((g: any, i: number) => (
                          <div key={i} className="flex justify-between items-center p-3 bg-white/[0.03] rounded-xl border border-white/5">
                            <span className="font-bold">{g.symbol}</span>
                            <span className="text-[#00ff88] font-bold">{g.change}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                    <div>
                      <div className="text-[12px] font-bold text-zinc-500 mb-3 uppercase tracking-wider">Hacim Artışı</div>
                      <div className="grid grid-cols-1 gap-2">
                        {bultenData?.bist_summary?.slice(0, 3).map((s: any, i: number) => (
                          <div key={i} className="flex justify-between items-center p-3 bg-white/[0.03] rounded-xl border border-white/5">
                            <span className="font-bold">{s.symbol}</span>
                            <span className="text-zinc-400 text-xs">{s.price} ₺</span>
                          </div>
                        ))}
                      </div>
                    </div>
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

export default App;
