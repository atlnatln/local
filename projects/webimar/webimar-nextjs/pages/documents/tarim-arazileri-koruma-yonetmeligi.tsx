import Seo from '../../components/Seo';
import Layout from '../../components/Layout';
import styles from '../../styles/DocumentPage.module.css';

export default function TarimArazileriKorumaYonetmeligiPage() {
  return (
    <>
      <Seo
        title="Tarım Arazilerinin Korunması ve Kullanılması Hakkında Yönetmelik"
        description="5403 sayılı Kanun'a dayalı Tarım Arazilerinin Korunması ve Kullanılması Hakkında Yönetmelik — tarımsal amaçlı yapılar, arazi sınıflandırması, toprak koruma kurulu, izinlendirme usulleri ve cezai yaptırımlar"
        canonical="https://tarimimar.com.tr/documents/tarim-arazileri-koruma-yonetmeligi/"
        url="https://tarimimar.com.tr/documents/tarim-arazileri-koruma-yonetmeligi/"
        ogImage="https://tarimimar.com.tr/og-image.svg"
        type="article"
        keywords="tarım arazileri koruma yönetmelik, 5403 sayılı kanun yönetmelik, tarımsal amaçlı yapı izin, arazi sınıflandırma, toprak koruma kurulu, tarım dışı kullanım, büyük ova koruma"
      />
      <Layout>
        <div className={styles.container}>
          <div className={styles.header}>
            <h1>📜 Tarım Arazilerinin Korunması ve Kullanılması Hakkında Yönetmelik</h1>
            <p>5403 Sayılı Toprak Koruma ve Arazi Kullanımı Kanunu'na Dayanılarak Hazırlanmıştır</p>
          </div>

          <div className={styles.content}>

            {/* AMAÇ VE KAPSAM */}
            <section className={styles.section}>
              <h2>🎯 Amaç ve Kapsam (Madde 1)</h2>
              <div className={styles.highlight}>
                <p>
                  Bu Yönetmeliğin amacı; toprak ve arazi varlığının belirlenmesi, tarım arazilerinin
                  sınıflandırılması, geliştirilmesi, zorunlu hallerde amaç dışı kullanımına izin verilmesi,
                  toprağın korunması, toprak koruma projelerinin hazırlanması ve uygulanması, toprak koruma
                  kurulunun teşekkülü, görevleri ve çalışma kuralları ile çevre öncelikli sürdürülebilir
                  kalkınma ilkesine uygun olarak arazilerin planlı kullanımını sağlayacak usul ve esasları
                  belirlemektir.
                </p>
              </div>
              <div className={styles.info} style={{ marginTop: '1rem' }}>
                <p><strong>Kapsam dışı tutulan alanlar:</strong></p>
                <ul>
                  <li>6831 sayılı Orman Kanunu ve 4342 sayılı Mera Kanunu kapsamındaki alanlar</li>
                  <li>Tarım dışı alanlar, köy/kırsal yerleşik alanları ve çevresi</li>
                  <li>İmar planlarında tarımsal niteliği korunacak alan (TNKA) olarak ayrılan yerler</li>
                  <li>Planın yürürlükte olması şartıyla arsa vasfı kazanmış parseller</li>
                  <li>3573 sayılı Zeytinciliğin Islahı Kanunu kapsamındaki alanlar (o Kanunda bulunmayan hükümler yönünden uygulanır)</li>
                </ul>
              </div>
            </section>

            {/* TANIMLAR */}
            <section className={styles.section}>
              <h2>📝 Temel Tanımlar (Madde 3)</h2>
              <div className={styles.info}>
                <ul>
                  <li><strong>Aile:</strong> Karı-koca ve birlikte oturan reşit olmayan çocuklardan meydana gelen müessese</li>
                  <li><strong>Bağ evi:</strong> Tarımsal faaliyetin yapılması için ihtiyaç duyulan ve tarımsal üretimi artırıcı etkisi olan, doğal yapıyı bozmayacak şekilde inşa edilen yapı</li>
                  <li><strong>Mandıra:</strong> Büyükbaş/küçükbaş hayvancılık yapılan yerlerde işletme içi veya dışında yalnızca süt sağım ve soğutma yapılan tesis</li>
                  <li><strong>Sera:</strong> Kültür bitkilerinin üretildiği, ışık geçirebilen malzeme ile kaplı, toprağa/betona sabitlenmiş iskelet sistemiyle oluşan kapalı ortam bitkisel üretim ünitesi</li>
                  <li><strong>TAD Portal:</strong> Tarım Arazileri Değerlendirme ve Bilgilendirme Sistemi — izinlendirme sürecini tek merkezden yöneten sistem</li>
                  <li><strong>Tarımsal amaçlı entegre tesis:</strong> Tarımsal üretimden elde edilen ürünlerin birincil üretim aşamasından sonra fiziksel ve/veya kimyasal işleme tabi tutulacağı tesis</li>
                  <li><strong>Tarımsal arazi kullanım bütünlüğü:</strong> Tarım dışı kullanım talep edilen arazinin; planlı alana, karayoluna, köy/mahalle yoluna veya tarım dışı alana sınır dışı olmaması</li>
                  <li><strong>Un değirmeni:</strong> Sanayi niteliği taşımayan, geleneksel yöntemlerle tarım ürünlerinin ezilerek un elde edildiği yapı</li>
                </ul>
              </div>
            </section>

            {/* TARIMSAL AMAÇLI YAPILAR */}
            <section className={styles.section}>
              <h2>🏗️ Tarımsal Amaçlı Yapılar (Madde 4)</h2>
              <div className={styles.highlight}>
                <p>
                  Tarımsal amaçlı yapılar; toprak koruma ve sulamaya yönelik altyapı tesisleri, entegre
                  nitelikte olmayan hayvancılık ve su ürünleri üretim/muhafaza tesisleri ve müştemilatı,
                  mandıra, bitkisel ürün depoları, un değirmeni, sundurma ve çiftlik atölyeleri, seralar,
                  hasattan sonra 2 saat içinde işlenmesi gereken ürün tesisleri ile Bakanlık tarafından
                  tarımsal amaçlı olduğu kabul edilen entegre nitelikte olmayan diğer tesisler.
                </p>
              </div>
              <div className={styles.info} style={{ marginTop: '0.75rem' }}>
                <p><strong>Bakanlık kararıyla tarımsal amaçlı kabul edilen ek yapılar:</strong></p>
                <ul>
                  <li>İpek böcekçiliği üretim alanı</li>
                  <li>Hara (at üretimi/yetiştiriciliği)</li>
                  <li>Deve kuşu üretim tesisi</li>
                  <li>Tarımsal amaçlı depo (üreticinin bitkisel ürünü için)</li>
                  <li>Solucan ve solucan gübresi üretim tesisi</li>
                  <li>Yumru köklü bitkilerin yıkama tesisi</li>
                  <li>İlçe sınırlarındaki hububat/çeltik/ceviz/ayçiçeği kurutma tesisi</li>
                  <li>Islım ünitesi ve muz sarartma ünitesi</li>
                  <li>Hayvan içme suyu göleti</li>
                  <li>Tarımsal AR-GE tesisleri (yetkili kamu kurumuna proje sunulan)</li>
                  <li>Fide ve fidan üretim tesisleri</li>
                  <li>Tarımsal amaçlı teleferik</li>
                  <li>Bağ evi</li>
                  <li>Sahipsiz hayvan barınakları</li>
                  <li>Çatı GES ve sulama amaçlı GES</li>
                </ul>
                <p style={{ marginTop: '0.5rem' }}>
                  Bu yapıların dışında kalıp tarımsal üretime katkı sunacağı değerlendirilen tesisler de
                  Bakanlık tarafından tarımsal amaçlı yapı olarak kabul edilebilir.
                </p>
              </div>
              <div className={styles.warning} style={{ marginTop: '0.75rem' }}>
                <ul>
                  <li>Tarımsal amaçlı yapılarda <strong>tarımsal arazi kullanım bütünlüğü aranmaz</strong></li>
                  <li>Yapı taleplerinin değerlendirilmesinde <strong>Ek-1'deki kriterler (Talimat)</strong> esas alınır</li>
                  <li>İzinlendirilen yapının projesine uygun yapılması, amaç dışı kullanılmaması, arsaya dönüştürülmemesi zorunludur; ihlalde izin iptal edilir</li>
                  <li>Talep sahibi noter onaylı taahhütname (Ek-7), proje teknik raporu (Ek-16), tarımsal GES taahhütnamesi (Ek-14), muvafakatname (Ek-17) sunar; hayvancılıkta gübre depo hesap tablosu (Ek-13) kullanılır</li>
                </ul>
              </div>
            </section>

            {/* BAŞVURU USULLERİ */}
            <section className={styles.section}>
              <h2>📋 Arazi Kullanım Taleplerinin Yapılması (Madde 5)</h2>
              <div className={styles.info}>
                <ul>
                  <li>İmar planları ve köy yerleşik alanı çalışmaları: planlama öncesinde <strong>TAD Portal</strong> üzerinden il müdürlüğüne başvurulur</li>
                  <li>Gerçek/tüzel kişi talepleri: belediye sınırları içinde belediyelere, dışında il özel idarelerine başvurulur; bunlar TAD Portal üzerinden il müdürlüğüne iletir</li>
                  <li>Madencilik, yenilenebilir enerji, elektrik iletim hatları vb. plan zorunluluğu olmayan yatırımlar: TAD Portal üzerinden doğrudan il müdürlüğüne</li>
                  <li>Başvurularda <strong>yetki belgeleri</strong> dosyayla birlikte sunulması zorunludur</li>
                </ul>
              </div>
            </section>

            {/* ARAZİ ETÜDÜ */}
            <section className={styles.section}>
              <h2>🔍 Arazi Etüt Raporlarının Hazırlanması ve Sınıflandırılması (Madde 6)</h2>
              <div className={styles.info}>
                <ul>
                  <li>En az iki <strong>hizmet içi eğitimli ziraat mühendisi</strong> tarafından Ek-3 formatına uygun olarak TAD Portal üzerinden hazırlanır</li>
                  <li>Raporda alternatif alanlar haritalı gösterilir; toprak koruma projesi gerekip gerekmediği açıkça belirtilir</li>
                  <li>İlgili şube müdürünce kontrol edilir, il müdürü tarafından onaylanır</li>
                  <li>Arazinin doğal durumu tamamen bozulmuşsa, komşu araziden ve Bakanlık veri tabanından yararlanılarak etüt yapılır</li>
                  <li><strong>GES için:</strong> Arazi sınıfının <em>kuru marjinal tarım arazisi</em> olması zorunludur; diğer arazi sınıflarındaki GES talepleri Kurul gündemine alınmaz</li>
                  <li>Dikili tarım arazisi tespitinde Ek-4'teki ağaç sayısı normları esas alınır (zeytin sayısı 3573 sayılı Kanun kapsamında ayrıca değerlendirilir)</li>
                  <li>Dikili tarım arazisi vasfı kazanmış ve 5 yıl dolmamış ise toprak, topoğrafik, verim veya mücbir sebep dışında sınıf değiştirilemez</li>
                </ul>
              </div>
            </section>

            {/* ALTERNATİF ALAN */}
            <section className={styles.section}>
              <h2>🗺️ Alternatif Alan ve Tarımsal Arazi Kullanım Bütünlüğü (Madde 9)</h2>
              <div className={styles.info}>
                <ul>
                  <li>Tarım arazileri arazi kullanım planlarında belirtilen amaçları dışında kullanılamaz</li>
                  <li>Alternatif alan araştırması talebin yapıldığı köy/kırsal mahalle sınırları içinde yapılır</li>
                  <li><strong>Alternatif alan aranmayan durumlar:</strong>
                    <ul>
                      <li>1. grup maden dışındaki madenler, jeotermal kaynaklar, petrol</li>
                      <li>Yenilenebilir enerji santralleri ve depolama tesisleri, bunlara ait yol, trafo, şalt, iletim</li>
                      <li>Su deposu, arıtma tesisi, içme suyu hattı talepleri</li>
                    </ul>
                  </li>
                  <li>Büyük ova alanlarında büyük ova dışındaki alanlar her zaman alternatif alan sayılır</li>
                  <li>Tarımsal amaçlı yapılarda önce ova dışı arazi ve organize sanayi bölgelerinden karşılanması esastır</li>
                </ul>
              </div>
            </section>

            {/* TOPRAK KORUMA KURULU */}
            <section className={styles.section}>
              <h2>🏛️ Toprak Koruma Kurulunun Teşekkülü ve Görevleri (Madde 10–12)</h2>
              <div className={styles.info}>
                <p>Her ilde valinin başkanlığında oluşur; üyeler:</p>
                <ul>
                  <li>Başkan yardımcısı olarak il müdürü</li>
                  <li>Hazine ve Maliye Bakanlığı üst düzey temsilcisi</li>
                  <li>Büyükşehir belediyesi / il belediyesi / il özel idaresi ve üniversite temsilcileri (3 üye)</li>
                  <li>Sivil toplum kuruluşları, TOBB/Ziraat Odaları, TMMOB/ZMO (3 üye)</li>
                  <li>Toplam: Ek-6 listesine uygun <strong>en az 9 üye</strong></li>
                </ul>
                <p style={{ marginTop: '0.5rem' }}><strong>Toplanma:</strong> Ayda en az 1 olağan toplantı; toplantı için en az 6 üye, karar için en az 6 olumlu oy gerekir.</p>
                <p><strong>Tarımsal amaçlı yapı talepleri:</strong> Büyük ova dışındaki tarımsal amaçlı yapılar ve kuru marjinal arazi için gerçek/tüzel kişi talepleri Kurul gündemine alınmaz; valilikler tarafından değerlendirilerek sonuçlandırılır.</p>
              </div>
            </section>

            {/* ARazi KULLANIM ESASI */}
            <section className={styles.section}>
              <h2>⚖️ Tarım Dışı Kullanım İzni (Madde 13–14)</h2>
              <div className={styles.warning}>
                <p><strong>Mutlak, özel ürün, dikili ve sulu tarım arazilerinde</strong> aşağıdaki faaliyetler için; alternatif alan bulunmaması ve Kurul uygun görüşü şartıyla Bakanlık izin verebilir:</p>
                <ul>
                  <li>Savunmaya yönelik stratejik ihtiyaçlar</li>
                  <li>Doğal afet sonrası geçici yerleşim yeri</li>
                  <li>Petrol ve doğal gaz arama/işletme</li>
                  <li>Kamu yararı kararı alınmış madencilik faaliyetleri</li>
                  <li>Kamu yararı kararı alınmış plan ve yatırımlar</li>
                  <li>Yol, altyapı ve üstyapı faaliyetleri</li>
                  <li>EPDK/6446 sayılı Kanun kapsamındaki yenilenebilir enerji yatırımları</li>
                  <li>Jeotermal kaynaklı teknolojik sera yatırımları</li>
                </ul>
              </div>
              <div className={styles.info} style={{ marginTop: '0.75rem' }}>
                <p><strong>Tarımsal amaçlı yapılar:</strong> Arazi niteliklerine ve sınıfına bakılmaksızın, alternatif alan ve tarımsal kullanım bütünlüğü aranmaksızın, <em>toprak koruma projesine uyulması şartıyla</em> valilikçe izin verilebilir.</p>
                <p><strong>Kuru marjinal arazi:</strong> Çevre arazilerdeki tarımsal kullanım bütünlüğünü bozmamak ve toprak koruma projesine uymak koşuluyla Kurul görüşü aranmaksızın valilikçe tarım dışı kullanım izni verilebilir.</p>
              </div>
            </section>

            {/* BÜYÜK OVA */}
            <section className={styles.section}>
              <h2>🌾 Büyük Ovalarda Tarım Arazilerinin Amaç Dışı Kullanımı (Madde 15)</h2>
              <div className={styles.warning}>
                <p>Büyük ova koruma alanı olarak belirlenen alanlardaki tarım arazileri <strong>hiçbir surette</strong> amaç dışı kullanılamaz. Yalnızca iki istisnada alternatif alan bulunmaması ve Kurul/Kurullar uygun görüşü şartıyla Bakanlıkça izin verilebilir:</p>
                <ol>
                  <li>Tarımsal amaçlı yapılar</li>
                  <li>İlgili Bakanlık ile ortaklaşa kamu yararı kararı alınmış faaliyetler</li>
                </ol>
                <p style={{ marginTop: '0.5rem' }}>Büyük ova ilanından önce onaylı imar planları içinde kalan alanlar ve önceden izin alınmış talepler bu madde kapsamında değerlendirilmez.</p>
              </div>
            </section>

            {/* GENEL HÜKÜMLER */}
            <section className={styles.section}>
              <h2>📌 Genel Hükümler — İzin Geçerlilik ve Tamamlama (Madde 16)</h2>
              <div className={styles.info}>
                <ul>
                  <li>Arazi kullanım izinleri tebliğden itibaren <strong>2 yıl içinde</strong> ruhsata/plana bağlanmazsa geçersiz sayılır (sera, bağ evi, maden ocağı, enerji nakil hattı gibi plan/ruhsat zorunluluğu olmayan onaylar için de bu süre geçerlidir)</li>
                  <li>İmar planlarındaki Tarımsal Niteliği Korunacak Alanlar (TNKA): izinsiz tarımsal üretim dışı kullanım yapılamaz, ifraz edilemez, yol geçirilemez, plan değişikliğinde Bakanlık izni zorunludur</li>
                  <li>Çevre düzeni planlarına dayalı olarak tarım dışı kullanım izni verilmez; Bakanlık onaylı AKUP haritası altlık olarak sunulur</li>
                  <li>Eksik belgeler: kamu kurumlarından alınacak belgeler <strong>6 ay</strong>, diğerleri <strong>3 ay</strong> içinde tamamlanır; süre dolunca başvuru iade edilir</li>
                </ul>
              </div>
            </section>

            {/* TOPRAK KORUMA PROJESİ */}
            <section className={styles.section}>
              <h2>🔨 Toprak Koruma Projeleri (Madde 17)</h2>
              <div className={styles.info}>
                <ul>
                  <li>Kazı veya dolgu gerektiren arazi kullanımında çevredeki tarım arazilerinde toprak yapısının bozulması veya erozyon riski varsa zorunludur</li>
                  <li>En az bir <strong>ziraat mühendisi</strong> (toprak koruma sertifikası veya Tüzük yetkisiyle) sorumluluğunda Ek-9 dispozisyonuna uygun hazırlanır</li>
                  <li>Projeler; sekileme, çevirme, koruma duvarı, bitkilendirme, arıtma, drenaj gibi tedbirleri içerir</li>
                  <li>Proje hazırlanmaması veya yetersizliği sonucu oluşan zararlardan karar verenler ve projeyi hazırlayan/onaylayanlar sorumludur</li>
                </ul>
              </div>
            </section>

            {/* İTİRAZ */}
            <section className={styles.section}>
              <h2>📣 İtiraz, Denetim ve İdari Yaptırımlar (Madde 18–22)</h2>
              <div className={styles.subsection}>
                <h3>İtiraz (Madde 18)</h3>
                <div className={styles.info}>
                  <ul>
                    <li>Verilen kararlara <strong>bir defaya mahsus</strong> itiraz edilebilir</li>
                    <li>Kararın tebliğinden itibaren <strong>1 yıl içinde</strong> valiliklere yapılır; Bakanlık inceler ve kesin karar verir</li>
                    <li>Olumsuz karara karşı gerekçeli rapor veya kamu kurumu belgesi sunulması halinde yeniden inceleme yapılabilir</li>
                  </ul>
                </div>
              </div>
              <div className={styles.subsection}>
                <h3>Denetim (Madde 20)</h3>
                <div className={styles.info}>
                  <ul>
                    <li>Denetim Bakanlık, valilikler veya kurullar tarafından yapılır</li>
                    <li>Aykırılık tespitinde <strong>7 gün içinde</strong> tapu kütüğünün beyanlar hanesine "5403 sayılı Kanunun amacı dışında kullanılmıştır" şeklinde belirtme yapılır</li>
                    <li>Aykırılığın giderildiğine dair Bakanlık/valilik bildirimi olmadan belirtme terkin edilmez</li>
                  </ul>
                </div>
              </div>
              <div className={styles.subsection}>
                <h3>İdari Yaptırımlar (Madde 22)</h3>
                <div className={styles.warning}>
                  <ul>
                    <li>İzinsiz başlanılan yapı inşaat halinde ise <strong>valilik işi durdurur</strong>; tamamlanmışsa kullanıma izin verilmez</li>
                    <li>İdari para cezası uygulanır (5403 Md. 21)</li>
                    <li>Ceza tebliğinden itibaren <strong>1 ay içinde</strong> izin başvurusu yapılarak işin tamamlanmasına izin verilebilir; başvuru yapmayana <strong>2 ay içinde yıkım</strong> zorunluluğu getirilir</li>
                    <li>2 aylık süre dolunca yıkılmayan yapılar için <strong>3 kat idari para cezası</strong> uygulanır</li>
                    <li>Belediye veya il özel idaresi yıkımı 1 ay içinde yapar; masraflar %100 fazlasıyla tahsil edilir</li>
                    <li>Tescili mümkün olmayan fiili hisselerle arazinin bütünlüğünü bozanlara <strong>Cumhuriyet Başsavcılığına</strong> suç duyurusunda bulunulur</li>
                  </ul>
                </div>
              </div>
            </section>

            {/* YÜRÜRLÜK */}
            <section className={styles.section}>
              <h2>⚖️ Yürürlük ve Dayanak (Madde 24–26)</h2>
              <div className={styles.info}>
                <ul>
                  <li>Bu Yönetmelik; <strong>9/12/2017 tarihli ve 30265 sayılı</strong> Resmî Gazete'de yayımlanan Tarım Arazilerinin Korunması, Kullanılması ve Planlanmasına Dair Yönetmeliği <strong>yürürlükten kaldırmıştır</strong></li>
                  <li>Dayanağı: 5403 sayılı Kanunun 7, 12, 13, 14, 21 ve 24. maddeleri</li>
                  <li>Yürürlük: Yayımı tarihinde</li>
                  <li>Yürütme: Tarım ve Orman Bakanı</li>
                </ul>
              </div>
            </section>

            {/* Dönüş */}
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
