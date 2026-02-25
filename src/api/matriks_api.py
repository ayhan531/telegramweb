"""
Matriks Data API Wrapper
========================
Matriks Data (matriksdata.com) için REST API entegrasyon modülü.

Kurulum:
    .env dosyasına ekleyin:
        MATRIKS_API_KEY=your_api_key_here
        MATRIKS_API_URL=https://api.matriksdata.com/v1  (veya size verilen URL)

API Key Alma:
    👉 https://matriksdata.com/urunler/veri-servisleri
    - "API Teklifi Al" formunu doldurun
    - Ücretli servis: AKD, Takas, Level-2 derinlik, VIOP için gerekli
    - Ücretsiz test API'si için iletişim: info@matriksdata.com

Desteklenen Veriler (API key ile):
    - Gerçek zamanlı BIST fiyatları (tick-by-tick)
    - Level-2 Emir Defteri (5-10 kademe derinlik)
    - Kurumsal Takas/AKD (günlük EOD)
    - VIOP Vadeli Kontratlar
    - Hisse Derinlik analizi
"""

import os
import json
import requests
import urllib3
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class MatriksAPI:
    """
    Matriks Data REST API için wrapper sınıfı.
    API key .env'den otomatik yüklenir.
    """
    
    def __init__(self):
        self.api_key = os.getenv("MATRIKS_API_KEY", "")
        self.base_url = os.getenv("MATRIKS_API_URL", "https://api.matriksdata.com/v1")
        self.session = requests.Session()
        
        if self.api_key:
            self.session.headers.update({
                "Authorization": f"Bearer {self.api_key}",
                "X-API-Key": self.api_key,
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "DerinlikBot/1.0"
            })
    
    def is_configured(self):
        """API key yapılandırılmış mı?"""
        return bool(self.api_key and self.api_key != "your_api_key_here")
    
    def _get(self, endpoint, params=None):
        """Generic GET request."""
        if not self.is_configured():
            return {"error": "MATRIKS_API_KEY yapılandırılmamış. .env dosyasına ekleyin."}
        
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            resp = self.session.get(url, params=params, timeout=10, verify=False)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError as e:
            return {"error": f"HTTP {e.response.status_code}: {str(e)}"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_quote(self, symbol):
        """
        Anlık fiyat verisi.
        Endpoint: GET /quotes/{symbol}
        """
        data = self._get(f"/quotes/{symbol.upper()}")
        if "error" in data:
            return data
        
        return {
            "symbol": symbol.upper(),
            "price": data.get("lastPrice") or data.get("price"),
            "change": data.get("change") or data.get("changePercent"),
            "high": data.get("high"),
            "low": data.get("low"),
            "open": data.get("open"),
            "volume": data.get("volume"),
            "source": "Matriks Data (Anlık)"
        }
    
    def get_orderbook(self, symbol, levels=5):
        """
        Emir defteri / piyasa derinliği.
        Endpoint: GET /orderbook/{symbol}
        """
        data = self._get(f"/orderbook/{symbol.upper()}", params={"levels": levels})
        if "error" in data:
            return data
        
        return {
            "symbol": symbol.upper(),
            "bids": data.get("bids", []),   # Alış emirleri
            "asks": data.get("asks", []),    # Satış emirleri
            "timestamp": data.get("timestamp"),
            "source": "Matriks Data Level-2"
        }
    
    def get_akd(self, symbol, date=None):
        """
        Aracı Kurum Dağılımı (AKD).
        Endpoint: GET /akd/{symbol}
        """
        params = {}
        if date:
            params["date"] = date
        
        data = self._get(f"/akd/{symbol.upper()}", params=params)
        if "error" in data:
            return data
        
        return {
            "symbol": symbol.upper(),
            "date": data.get("date", datetime.now().strftime("%d/%m/%Y")),
            "buyers": data.get("buyers", []),
            "sellers": data.get("sellers", []),
            "source": "Matriks Data AKD (Gerçek)",
            "status": "Gerçek Veri"
        }
    
    def get_takas(self, symbol):
        """
        MKK Takas/Saklama dağılımı.
        Endpoint: GET /takas/{symbol}
        """
        data = self._get(f"/takas/{symbol.upper()}")
        if "error" in data:
            return data
        
        return {
            "symbol": symbol.upper(),
            "date": data.get("date", datetime.now().strftime("%d/%m/%Y")),
            "holders": data.get("holders", []),
            "source": "Matriks Data - MKK Saklama (Gerçek)",
            "status": "EOD"
        }
    
    def get_viop(self, contract=None):
        """
        VIOP vadeli kontrat verileri.
        Endpoint: GET /viop/contracts
        """
        params = {}
        if contract:
            params["contract"] = contract
        
        data = self._get("/viop/contracts", params=params)
        if "error" in data:
            return data
        
        return data.get("contracts", [])
    
    def get_institutional_flow(self):
        """
        Kurumsal para akışı (bugünkü).
        Endpoint: GET /institutional/flow
        """
        data = self._get("/institutional/flow", params={"date": datetime.now().strftime("%Y-%m-%d")})
        if "error" in data:
            return data
        
        return data.get("institutions", [])


# Singleton instance
matriks = MatriksAPI()


def get_matriks_quote(symbol):
    """Matriks'ten anlık fiyat."""
    return matriks.get_quote(symbol)

def get_matriks_orderbook(symbol, levels=5):
    """Matriks'ten emir defteri."""
    return matriks.get_orderbook(symbol, levels)

def get_matriks_akd(symbol):
    """Matriks'ten AKD verisi."""
    return matriks.get_akd(symbol)

def get_matriks_takas(symbol):
    """Matriks'ten takas verisi."""
    return matriks.get_takas(symbol)

def get_matriks_status():
    """Matriks API durumu."""
    return {
        "configured": matriks.is_configured(),
        "api_key_set": bool(matriks.api_key),
        "base_url": matriks.base_url,
        "message": "✅ API key ayarlı, hazır!" if matriks.is_configured() else "❌ MATRIKS_API_KEY .env'de eksik"
    }


if __name__ == "__main__":
    import sys
    status = get_matriks_status()
    print(json.dumps(status, ensure_ascii=False, indent=2))
    
    if matriks.is_configured():
        symbol = sys.argv[1].upper() if len(sys.argv) > 1 else "THYAO"
        print(json.dumps(get_matriks_quote(symbol), ensure_ascii=False, indent=2))
