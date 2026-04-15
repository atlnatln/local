import Seo from '../../components/Seo';
import Layout from '../../components/Layout';
import styles from '../../styles/DocumentPage.module.css';

export default function TarimYapiKriterleriPage() {
  return (
    <>
      <Seo
        title="Tarımsal Yapı Kriterleri - Tarımsal Amaçlı Yapıların Kriterleri Talimatı"
        description="Tarımsal amaçlı yapıların kriterleri: bağ evi, sera, hayvancılık tesisleri, fide-fidan üretimi, sahipsiz hayvan barınakları, GES ve tüm tarımsal yapı türleri için alan ve yapılaşma koşulları"
        canonical="https://tarimimar.com.tr/documents/tarimsal-yapi-kriterleri/"
        url="https://tarimimar.com.tr/documents/tarimsal-yapi-kriterleri/"
        ogImage="https://tarimimar.com.tr/og-image.svg"
        type="article"
        keywords="tarımsal yapı kriterleri, bağ evi koşulları, sera yapılaşma, hayvancılık tesisi, fide fidan üretim, sundurma çiftlik atölyesi, tarımsal GES, hara, sahipsiz hayvan barınağı, islim, muz sarartma, teleferik, gölet, mandıra, un değirmeni"
      />
      <Layout>
        <div className={styles.container}>
          <div className={styles.header}>
            <h1>📋 Tarımsal Yapı Kriterleri</h1>
            <p>Tarımsal Amaçlı Yapıların Kriterleri Talimatı (5403 sayılı Kanun kapsamında)</p>
          </div>

          <div className={styles.content}>

            {/* TANIM */}
            <section className={styles.section}>
              <h2>🏗️ Tarımsal Amaçlı Yapılar — Tanım ve Kapsam</h2>
              <div className={styles.highlight}>
                <p>
                  Tarımsal amaçlı yapılar; toprak koruma ve sulamaya yönelik altyapı tesisleri, entegre
                  nitelikte olmayan hayvancılık ve su ürünleri üretim ve muhafaza tesisleri ile zorunlu olarak
                  tesis edilmesi gerekli olan müştemilatı, mandıra, üreticinin bitkisel üretime bağlı olarak
                  elde ettiği ürünü için ihtiyaç duyacağı yeterli boyut ve hacimde depolar, un değirmeni,
                  tarım alet ve makinelerinin muhafazasında kullanılan sundurma ve çiftlik atölyeleri,
                  seralar, tarımsal işletmede üretilen ürünün özelliği itibarıyla hasattan sonra iki saat
                  içinde işlenmediği takdirde ürünün kalite ve besin değeri kaybolması söz konusu ise bu
                  ürünlerin işlenmesi için kurulan tesisler ile Bakanlık tarafından tarımsal amaçlı olduğu
                  kabul edilen entegre nitelikte olmayan diğer tesislerdir.
                </p>
                <p style={{ marginTop: '0.75rem' }}>
                  <strong>Bakanlık tarafından tarımsal amaçlı kabul edilen diğer tesisler:</strong> ipek
                  böcekçiliği üretim alanı, hara (at üretimi/yetiştiriciliği), deve kuşu üretim tesisi,
                  tarımsal amaçlı depo, solucan ve solucan gübresi üretim tesisi, yumru köklü bitkilerin
                  yıkama tesisi, hububat/çeltik/ceviz/ayçiçeği kurutma tesisi, islim ünitesi, muz sarartma
                  ünitesi, hayvan içme suyu göleti, tarımsal AR-GE tesisleri, fide ve fidan üretim tesisleri,
                  tarımsal amaçlı teleferik, bağ evi, sahipsiz hayvan barınakları, çatı GES ve sulama GES.
                </p>
              </div>
            </section>

            {/* BAŞVURU BELGELERİ */}
            <section className={styles.section}>
              <h2>📄 İzin Başvurusu İçin Gerekli Belgeler</h2>
              <div className={styles.info}>
                <ul>
                  <li>Müracaat dilekçesi veya yazısı</li>
                  <li>TAD Portal giriş numarasının yazılı olduğu talep üst yazısı</li>
                  <li>Onaylı arazi etüt raporu</li>
                  <li>Toprak koruma kurulu görüşü (varsa şerhlerle birlikte)</li>
                  <li>Talep konusu parselleri ve tesisin yerleşimini gösteren <strong>kml/kmz uzantılı dosya</strong></li>
                  <li>Noter onaylı taahhütname (Ek-7)</li>
                  <li>DSİ kurum görüşü ve diğer kurum görüşleri</li>
                  <li>SMM büro tescil belgesi olan ziraat mühendisi tarafından hazırlanan <strong>proje teknik raporu</strong> (Ek-16 dispozisyonu)</li>
                  <li>Vaziyet planı</li>
                  <li>Arazi fotoğrafları</li>
                  <li>Hisseli arazilerde <strong>noter onaylı muvafakatname</strong> (Ek-17)</li>
                  <li>Tarımsal GES taleplerinde noter onaylı taahhütname (Ek-14)</li>
                  <li>Büyük ova içindeki taleplerde organize sanayi bölgesi alternatif alan görüşü</li>
                  <li>Sulama GES taleplerinde bireysel/modern basınçlı sulama sistemi projesi</li>
                  <li>Tarımsal GES taleplerinde meslek odasına kayıtlı elektrik mühendisi raporu</li>
                </ul>
              </div>
            </section>

            {/* GENEL HÜKÜMLER */}
            <section className={styles.section}>
              <h2>⚖️ Genel İzinlendirme Hükümleri</h2>
              <div className={styles.info}>
                <ul>
                  <li><strong>Alternatif alan:</strong> Bağ evi ve sera taleplerinde alternatif alan aranmaz.</li>
                  <li><strong>Ulaşım yolu:</strong> Parseldeki tarımsal amaçlı yapıya ulaşım yolu müştemilat olarak kabul edilir.</li>
                  <li><strong>Tarımsal kullanım bütünlüğü:</strong> Tarımsal amaçlı yapı taleplerinde aranmaz.</li>
                  <li><strong>Tapu şerhi:</strong> İzin verilen parselin tapu kaydına "Bu parsel tarımsal amaçlı yapı için izin verilmiş olup başka amaçla kullanılamaz" ibaresi eklenir; Bakanlığın talebi olmadan kaldırılamaz.</li>
                  <li><strong>Projeye uygunluk:</strong> İzinlendirilen yapının projesine uygun yapılması, tarımsal amaç dışında kullanılmaması, arsaya dönüştürülmemesi şartı; ihlalde izin iptal edilir ve ruhsat merciine bildirilir.</li>
                  <li><strong>Kiralama:</strong> Büyük ova içi/dışı kiralamada en az 10 yıllık kiralama, tapuya işlenmesi ve aynı ilçede mülk bulunmaması şartıyla izinlendirme yapılabilir.</li>
                </ul>
              </div>
            </section>

            {/* 1. TOPRAK KORUMA */}
            <section className={styles.section}>
              <h2>🌊 1. Toprak Korumaya Yönelik Altyapı Tesisleri</h2>
              <div className={styles.info}>
                <ul>
                  <li>Su ve rüzgâr erozyonuna karşı <strong>seki, teras ve rüzgâr perdeleri</strong></li>
                  <li>Taşkın koruma amaçlı <strong>seddeler ve istinat duvarları</strong></li>
                </ul>
              </div>
            </section>

            {/* 2. SULAMA */}
            <section className={styles.section}>
              <h2>💧 2. Sulamaya Yönelik Altyapı Tesisleri</h2>
              <div className={styles.info}>
                <ul>
                  <li>Tarımsal sulama amaçlı <strong>baraj, göl, gölet</strong> ve bunların müştemilatı</li>
                  <li>Tahliye kanalı, drenaj kanalı, kanal, kanalet, hidrant, su kuyuları</li>
                  <li>Tarımsal amaçlı yapılar için ihtiyaç duyulan <strong>su depoları</strong></li>
                  <li>Bitkisel üretim için yağmur suyu ve benzeri suların yeraltında veya yer üstünde depolanması amaçlı depo, havuz ve benzeri yapılar</li>
                  <li>Bunlar için gerekli <strong>pompaj tesisleri</strong></li>
                </ul>
              </div>
            </section>

            {/* 3. SERA */}
            <section className={styles.section}>
              <h2>🌿 3. Sera</h2>
              <div className={styles.subsection}>
                <div className={styles.highlight}>
                  <ul>
                    <li>Yapılmış veya yapılacak seralarda <strong>20 m²'den az olmamak şartıyla</strong>, taban alanı sera alanının <strong>%5'ine kadar</strong> idari ve teknik bina (laboratuvar, soğuk oda, ofis, tuvalet/duş, soyunma odası, yemekhane dahil) tarımsal amaçlı yapı olarak kabul edilir.</li>
                    <li>Asgari <strong>0,3 hektar</strong> sera arazisinde bakıcı evi talebi kabul edilir; serayla birlikte yapılmasına izin verilebilir.</li>
                    <li>Sera üzerine GES tesisi bitkisel üretim tekniği açısından uygun görülmemektedir.</li>
                    <li>Marjinal tarım arazisinde proje alanının en fazla <strong>%1,5'ine zemine GES</strong> kurulabilir.</li>
                    <li>İzin verilen seralar, bitkisel üretim yapılmayan dönemlerde; kurutma fanı olması, beton/mıcır/parke taşı kullanılmaması ve tapudaki cinsinin değiştirilmemesi koşuluyla büyükbaş için <strong>geçici barınak</strong> olarak kullanılabilir. (Gübre yolu max 4 m, yem yolu max 4 m, sağımhane max %1 alan; yalnızca bu alanlarda beton kullanılabilir.)</li>
                  </ul>
                </div>
              </div>
            </section>

            {/* 4. FİDE FİDAN */}
            <section className={styles.section}>
              <h2>🌱 4. Fide ve Fidan Üretim Tesisleri</h2>
              <div className={styles.subsection}>
                <h3>4.1 Fide Üretim Tesisi</h3>
                <div className={styles.info}>
                  <ul>
                    <li>Fide üretimi için <strong>en az 0,2 hektar sera</strong></li>
                    <li>Fidelerin depolanıp sevkiyatı için en çok <strong>500 m² kapalı alan</strong></li>
                    <li>Bu kapasiteyi aşan talepler için oranlama yapılarak alan belirlenir.</li>
                  </ul>
                </div>
              </div>
              <div className={styles.subsection}>
                <h3>4.2 Fidan Üretim Tesisi</h3>
                <div className={styles.info}>
                  <p><strong>Açık alanda üretim:</strong> Her bin adet kapasite için;</p>
                  <ul>
                    <li><strong>1,5–2,5 m²</strong> soğuk hava deposu</li>
                    <li><strong>0,15 m²</strong> yönetim ve idare binası</li>
                    <li><strong>0,1 m²</strong> depo (malzemeler için)</li>
                  </ul>
                  <p style={{ marginTop: '0.5rem' }}><strong>Doku kültürü yöntemi:</strong> Her bin adet kapasite için;</p>
                  <ul>
                    <li><strong>0,1 m²</strong> iklimlendirme odası</li>
                    <li><strong>0,02 m²</strong> transfer odası</li>
                    <li><strong>7 m²</strong> sera alanı</li>
                  </ul>
                </div>
              </div>
            </section>

            {/* 5. SAHİPSİZ HAYVAN */}
            <section className={styles.section}>
              <h2>🐾 5. Sahipsiz Hayvan Barınakları</h2>
              <div className={styles.warning}>
                <ul>
                  <li><strong>Büyük ova koruma alanları dışındaki marjinal sınıf tarım arazilerinde</strong> yapılabilir</li>
                  <li>Doğa Koruma ve Milli Parklar Genel Müdürlüğü uygun görüşü şarttır</li>
                  <li>Arazi üzerinde <strong>kazı-dolgu yapılmadan, beton atılmadan</strong></li>
                  <li><strong>Sökülüp takılabilir, istenildiği zaman kaldırılabilir</strong> şekilde yapılmalıdır</li>
                </ul>
              </div>
            </section>

            {/* 6. BAĞ EVİ */}
            <section className={styles.section}>
              <h2>🏠 6. Bağ Evi</h2>
              <div className={styles.subsection}>
                <div className={styles.highlight}>
                  <h4>📏 Arazi Büyüklüğü Koşulları</h4>
                  <ul>
                    <li>Yüzölçümü <strong>5 hektar ve üzeri</strong> olan mutlak, özel ürün ve marjinal tarım arazisi</li>
                    <li>Yüzölçümü <strong>1 hektar ve üzeri</strong> olan dikili tarım arazisi</li>
                    <li><strong>0,3 hektar ve üzeri</strong> örtüaltı tarım arazisi</li>
                  </ul>
                  <h4>🏘️ Yapılaşma Koşulları</h4>
                  <ul>
                    <li>Taban alanı: <strong>En fazla 30 m²</strong>, iki katlı</li>
                    <li><em>(İnşaat alanı: en fazla 60 m²)</em></li>
                  </ul>
                  <h4>⚠️ Özel Kısıtlamalar</h4>
                  <ul>
                    <li>Kiralanan arazilere kiracılar bağ evi talep edemez</li>
                    <li>Her aile için aynı ilçe içinde <strong>sadece bir adet</strong> bağ evi izni</li>
                    <li>Her parselde <strong>sadece bir adet</strong> bağ evi izni</li>
                    <li>Dikili/örtü altı arazinin tapudaki vasfı farklıysa önce cins değişikliği yapılır</li>
                    <li>Hisseli parsellerde diğer hissedarlardan <strong>muvafakatname</strong> zorunludur</li>
                  </ul>
                </div>
              </div>
            </section>

            {/* 7. TARIMSAL DEPO */}
            <section className={styles.section}>
              <h2>🏪 7. Tarımsal Amaçlı Depo</h2>
              <div className={styles.info}>
                <p>Üreticinin bitkisel üretimden elde ettiği ürünü için ihtiyaç duyduğu depo; arazi varlığının sınıfa göre asgari büyüklüğü aşması koşuluyla <strong>toplam arazi varlığının %1'i</strong> kadar alana yapılabilir.</p>
                <h4>Arazi Varlığı Asgari Eşiği:</h4>
                <ul>
                  <li>Mutlak tarım, marjinal ve özel ürün arazileri: <strong>2 hektar</strong> üzeri</li>
                  <li>Dikili tarım arazileri: <strong>1 hektar</strong> üzeri</li>
                  <li>Örtü altı tarımı yapılan araziler: <strong>0,3 hektar</strong> üzeri</li>
                </ul>
                <p style={{ marginTop: '0.5rem' }}>
                  Üretici örgütleri tarafından üyelerinin ihtiyacı için depo, örgüte üye çiftçilerin arazi varlığının %1'ine kurulabilir; bu izni alan üyeler ayrıca depo talebinde bulunamazlar.
                </p>
                <div className={styles.warning} style={{ marginTop: '0.75rem' }}>
                  <ul>
                    <li>Kiralama ve sözleşmeli üretim arazileri depo alanı hesabına dahil edilmez</li>
                    <li>Hisseli parsellerde hisse oranı arazi varlığı hesabına dahil edilir</li>
                    <li>İhtiyaç olduğu il müdürlüğünce incelenerek belirlenir</li>
                  </ul>
                </div>
              </div>
            </section>

            {/* 8. SUNDURMA VE ÇİFTLİK ATÖLYESİ */}
            <section className={styles.section}>
              <h2>🔧 8. Sundurma ve Çiftlik Atölyesi</h2>
              <div className={styles.highlight}>
                <p>Tarım alet ve makinelerinin muhafazasında kullanılır. Arazi varlığı 7. maddenin asgari eşiklerini aşıyorsa, her sınıftaki tarım arazisine:</p>
                <ul>
                  <li>Kenarları açık veya yarı açık, <strong>en fazla 50 m²</strong> sundurma</li>
                  <li>ve/veya <strong>en fazla 50 m²</strong> çiftlik atölyesi</li>
                </ul>
                <p>izin verilebilir.</p>
              </div>
            </section>

            {/* 9. HASAT SONRASI İŞLEME */}
            <section className={styles.section}>
              <h2>⏱️ 9. Hasattan Sonra 2 Saat İçinde İşlenmesi Gereken Ürünlerin Tesisleri</h2>
              <div className={styles.info}>
                <p>
                  Tarımsal işletmede üretilen ürünün özelliği itibarıyla hasattan sonra 2 saat içinde
                  işlenmediğinde ürünün kalite ve besin değeri kaybolması söz konusu ise bu ürünlerin
                  işlenmesi için kurulan tesisler tarımsal amaçlı yapı olarak kabul edilir.
                </p>
                <p style={{ marginTop: '0.5rem' }}>
                  <strong>Kapsam:</strong> Yağ gülü, yasemin, stevya ve Tarımsal Araştırmalar Genel
                  Müdürlüğünce onaylanmış diğer ürünler.
                </p>
              </div>
            </section>

            {/* 10. GES */}
            <section className={styles.section}>
              <h2>☀️ 10. Tarımsal Amaçlı GES</h2>
              <div className={styles.subsection}>
                <h3>10.1–10.6 Müştemilat GES (Tarımsal Yapı Çatısı/Zemini)</h3>
                <div className={styles.info}>
                  <ul>
                    <li><strong>Mutlak, özel ürün veya dikili arazi:</strong> Yalnızca tesisin ihtiyacı kadar enerji için tesisin <strong>çatısına</strong> izin verilebilir.</li>
                    <li><strong>Marjinal arazi:</strong> Öncelikle çatıya; yetmezse tesis alanının en fazla <strong>%1,5'i</strong> kadar zemine izin verilebilir.</li>
                    <li>Elektrik mühendisi tarafından kapasite raporu hazırlanması zorunludur.</li>
                    <li>Üretilen enerjinin tarımsal amaç dışında kullanılmayacağına dair <strong>noter taahhütnamesi</strong> (Ek-14) alınır.</li>
                    <li>Taahhüde uyulmaması halinde izin iptal edilir; EPDK'ya bildirilir.</li>
                  </ul>
                </div>
              </div>
              <div className={styles.subsection}>
                <h3>10.7 Sulama Amaçlı GES</h3>
                <div className={styles.info}>
                  <ul>
                    <li>Enerjinin ulusal ağa verilmeyeceği taahhüt edilmeli veya bağlantı hattı bulunmamalı</li>
                    <li>Hisseli arazilerde diğer hissedarlardan <strong>muvafakatname</strong> zorunlu</li>
                    <li>DSİ'den izinli pompaj tesisi, aynı kişiye ait olmalı</li>
                    <li>Pompaj tesislerinin sulayabildiği toplam arazinin en fazla <strong>%1,5'i</strong> kadar alan</li>
                    <li><strong>Mutlak/özel ürün/dikili arazi:</strong> Aynı il sınırlarında toplam <strong>20 hektar ve üzeri</strong> arazi varlığı şartı</li>
                    <li>Yalnızca <strong>bireysel/modern basınçlı sulama sistemi</strong> kullanan üreticilere izin verilir</li>
                    <li>Kiralanan araziler toplam arazi varlığı hesabına dahil edilmez</li>
                  </ul>
                </div>
              </div>
            </section>

            {/* 11. HAYVANCILIK */}
            <section className={styles.section}>
              <h2>🐄 11. Entegre Nitelikte Olmayan Hayvancılık Tesisleri</h2>
              <div className={styles.info}>
                <p>Hayvancılık tesislerinin müştemilatından sayılanlar: hayvan gezinti alanı, sağımhane ve revir, silaj çukuru, doğumhane, bakıcı evi (kapasiteye göre), yem deposu, samanlık, su deposu, malzeme deposu, gübre deposu, aynı işletmede üretilen ürünün paketleme/depo tesisi, bekçi kulübesi, jeneratör odası, istinat duvarı, işletme içi yollar.</p>
                <div className={styles.warning} style={{ marginTop: '0.75rem' }}>
                  <p><strong>Önemli:</strong> Bakıcı evi, ahır/ağıl/kümes ile yem deposu ve gübre çukurundan <em>sonra</em> yapılmalıdır. Aksi halde tarım dışı kullanım sayılır.</p>
                </div>
                <div className={styles.highlight} style={{ marginTop: '0.75rem' }}>
                  <h4>🏠 İdari Bina — Standart Ölçü (Hayvancılık)</h4>
                  <ul>
                    <li>Taban alanı <strong>75 m²</strong>, inşaat alanı <strong>150 m²</strong> yi geçmeyecek bakıcı evi / idari bina (büyükbaş kapalı alanı 550–1500 m² arasındaki tesisler için)</li>
                    <li>Kapalı alanı <strong>1500 m²'yi aşan</strong> büyükbaş tesislerde: taban alanı <strong>150 m²</strong>, inşaat alanı <strong>300 m²</strong></li>
                  </ul>
                </div>
              </div>

              {/* 11.1 Geçici */}
              <div className={styles.subsection}>
                <h3>11.1 Geçici Hayvan Barınakları</h3>
                <div className={styles.info}>
                  <ul>
                    <li>Çadır tipi yapılar; kazı-dolgu ve beton olmadan, toprak zemin üzerine, sökülüp takılabilir şekilde yapılabilir</li>
                    <li>TAD Portala girişi yapılmaksızın kurulabilir (taahhütname alınır)</li>
                    <li>Müştemilat yapılmasına izin verilmez</li>
                  </ul>
                </div>
              </div>

              {/* 11.2 Su Ürünleri */}
              <div className={styles.subsection}>
                <h3>11.2 Su Ürünleri Üretim Tesisleri</h3>
                <div className={styles.info}>
                  <ul>
                    <li>Balıkçılık ve Su Ürünleri Genel Müdürlüğü tarafından <strong>yetiştiricilik projesi onaylanan</strong> tesislere tarımsal amaçlı yapı izni verilebilir</li>
                    <li>Taban alanı <strong>75 m²</strong>, toplam inşaat alanı <strong>150 m²</strong>'yi geçmeyen bakıcı evine izin verilebilir</li>
                  </ul>
                </div>
              </div>

              {/* 11.3 İpek böceği */}
              <div className={styles.subsection}>
                <h3>11.3 İpek Böceği Üretim Tesisi</h3>
                <div className={styles.info}>
                  <ul>
                    <li>50 dekara kadar dikili arazi normuna uygun <strong>dut bahçesi</strong> gereklidir</li>
                    <li>Dut bahçesi alanının <strong>%10–12'si</strong>: ipek böceği besleme evi, depo ve ipek çekim odası</li>
                    <li>Müştemilat olarak <strong>75 m² idari bina</strong> ve <strong>75 m² bakıcı evi</strong> izni verilebilir</li>
                  </ul>
                </div>
              </div>

              {/* 11.4 Arıhane */}
              <div className={styles.subsection}>
                <h3>11.4 Arıhane / Arı Kışlatma Evi</h3>
                <div className={styles.info}>
                  <ul>
                    <li>En az <strong>50 arılı kovana</strong> sahip olunması ve AKS'ye kayıtlı olunması şartı</li>
                    <li>Bir işletmeye: <strong>50 m²</strong> arıhane veya arı kışlatma evi</li>
                    <li>İlave her <strong>50 arılı kovan</strong> için ilave <strong>10 m²</strong> alan</li>
                  </ul>
                </div>
              </div>

              {/* 11.5 Solucan */}
              <div className={styles.subsection}>
                <h3>11.5 Solucan Gübresi Üretim Tesisleri</h3>
                <div className={styles.info}>
                  <ul>
                    <li>İhtiyaç duyulan alan <strong>en az 500 m²</strong></li>
                    <li>Müştemilat: temiz alan, kirli alan, kompostlama alanı, ısıl işlem ünitesi, paketleme ünitesi, depolama alanı, giyinme odası, yemekhane, büro, tuvalet ve duş</li>
                  </ul>
                </div>
              </div>

              {/* 11.6 Hara */}
              <div className={styles.subsection}>
                <h3>11.6 Hara (At Üretimi ve Yetiştiriciliği)</h3>
                <div className={styles.highlight}>
                  <ul>
                    <li>Asgari kapasite: <strong>en az 10 baş damızlık kısrak</strong></li>
                    <li>10 kısraklı işletmede ahırlar ortalama <strong>40 boks</strong> kapasiteli olmalıdır</li>
                    <li>Her bir boks büyüklüğü: kısrak <strong>4×4 m</strong>, yavrulama bölmesi <strong>5×5 m</strong>, aygır <strong>5×5 m</strong></li>
                    <li>Bakıcı evi: ahır alanının <strong>%6–7'si</strong></li>
                    <li>Yem deposu: ahır alanının <strong>%7–8'i</strong></li>
                    <li>Padok (serbest gezinti): bireysel boksun <strong>en az 2 katı</strong></li>
                    <li>Maneş (antrenman alanı): <strong>3×6 m</strong></li>
                    <li>Müştemilat: ahır (tavla), padok, sundurma, maneş, yem deposu, gübre çukuru, bakıcı evi</li>
                  </ul>
                </div>
              </div>

              {/* 11.7 Büyükbaş */}
              <div className={styles.subsection}>
                <h3>11.7 Büyükbaş Hayvancılık (Ahır)</h3>
                <div className={styles.info}>
                  <ul>
                    <li>Kapalı alan <strong>550–1500 m²</strong> arasında: bakıcı evi taban alanı <strong>75 m²</strong>, inşaat <strong>150 m²</strong></li>
                    <li>Kapalı alan <strong>1500 m²'den büyük:</strong> bakıcı evi taban alanı <strong>150 m²</strong>, inşaat <strong>300 m²</strong></li>
                  </ul>
                </div>
              </div>

              {/* 11.8 Küçükbaş */}
              <div className={styles.subsection}>
                <h3>11.8 Küçükbaş Hayvancılık (Ağıl)</h3>
                <div className={styles.info}>
                  <ul>
                    <li>Kapalı alan <strong>450–900 m²</strong> arasında: bakıcı evi taban alanı <strong>75 m²</strong>, inşaat <strong>150 m²</strong></li>
                    <li>Kapalı alan <strong>900 m²'den büyük:</strong> bakıcı evi taban alanı <strong>150 m²</strong>, inşaat <strong>300 m²</strong></li>
                  </ul>
                </div>
              </div>

              {/* 11.9 Kanatlı */}
              <div className={styles.subsection}>
                <h3>11.9 Kanatlı Hayvancılık Tesisi (Kümes)</h3>
                <div className={styles.info}>
                  <ul>
                    <li>Kapalı alan <strong>750–1500 m²</strong> arasında: bakıcı evi taban alanı <strong>75 m²</strong>, inşaat <strong>150 m²</strong></li>
                    <li>Kapalı alan <strong>1500 m² üzeri:</strong> bakıcı evi taban alanı <strong>150 m²</strong>, inşaat <strong>300 m²</strong></li>
                    <li>Kuluçkahaneler, damızlık kanatlı kümeslerin müştemilatı sayılır</li>
                  </ul>
                  <div className={styles.highlight} style={{ marginTop: '0.75rem' }}>
                    <h4>🐓 Deve Kuşu Üretim Tesisleri (11.9.3)</h4>
                    <ul>
                      <li>Kapalı alan <strong>en az 100 m²</strong>, gezinti alanı <strong>en az 350 m²</strong></li>
                      <li>Bakıcı evi: taban <strong>75 m²</strong>, inşaat <strong>150 m²</strong></li>
                      <li>İdari bina: taban <strong>75 m²</strong>, inşaat <strong>150 m²</strong></li>
                      <li>Kulüçkahane + civciv büyütme: kapalı alan kadar</li>
                      <li>Yem deposu: (kapalı alan + gezinti alanı)'nın yarısına kadar</li>
                    </ul>
                  </div>
                </div>
              </div>

              {/* 11.10 Gübre deposu */}
              <div className={styles.subsection}>
                <h3>11.10 Gübre Deposu (Çukuru)</h3>
                <div className={styles.info}>
                  <p>
                    Hayvancılık tesislerinde olması gereken gübre deposu/çukuru; <em>Nitrat Kirliliğine Karşı
                    Suların Korunması Yönetmeliği</em> ve <em>Nitrata Hassas Bölgelerin Belirlenmesi Tebliği
                    (2025/17)</em> kapsamında belirtilen ölçülerde, <strong>Ek-13 Gübre Deposu Hesaplama
                    Cetveli</strong>'ne uygun olarak yapılması zorunludur.
                  </p>
                </div>
              </div>
            </section>

            {/* MANDIRA VE DİĞERLERİ */}
            <section className={styles.section}>
              <h2>🥛 Mandıra, Un Değirmeni ve Diğer Yapılar</h2>
              <div className={styles.info}>
                <ul>
                  <li><strong>Mandıra:</strong> Büyükbaş/küçükbaş hayvancılık yapılan yerlerde işletme içi veya dışında yalnızca süt sağım ve soğutma yapılan tesis. Tarımsal amaçlı yapı olarak kabul edilir.</li>
                  <li><strong>Un değirmeni:</strong> Sanayi niteliği taşımayan, geleneksel yöntemlerle tarım ürünlerinin ezilerek un elde edildiği yapı.</li>
                  <li><strong>Tarımsal amaçlı teleferik:</strong> Bakanlık tarafından tarımsal amaçlı yapı olarak kabul edilir.</li>
                  <li><strong>Islım ünitesi:</strong> İlçe sınırları içinde üretilen hububat, çeltik, ceviz ve ayçiçeği ürünleri kurutma tesisi kapsamında değerlendirilir.</li>
                  <li><strong>Muz sarartma ünitesi:</strong> Bakanlık tarafından tarımsal amaçlı yapı olarak kabul edilir.</li>
                  <li><strong>Hayvan içme suyu göleti:</strong> Sulamaya yönelik altyapı tesisleri kapsamında tarımsal amaçlı yapı olarak kabul edilir.</li>
                  <li><strong>Tarımsal AR-GE tesisleri:</strong> Ürün işleme tesisleri hariç, AR-GE konusunda yetkili kamu kurumuna sunulacak proje kapsamında tarımsal AR-GE olduğu belirtilen tesisler.</li>
                </ul>
              </div>
            </section>

            {/* ARAZİ SINIFLARI ÖZET */}
            <section className={styles.section}>
              <h2>🗂️ Tarım Arazisi Sınıf Özeti</h2>
              <div className={styles.subsection}>
                <h3>MT — Mutlak Tarım Arazisi</h3>
                <div className={styles.info}>
                  <ul>
                    <li>Tesirli toprak derinliği <strong>en az 50 cm</strong></li>
                    <li>Eğim: yağış {'<'}574 mm ise max %3; yağış {'≥'}574 mm ise max %8</li>
                    <li>Yöre ortalaması ve üzerinde ürün alınabilen, münavebeye açık araziler</li>
                    <li>Sabit örtü altı yapılar mutlak tarım arazisi kategorisinde değerlendirilir</li>
                  </ul>
                </div>
              </div>
              <div className={styles.subsection}>
                <h3>OT — Özel Ürün Arazisi</h3>
                <div className={styles.info}>
                  <ul>
                    <li>MT'den fazla toprak ve topoğrafik sınırlamalara sahip</li>
                    <li>Yalnızca sınırlamalara uyum sağlayan bitkilerin tarımı yapılabilir</li>
                    <li>Eğim: yağış {'<'}574 mm ise max %8; yağış {'≥'}574 mm ise max %12</li>
                  </ul>
                </div>
              </div>
              <div className={styles.subsection}>
                <h3>DT — Dikili Tarım Arazisi</h3>
                <div className={styles.info}>
                  <ul>
                    <li>Ağaç, ağaççık ve çalı formunda bitkiler (bağ, çay, fındık, meyvelik, zeytin vb.)</li>
                    <li>Ekonomik ömrünü tamamlamış ve yenilenebilir olmayan dikili yerler dikili alan sayılmaz</li>
                  </ul>
                </div>
              </div>
              <div className={styles.subsection}>
                <h3>TA — Marjinal Tarım Arazisi</h3>
                <div className={styles.info}>
                  <ul>
                    <li>MT, OT ve DT dışında kalan, yerel ihtiyaçlarla tarıma açılmış araziler</li>
                    <li>Eğim: yağış {'<'}574 mm ise %8'den fazla; yağış {'≥'}574 mm ise %12'den fazla</li>
                    <li>Toprak derinliği 50 cm'den az, tarımsal üretim potansiyeli düşük</li>
                  </ul>
                </div>
              </div>
            </section>

            {/* Ana sayfaya dönüş */}
            <div style={{ textAlign: 'center', marginTop: 48 }}>
              <a href="/" style={{
                display: 'inline-block',
                background: 'linear-gradient(90deg, #d2691e, #8b4513)',
                color: '#fff',
                padding: '0.75rem 2.5rem',
                borderRadius: 8,
                fontWeight: 700,
                fontSize: '1.1rem',
                textDecoration: 'none',
                boxShadow: '0 2px 8px rgba(139,69,19,0.08)',
                transition: 'background 0.2s',
              }}
                onMouseOver={e => (e.currentTarget.style.background = 'linear-gradient(90deg, #8b4513, #d2691e)')}
                onMouseOut={e => (e.currentTarget.style.background = 'linear-gradient(90deg, #d2691e, #8b4513)')}
              >
                Ana Sayfaya Dön
              </a>
            </div>
          </div>
        </div>
      </Layout>
    </>
  );
}
