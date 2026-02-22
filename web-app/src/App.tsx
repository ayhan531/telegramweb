import React, { useEffect, useState } from 'react';
import { Search, Building2, MoreHorizontal, FileText, Briefcase, Home, Edit2, Star, Activity, ArrowLeft, RefreshCw, ChevronDown, Bell, ArrowUpRight, ArrowDownRight, Copy } from 'lucide-react';
import axios from 'axios';

const API_BASE = '/api';

declare global {
  interface Window { Telegram: { WebApp: any; }; }
}

const App: React.FC = () => {
  const [currentView, setCurrentView] = useState('anasayfa');
  const [symbol, setSymbol] = useState('');
  const [akdData, setAkdData] = useState<any>(null); // Dummy data container for AKD page

  useEffect(() => {
    try {
      const WebApp = window.Telegram?.WebApp;
      if (WebApp) {
        WebApp.ready();
        WebApp.expand();
        WebApp.setHeaderColor('#000000');
        WebApp.setBackgroundColor('#000000');
      }
    } catch (err) {
      console.error(err);
    }

    // Pre-fetch some generic data for the AKD tab
    axios.get(`${API_BASE}/akd/THYAO`).then(res => setAkdData(res.data)).catch(console.error);
  }, []);

  const renderContent = () => {
    if (symbol) {
      return <SymbolDetail symbol={symbol} onBack={() => setSymbol('')} />;
    }

    switch (currentView) {
      case 'anasayfa': return <Anasayfa onSearch={(s: string) => setSymbol(s)} />;
      case 'kurumsal': return <Kurumsal akdData={akdData} />;
      case 'bulten': return <Bulten />;
      case 'fon': return <Fon />;
      case 'diger': return <Diger />;
      default: return <Anasayfa onSearch={(s: string) => setSymbol(s)} />;
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

const ViewTimerBadge = ({ time }: { time: string }) => (
  <div className="flex justify-center mt-3 mb-2">
    <div className="bg-[#002f1a] text-[#00ff88] px-4 py-1.5 rounded-full text-xs font-bold border border-[#00502a] flex items-center gap-2">
      <div className="w-2 h-2 rounded-full bg-[#00ff88] animate-pulse"></div> {time}
    </div>
  </div>
);

// 1. ANASAYFA
const Anasayfa = ({ onSearch }: { onSearch: (s: string) => void }) => {
  const [val, setVal] = useState('');
  return (
    <div className="animate-fade-in animate-duration-200">
      <div className="flex justify-center mt-4">
        <ViewTimerBadge time="29:38" />
      </div>

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
              className="w-full bg-[#111114] border border-white/10 rounded-xl py-3 pl-10 pr-4 text-[15px] focus:outline-none focus:border-white/20 text-white placeholder:text-zinc-600"
            />
          </div>
          <button type="button" className="w-[46px] h-[46px] flex-shrink-0 flex items-center justify-center bg-[#111114] rounded-xl border border-white/10">
            <Edit2 className="w-4 h-4 text-zinc-400" />
          </button>
          <div className="w-[46px] h-[46px] flex-shrink-0 rounded-full bg-gradient-to-br from-red-400 to-red-500 flex items-center justify-center text-white font-bold text-lg border border-red-500/50 shadow-inner">
            C
          </div>
        </form>

        <h2 className="text-[22px] font-bold mt-2 tracking-tight">Mutlu pazarlar Cem! ⛅</h2>
      </div>

      <div className="w-full h-[1px] bg-white/5 mt-2"></div>

      <div className="flex flex-col items-center justify-center pt-28 text-center px-6">
        <Star className="w-14 h-14 text-[#222226] mb-4" strokeWidth={1} />
        <h3 className="text-[17px] font-bold tracking-wide">"Favoriler" Listesi Boş</h3>
        <p className="text-zinc-500 text-[13px] mt-2 leading-relaxed max-w-[280px]">
          Hisse ararken yıldız butonuna tıklayarak bu listeye hisse ekleyebilirsiniz.
        </p>
        <p className="text-[#ff9d00] text-[13px] mt-1 font-medium">Tüm listelerde toplamda 50 hisse eklenebilir.</p>
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
      <ViewTimerBadge time="29:25" />

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
        {(tab === 'alanlar' ? akdData?.buyers : akdData?.sellers)?.map((b: any, i: number) => generateBrokerRow(b, i, tab === 'satanlar'))}

        {/* Mock Data if API is null for exact screenshot look */}
        {!akdData && (
          <>
            {generateBrokerRow({ kurum: 'Tera', lot: '3,2 Mr ₺' }, 0, tab === 'satanlar')}
            {generateBrokerRow({ kurum: 'BofA', lot: '1,9 Mr ₺' }, 1, tab === 'satanlar')}
            {generateBrokerRow({ kurum: 'Ak', lot: '1,1 Mr ₺' }, 2, tab === 'satanlar')}
            {generateBrokerRow({ kurum: 'İnfo', lot: '681,7 Mn ₺' }, 3, tab === 'satanlar')}
            {generateBrokerRow({ kurum: 'Alnus', lot: '391,2 Mn ₺' }, 4, tab === 'satanlar')}
          </>
        )}
      </div>
    </div>
  );
};

// 3. BULTEN
const Bulten = () => (
  <div className="animate-fade-in">
    <HeaderBar title="Veri Terminali" />
    <ViewTimerBadge time="29:16" />

    <div className="px-5 py-2">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-black text-[#ffb04f] tracking-tight">Bülten</h1>
        <div className="flex items-center gap-3 relative top-2">
          <span className="text-zinc-400 text-sm font-medium">22 Şubat Pazar</span>
          <span className="bg-[#002f1a] text-[#00ff88] text-[11px] font-black px-2.5 py-1 rounded border border-[#00502a] tracking-wider">POZİTİF</span>
          <button className="w-8 h-8 rounded-lg bg-[#111114] border border-white/10 flex items-center justify-center disabled:opacity-50">
            <Copy className="w-4 h-4 text-zinc-400" />
          </button>
        </div>
      </div>

      <div className="flex justify-between items-start mb-4">
        <h2 className="text-xl font-bold tracking-tight">BIST 100</h2>
        <div className="text-right">
          <div className="text-[22px] font-black leading-none">13934,06</div>
          <div className="text-[#00ff88] text-sm font-bold mt-1">+129,85 (+0.94%)</div>
        </div>
      </div>

      <p className="text-zinc-400 text-[15px] leading-relaxed mb-6 font-medium">
        BIST 100 endeksi, günü <span className="text-[#00ff88] font-bold">%0.94 yükselişle 13934,06</span> seviyesinden tamamladı. Gün içerisinde en düşük <span className="text-[#ff3b30] font-bold">13718,14</span>, en yüksek <span className="text-[#00ff88] font-bold">13934,06</span> puanları test edildi. Toplam işlem hacmi <span className="text-[#ffb04f] font-bold">171.4 Milyar TL</span> olarak gerçekleşti.
      </p>

      <p className="text-white text-base mb-6 font-medium">Merhaba <span className="font-bold">Cem</span>, iyi hafta sonları! 🎉</p>

      <div className="grid grid-cols-2">
        <div className="border border-white/5 rounded-l-xl bg-gradient-to-b from-[#00ff88]/[0.05] to-transparent">
          <div className="text-[#00ff88] text-center py-3 font-bold border-b border-white/5 text-[15px]">Endeksi Yükseltenler</div>
          <div className="flex flex-col">
            <div className="flex justify-between items-center px-4 py-3 border-b border-white/5"><span className="font-bold text-[14px]">DSTKF</span><span className="text-[#00ff88] font-bold text-sm">+31.9</span></div>
            <div className="flex justify-between items-center px-4 py-3 border-b border-white/5"><span className="font-bold text-[14px]">ASELS</span><span className="text-[#00ff88] font-bold text-sm">+24.8</span></div>
            <div className="flex justify-between items-center px-4 py-3 border-b border-white/5"><span className="font-bold text-[14px]">THYAO</span><span className="text-[#00ff88] font-bold text-sm">+18.5</span></div>
            <div className="flex justify-between items-center px-4 py-3 border-b border-white/5"><span className="font-bold text-[14px]">AKBNK</span><span className="text-[#00ff88] font-bold text-sm">+12.1</span></div>
            <div className="flex justify-between items-center px-4 py-3"><span className="font-bold text-[14px]">YKBNK</span><span className="text-[#00ff88] font-bold text-sm">+9.2</span></div>
          </div>
        </div>
        <div className="border border-white/5 border-l-0 rounded-r-xl bg-gradient-to-b from-[#ff3b30]/[0.05] to-transparent">
          <div className="text-[#ff3b30] text-center py-3 font-bold border-b border-white/5 text-[15px]">Endeksi Düşürenler</div>
          <div className="flex flex-col">
            <div className="flex justify-between items-center px-4 py-3 border-b border-white/5"><span className="font-bold text-[14px]">KLRHO</span><span className="text-[#ff3b30] font-bold text-sm">-37.9</span></div>
            <div className="flex justify-between items-center px-4 py-3 border-b border-white/5"><span className="font-bold text-[14px]">BIMAS</span><span className="text-[#ff3b30] font-bold text-sm">-7.9</span></div>
            <div className="flex justify-between items-center px-4 py-3 border-b border-white/5"><span className="font-bold text-[14px]">SASA</span><span className="text-[#ff3b30] font-bold text-sm">-5.8</span></div>
            <div className="flex justify-between items-center px-4 py-3 border-b border-white/5"><span className="font-bold text-[14px]">EKGYO</span><span className="text-[#ff3b30] font-bold text-sm">-4.7</span></div>
            <div className="flex justify-between items-center px-4 py-3"><span className="font-bold text-[14px]">CCOLA</span><span className="text-[#ff3b30] font-bold text-sm">-3.3</span></div>
          </div>
        </div>
      </div>
    </div>
  </div>
);

// 4. DIGER
const Diger = () => (
  <div className="animate-fade-in">
    <HeaderBar title="Veri Terminali" />
    <ViewTimerBadge time="28:39" />

    <div className="mt-8 mb-4 relative">
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="w-8 h-1 bg-white/10 rounded-full absolute -top-5"></div>
      </div>
      <h3 className="text-center font-bold text-lg">Diğer</h3>
    </div>

    <div className="px-4 space-y-2 pb-10">
      <DigerMenuItem icon={Search} title="Hisse Radar" subtitle="Hisse tarama ve filtreleme" color="text-cyan-400" bg="bg-cyan-400/10" />
      <DigerMenuItem icon={Activity} title="Teknik Tarama" subtitle="Teknik strateji taramaları" color="text-red-400" bg="bg-red-400/10" />
      <DigerMenuItem icon={Search} title="AKD Tarama" subtitle="Kurum alım/satım taraması" color="text-cyan-400" bg="bg-cyan-400/10" />
      <DigerMenuItem icon={Briefcase} title="Takas Tarama" subtitle="Takas verisi tarama araçları" color="text-indigo-400" bg="bg-indigo-400/10" />
      <DigerMenuItem icon={Bell} title="KAP Ajan" subtitle="KAP bildirim takip ajanı" color="text-orange-400" bg="bg-orange-400/10" />
    </div>
  </div>
);

const DigerMenuItem = ({ icon: Icon, title, subtitle, color, bg }: any) => (
  <div className="flex items-center gap-4 bg-[#0a0a0c] border border-white/5 p-4 rounded-2xl active:bg-white/5 transition-colors">
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
const Fon = () => (
  <div className="animate-fade-in">
    <HeaderBar title="Veri Terminali" />
    <ViewTimerBadge time="29:08" />

    <div className="px-4 mt-2">
      <div className="relative mb-6">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500 w-4 h-4" />
        <input type="text" placeholder="Fon ara..." className="w-full bg-[#111114] border border-white/10 rounded-xl py-3 pl-10 pr-4 text-[15px] focus:outline-none focus:border-white/20 text-white placeholder:text-zinc-600" />
      </div>

      <div className="bg-[#0a0a0c] border border-white/5 rounded-2xl overflow-hidden mb-6">
        <h3 className="text-[17px] font-bold text-white p-4 pb-2">Bizim Seçtiklerimiz</h3>

        <div className="flex px-4 py-2 gap-2 overflow-x-auto hide-scrollbar">
          <button className="whitespace-nowrap px-4 py-1.5 rounded-full border border-white text-white font-medium text-sm bg-white/10">BIST100</button>
          <button className="whitespace-nowrap px-4 py-1.5 rounded-full border border-white/10 text-zinc-400 font-medium text-sm">Yabancı Hisse</button>
          <button className="whitespace-nowrap px-4 py-1.5 rounded-full border border-white/10 text-zinc-400 font-medium text-sm">Altın</button>
          <button className="whitespace-nowrap px-4 py-1.5 rounded-full border border-white/10 text-zinc-400 font-medium text-sm">Gümüş</button>
        </div>

        <table className="w-full mt-2">
          <thead>
            <tr className="text-zinc-500 text-[10px] uppercase font-bold text-left border-b border-white/5">
              <th className="pl-4 py-3 font-bold tracking-wider">FON</th>
              <th className="py-3 font-bold tracking-wider">FON ADI</th>
              <th className="pr-4 py-3 text-right font-bold tracking-wider">AYLIK DEĞİŞİM</th>
            </tr>
          </thead>
          <tbody>
            <FonRow code="KHA" name="PARDUS PORTFÖY İKİN..." val="+10,33%" color="bg-indigo-600" icon="P" />
            <FonRow code="GAF" name="INVEO PORTFÖY BİRİN..." val="+9,78%" color="bg-blue-600" icon="INVEO" />
            <FonRow code="AHI" name="ATLAS PORTFÖY BİRİN..." val="+7,97%" color="bg-cyan-600" icon="A" />
            <FonRow code="RHS" name="ROTA PORTFÖY HİSSE ..." val="+7,40%" color="bg-purple-600" icon="*" />
            <FonRow code="GMR" name="INVEO PORTFÖY İKİNC..." val="+2,17%" color="bg-blue-600" icon="INVEO" />
          </tbody>
        </table>
      </div>
    </div>
  </div>
);

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
const SymbolDetail = ({ symbol, onBack }: { symbol: string, onBack: () => void }) => {
  const [stock, setStock] = useState<any>(null);
  const [akd, setAkd] = useState<any>(null);
  const [takas, setTakas] = useState<any>(null);
  const [tab, setTab] = useState('derinlik');

  useEffect(() => {
    axios.get(`${API_BASE}/stock/${symbol}`).then(res => setStock(res.data)).catch(console.error);
    axios.get(`${API_BASE}/akd/${symbol}`).then(res => setAkd(res.data)).catch(console.error);
    axios.get(`${API_BASE}/takas/${symbol}`).then(res => setTakas(res.data)).catch(console.error);
  }, [symbol]);

  return (
    <div className="animate-fade-in bg-black min-h-screen">
      <div className="flex items-center gap-3 p-4 border-b border-white/5 sticky top-0 bg-black/80 backdrop-blur-md z-10">
        <button onClick={onBack} className="p-2 -ml-2 rounded-full hover:bg-white/10 active:bg-white/20 transition-colors">
          <ArrowLeft className="w-6 h-6 text-white" />
        </button>
        <span className="font-bold text-lg text-white">{symbol.toUpperCase()} Detay</span>
      </div>

      <div className="p-4 space-y-4 pb-20">
        {stock && (
          <div className="bg-[#111114] rounded-2xl p-5 border border-white/5">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h1 className="text-3xl font-black tracking-tight text-white">{symbol.toUpperCase()}</h1>
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

        <div className="flex bg-[#111114] rounded-xl p-1.5 border border-white/5 justify-between">
          <button onClick={() => setTab('derinlik')} className={`flex-1 py-2 text-xs font-bold rounded-lg transition-all ${tab === 'derinlik' ? 'bg-[#2a2a2d] text-white shadow-lg' : 'text-zinc-500'}`}>Derinlik</button>
          <button onClick={() => setTab('akd')} className={`flex-1 py-2 text-xs font-bold rounded-lg transition-all ${tab === 'akd' ? 'bg-[#2a2a2d] text-white shadow-lg' : 'text-zinc-500'}`}>AKD</button>
          <button onClick={() => setTab('takas')} className={`flex-1 py-2 text-xs font-bold rounded-lg transition-all ${tab === 'takas' ? 'bg-[#2a2a2d] text-white shadow-lg' : 'text-zinc-500'}`}>Takas</button>
          <button onClick={() => setTab('grafik')} className={`flex-1 py-2 text-xs font-bold rounded-lg transition-all ${tab === 'grafik' ? 'bg-[#2a2a2d] text-white shadow-lg' : 'text-zinc-500'}`}>Grafik</button>
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
                src={`https://s.tradingview.com/widgetembed/?frameElementId=tw&symbol=BIST%3A${symbol}&interval=D&hidesidetoolbar=1&symboledit=1&saveimage=1&toolbarbg=1a1a1d&theme=dark`}
                style={{ width: '100%', height: '100%', border: 'none' }}
              ></iframe>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default App;
