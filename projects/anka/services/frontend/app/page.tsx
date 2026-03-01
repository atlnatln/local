import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { CheckCircle2, ShieldCheck, Search, Database, Fingerprint, MapPin, Building2, Phone, Globe } from 'lucide-react'

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen bg-slate-50 text-slate-900 font-sans">
      {/* Navbar */}
      <header className="px-4 sm:px-6 py-4 flex items-center justify-between border-b bg-white">
        <div className="flex items-center gap-2 font-bold text-lg sm:text-xl text-slate-800">
          <Database className="w-5 h-5 sm:w-6 sm:h-6 text-indigo-600" />
          <span>Anka Data</span>
        </div>
        <div className="flex items-center gap-2 sm:gap-4">
          <Link href="/login">
            <Button size="sm" className="sm:hidden">Giriş Yap</Button>
            <Button className="hidden sm:inline-flex">Giriş Yap</Button>
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <section className="px-4 sm:px-6 py-12 sm:py-20 lg:py-32 max-w-7xl mx-auto grid lg:grid-cols-2 gap-8 lg:gap-12 items-center">
        <div className="space-y-6 sm:space-y-8">
          <div className="space-y-4">
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-slate-900 leading-tight">
              İstediğiniz şehir ve sektörde, <span className="text-indigo-600">doğrulanmış firma iletişim bilgilerini</span> tek seferde alın.
            </h1>
            <p className="text-lg text-slate-600 max-w-xl">
              Eksik, kapalı veya hatalı kayıtlar elenir. Sadece gerçekten var olan firmalar teslim edilir.
            </p>
          </div>
          
          <div className="flex flex-col sm:flex-row gap-4">
            <Link href="/dashboard">
              <Button size="lg" className="w-full sm:w-auto text-base px-8 h-12 bg-indigo-600 hover:bg-indigo-700">
                Liste Oluştur
              </Button>
            </Link>
            <a href="#nasil-calisir">
              <Button variant="outline" size="lg" className="w-full sm:w-auto text-base px-8 h-12">
                Nasıl Çalışır?
              </Button>
            </a>
          </div>
          
          <p className="text-sm text-slate-500 flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            Doğrulanmış veri garantisi • Kredi kartı gerekmez
          </p>
        </div>

        {/* Static Mock Table */}
        <div className="bg-white rounded-xl shadow-2xl border border-slate-200 overflow-hidden select-none opacity-90 hover:opacity-100 transition-opacity">
          <div className="bg-slate-50 px-4 py-3 border-b border-slate-200 flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-red-400"></div>
            <div className="w-3 h-3 rounded-full bg-amber-400"></div>
            <div className="w-3 h-3 rounded-full bg-emerald-400"></div>
            <span className="ml-2 text-xs font-mono text-slate-500">ankadata_preview.csv</span>
          </div>
          <div className="p-4 overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-slate-100">
                  <th className="pb-2 font-medium text-slate-500">Firma Adı</th>
                  <th className="pb-2 font-medium text-slate-500">Şehir</th>
                  <th className="pb-2 font-medium text-slate-500">Durum</th>
                  <th className="pb-2 font-medium text-slate-500">Telefon</th>
                </tr>
              </thead>
              <tbody className="text-slate-700">
                <tr className="border-b border-slate-50">
                  <td className="py-2.5 font-medium">Atlas Mimarlık</td>
                  <td className="py-2.5 text-slate-500">İstanbul</td>
                  <td className="py-2.5"><span className="bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded-full text-xs font-semibold">Aktif</span></td>
                  <td className="py-2.5 font-mono text-xs">+90 212 555 01..</td>
                </tr>
                <tr className="border-b border-slate-50">
                  <td className="py-2.5 font-medium">Yıldız İnşaat Ltd.</td>
                  <td className="py-2.5 text-slate-500">Ankara</td>
                  <td className="py-2.5"><span className="bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded-full text-xs font-semibold">Aktif</span></td>
                  <td className="py-2.5 font-mono text-xs">+90 312 444 02..</td>
                </tr>
                <tr className="border-b border-slate-50 opacity-40 bg-slate-50/50">
                  <td className="py-2.5 font-medium line-through">Eski Restoran A.Ş.</td>
                  <td className="py-2.5 text-slate-500">İzmir</td>
                  <td className="py-2.5"><span className="bg-slate-200 text-slate-600 px-2 py-0.5 rounded-full text-xs font-semibold">Kapalı</span></td>
                  <td className="py-2.5 font-mono text-xs">-</td>
                </tr>
                <tr>
                  <td className="py-2.5 font-medium">Tech Solutions</td>
                  <td className="py-2.5 text-slate-500">Bursa</td>
                  <td className="py-2.5"><span className="bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded-full text-xs font-semibold">Aktif</span></td>
                  <td className="py-2.5 font-mono text-xs">+90 224 333 03..</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Second Level Promise */}
      <section className="bg-white py-16 sm:py-24 border-y border-slate-200">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6">
          <p className="text-2xl text-slate-800 font-medium leading-relaxed">
            “Sistemimiz internetteki devasa veri havuzunu önce ücretsiz olarak tarayıp aday listesi oluşturur. 
            Ardından bu adayların gerçekten var olduğunu doğrulamak için düşük maliyetli bir kontrol yapar. 
            Sadece doğrulanmış ve kaliteli kayıtlara iletişim bilgisi ekleyerek bütçenizi boşa harcamadan en temiz listeyi sunar.”
          </p>
        </div>
      </section>

      {/* How It Works */}
      <section id="nasil-calisir" className="py-16 sm:py-24 max-w-7xl mx-auto px-4 sm:px-6 scroll-mt-8">
        <div className="grid md:grid-cols-3 gap-12 text-center md:text-left">
          <div className="space-y-4">
            <div className="w-12 h-12 bg-indigo-100 text-indigo-600 rounded-lg flex items-center justify-center mb-4 mx-auto md:mx-0">
              <Search className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-bold text-slate-900">Tarama</h3>
            <p className="text-slate-600">Sektör ve şehir bazlı aday firmalar milyonlarca kayıt arasından taranır ve bulunur.</p>
          </div>
          <div className="space-y-4">
            <div className="w-12 h-12 bg-indigo-100 text-indigo-600 rounded-lg flex items-center justify-center mb-4 mx-auto md:mx-0">
              <CheckCircle2 className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-bold text-slate-900">Doğrulama</h3>
            <p className="text-slate-600">Kapalı, taşınmış, alakasız veya hatalı kayıtlar otomatik olarak elenir.</p>
          </div>
          <div className="space-y-4">
            <div className="w-12 h-12 bg-indigo-100 text-indigo-600 rounded-lg flex items-center justify-center mb-4 mx-auto md:mx-0">
              <Database className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-bold text-slate-900">Teslim</h3>
            <p className="text-slate-600">Telefon ve web bilgileri zenginleştirilmiş temiz liste indirilebilir formatta sunulur.</p>
          </div>
        </div>
      </section>

      {/* What You Get & Audience */}
      <section className="bg-slate-900 text-slate-50 py-16 sm:py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 grid md:grid-cols-2 gap-12 md:gap-16">
          <div className="space-y-8">
            <h3 className="text-3xl font-bold">Ne Alırsınız?</h3>
            <ul className="space-y-4">
              <li className="flex items-center gap-3">
                <Building2 className="text-indigo-400 w-5 h-5" />
                <span className="text-lg">Resmi Firma Adı</span>
              </li>
              <li className="flex items-center gap-3">
                <MapPin className="text-indigo-400 w-5 h-5" />
                <span className="text-lg">Tam Adres ve Lokasyon</span>
              </li>
              <li className="flex items-center gap-3">
                <Phone className="text-indigo-400 w-5 h-5" />
                <span className="text-lg">Doğrulanmış Telefon Numarası</span>
              </li>
              <li className="flex items-center gap-3">
                <Globe className="text-indigo-400 w-5 h-5" />
                <span className="text-lg">Web Sitesi ve Dijital Varlık</span>
              </li>
              <li className="flex items-center gap-3">
                <Fingerprint className="text-indigo-400 w-5 h-5" />
                <span className="text-lg">Detaylı Sektör Bilgisi</span>
              </li>
            </ul>
            <p className="text-sm text-slate-400 pt-4 border-t border-slate-800">
              * Bilgiler kamuya açık yasal kaynaklardan derlenir ve teslim öncesi canlı kontrol edilir.
            </p>
          </div>

          <div className="space-y-8">
            <h3 className="text-3xl font-bold">Kimler İçin?</h3>
            <div className="grid gap-4">
              <div className="p-4 rounded-lg bg-slate-800 border border-slate-700">
                <h4 className="font-bold text-white mb-1">B2B Satış Ekipleri</h4>
                <p className="text-slate-400 text-sm">Hedef kitlenize doğrudan ulaşın, vakit kaybetmeyin.</p>
              </div>
              <div className="p-4 rounded-lg bg-slate-800 border border-slate-700">
                <h4 className="font-bold text-white mb-1">Danışmanlar</h4>
                <p className="text-slate-400 text-sm">Pazar araştırması ve potansiyel müşteri analizi için.</p>
              </div>
              <div className="p-4 rounded-lg bg-slate-800 border border-slate-700">
                <h4 className="font-bold text-white mb-1">Yerel Hizmet Sağlayıcılar</h4>
                <p className="text-slate-400 text-sm">Bölgenizdeki işletmeleri harita hassasiyetinde listeleyin.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Assurance / Footer */}
      <section className="py-12 sm:py-20 max-w-3xl mx-auto px-4 sm:px-6 text-center space-y-6">
        <h2 className="text-2xl font-bold text-slate-900">Yanlış kayıt riskini nasıl yönetiyoruz?</h2>
        <p className="text-lg text-slate-600">
          Teslim edilen listede hatalı veya ulaşılamayan kayıtları bildirmeniz halinde, 
          karşılığı sistem bakiyenize iade edilir. Sadece çalışan veri için ödeme yaparsınız.
        </p>
        <div className="pt-8">
             <Link href="/dashboard">
              <Button size="lg" className="bg-slate-900 hover:bg-slate-800 px-10">
                Hemen Başlayın
              </Button>
            </Link>
        </div>
      </section>

      <footer className="py-8 border-t bg-white text-center text-sm text-slate-500">
        &copy; {new Date().getFullYear()} Anka Data. Tüm hakları saklıdır.
      </footer>
    </div>
  )
}
