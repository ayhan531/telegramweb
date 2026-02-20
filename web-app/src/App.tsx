import React, { useEffect, useState } from 'react';
import WebApp from '@twa-dev/sdk';
import { Search, TrendingUp, BarChart2, Newspaper, PieChart } from 'lucide-react';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState('Anasayfa');

  useEffect(() => {
    WebApp.ready();
    WebApp.expand();
  }, []);

  const tabs = [
    { id: 'Anasayfa', icon: Search, label: 'Anasayfa' },
    { id: 'Kurumsal', icon: BarChart2, label: 'Kurumsal' },
    { id: 'Diger', icon: TrendingUp, label: 'Diğer' },
    { id: 'Bulten', icon: Newspaper, label: 'Bülten' },
    { id: 'Fon', icon: PieChart, label: 'Fon' },
  ];

  return (
    <div className="flex flex-col h-screen bg-black text-white overflow-hidden select-none">
      {/* Header */}
      <div className="p-4 flex items-center bg-zinc-900 border-b border-zinc-800">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500 w-4 h-4" />
          <input 
            type="text" 
            placeholder="Hisse ara..." 
            className="w-full bg-zinc-800 border-none rounded-lg py-2 pl-10 pr-4 text-sm focus:ring-1 focus:ring-cyan-500 outline-none"
          />
        </div>
        <div className="ml-3 w-8 h-8 bg-red-500 rounded-full flex items-center justify-center text-xs font-bold uppercase">
          {WebApp.initDataUnsafe.user?.first_name?.[0] || 'C'}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6 pb-24">
        <div className="space-y-1">
          <h1 className="text-lg font-semibold">İyi günler {WebApp.initDataUnsafe.user?.first_name || 'Cem'}! 👋</h1>
          <p className="text-xs text-zinc-500 italic">EMPAE halka arzı için talep toplanıyor — Bültene git</p>
        </div>

        {/* Empty State / Welcome */}
        <div className="flex flex-col items-center justify-center py-12 text-center space-y-4">
          <div className="w-16 h-16 bg-zinc-900 rounded-2xl flex items-center justify-center border border-zinc-800">
            <TrendingUp className="w-8 h-8 text-cyan-500" />
          </div>
          <div className="space-y-2">
            <h2 className="text-xl font-bold tracking-tight text-zinc-300">SERMAYE BORSASI</h2>
            <p className="text-sm text-zinc-500 max-w-[240px]">
              "Favoriler" Listesi Boş. Hisse ararken yıldız butonuna tıklayarak bu listeye hisse ekleyebilirsiniz.
            </p>
            <p className="text-xs text-amber-500 font-medium">Tüm listelerde toplamda 50 hisse eklenebilir.</p>
          </div>
        </div>

        {/* Example Market Summary */}
        <div className="bg-zinc-900 rounded-xl p-4 border border-zinc-800">
          <h3 className="text-xs font-bold text-zinc-500 uppercase mb-3 tracking-wider">Piyasa Özeti</h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <p className="text-[10px] text-zinc-400 font-medium uppercase">BIST 100</p>
              <p className="text-lg font-bold">9.245,60</p>
              <p className="text-xs text-emerald-500 font-semibold">+1,24%</p>
            </div>
            <div className="space-y-1">
              <p className="text-[10px] text-zinc-400 font-medium uppercase">USD/TRY</p>
              <p className="text-lg font-bold">31,12</p>
              <p className="text-xs text-red-500 font-semibold">-0,05%</p>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Navigation */}
      <div className="fixed bottom-0 left-0 right-0 bg-zinc-900 border-t border-zinc-800 px-2 pt-3 pb-8">
        <div className="flex justify-between items-center max-w-md mx-auto">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex flex-col items-center space-y-1 flex-1 transition-all duration-200 ${
                activeTab === tab.id ? 'text-cyan-500 scale-110' : 'text-zinc-500 hover:text-zinc-300'
              }`}
            >
              <tab.icon className={`w-5 h-5 ${activeTab === tab.id ? 'stroke-[2.5px]' : 'stroke-[2px]'}`} />
              <span className={`text-[9px] font-bold uppercase tracking-tighter ${activeTab === tab.id ? 'opacity-100' : 'opacity-80'}`}>{tab.label}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default App;
