import Head from 'next/head';
import Seo from '../../components/Seo';
import Layout from '../../components/Layout';
import styles from '../../styles/DocumentPage.module.css';

export default function ToprakKorumaKanumuPage() {
  return (
    <>
      <Seo
        title="Toprak Koruma ve Arazi Kullanımı Kanunu - 5403 Sayılı Kanun"
        description="5403 sayılı Toprak Koruma ve Arazi Kullanımı Kanunu - Tarım arazilerinin korunması, sınıflandırılması ve amaç dışı kullanım yasakları hakkında detaylı bilgi"
        canonical="https://tarimimar.com.tr/documents/toprak-koruma-kanunu/"
        url="https://tarimimar.com.tr/documents/toprak-koruma-kanunu/"
        ogImage="https://tarimimar.com.tr/og-image.svg"
        type="article"
        keywords="toprak koruma kanunu, 5403 sayılı kanun, tarım arazileri, arazi kullanımı, toprak sınıflandırılması, tarım mevzuatı, büyük ovalar"
      />
      <Layout>
        <div className={styles.container}>
          <div className={styles.header}>
            <h1>🌱 Toprak Koruma ve Arazi Kullanımı Kanunu</h1>
            <p>Resmî Gazete Tarihi: 19.07.2005 | Resmî Gazete Sayısı: 25880 | 5403 Sayılı Kanun</p>
          </div>

          <div className={styles.content}>
            <section className={styles.section}>
              <h2>🎯 Kanunun Amacı</h2>
              <div className={styles.highlight}>
                <p>Bu Kanunun amacı; toprağın korunması, geliştirilmesi, tarım arazilerinin sınıflandırılması, asgari tarımsal arazi ve yeter gelirli tarımsal arazi büyüklüklerinin belirlenmesi ve bölünmelerinin önlenmesi, tarımsal arazi ve yeter gelirli tarımsal arazilerin çevre öncelikli sürdürülebilir kalkınma ilkesine uygun olarak planlı kullanımını sağlayacak usul ve esasları belirlemektir.</p>
              </div>
            </section>

            <section className={styles.section}>
              <h2>📝 Temel Tanımlar</h2>
              
              <div className={styles.subsection}>
                <h3>🌾 Tarım Arazisi</h3>
                <div className={styles.info}>
                  <p>Toprak, topografya ve iklimsel özellikleri tarımsal üretim için uygun olup, hâlihazırda tarımsal üretim yapılan veya yapılmaya uygun olan veya imar, ihya, ıslah edilerek tarımsal üretim yapılmaya uygun hale dönüştürülebilen araziler</p>
                </div>
              </div>

              <div className={styles.subsection}>
                <h3>🥇 Mutlak Tarım Arazisi</h3>
                <div className={styles.info}>
                  <p>Bitkisel üretimde; toprağın fiziksel, kimyasal ve biyolojik özelliklerinin kombinasyonu yöre ortalamasında ürün alınabilmesi için sınırlayıcı olmayan, topografik sınırlamaları yok veya çok az olan; ülkesel, bölgesel veya yerel önemi bulunan, hâlihazır tarımsal üretimde kullanılan veya bu amaçla kullanıma elverişli olan araziler</p>
                </div>
              </div>

              <div className={styles.subsection}>
                <h3>🌸 Özel Ürün Arazisi</h3>
                <div className={styles.info}>
                  <p>Mutlak tarım arazileri dışında kalan, toprak ve topografik sınırlamaları nedeniyle yöreye adapte olmuş bitki türlerinin tamamının tarımının yapılamadığı ancak özel bitkisel ürünlerin yetiştiriciliği ile su ürünleri yetiştiriciliğinin ve avcılığının yapılabildiği, ülkesel, bölgesel veya yerel önemi bulunan araziler</p>
                </div>
              </div>

              <div className={styles.subsection}>
                <h3>🌳 Dikili Tarım Arazisi</h3>
                <div className={styles.info}>
                  <p>Mutlak ve özel ürün arazileri dışında kalan ve üzerinde yöre ekolojisine uygun çok yıllık ağaç, ağaççık ve çalı formundaki bitkilerin tarımı yapılan, ülkesel, bölgesel veya yerel önemi bulunan araziler</p>
                </div>
              </div>

              <div className={styles.subsection}>
                <h3>🏔️ Marjinal Tarım Arazisi</h3>
                <div className={styles.info}>
                  <p>Mutlak tarım arazileri, özel ürün arazileri ve dikili tarım arazileri dışında kalan, toprak ve topografik sınırlamalar nedeniyle üzerinde sadece geleneksel toprak işlemeli tarımın yapıldığı araziler</p>
                </div>
              </div>

              <div className={styles.subsection}>
                <h3>💧 Sulu Tarım Arazisi</h3>
                <div className={styles.info}>
                  <p>Tarımı yapılan bitkilerin büyüme devresinde ihtiyaç duyduğu suyun, su kaynağından alınarak yeterli miktarda ve kontrollü bir şekilde karşılandığı araziler</p>
                </div>
              </div>

              <div className={styles.subsection}>
                <h3>🏗️ Tarımsal Amaçlı Yapılar</h3>
                <div className={styles.info}>
                  <p>Toprak koruma ve sulamaya yönelik altyapı tesisleri, entegre nitelikte olmayan hayvancılık ve su ürünleri üretim ve muhafaza tesisleri ile zorunlu olarak tesis edilmesi gerekli olan müştemilatı, mandıra, üreticinin bitkisel üretime bağlı olarak elde ettiği ürünü için ihtiyaç duyacağı yeterli boyut ve hacimde depolar, un değirmeni, tarım alet ve makinelerinin muhafazasında kullanılan sundurma ve çiftlik atölyeleri, seralar, tarımsal işletmede üretilen ürünün özelliği itibarıyla hasattan sonra iki saat içinde işlenmediği takdirde ürünün kalite ve besin değeri kaybolması söz konusu ise bu ürünlerin işlenmesi için kurulan tesisler ile Bakanlık tarafından tarımsal amaçlı olduğu kabul edilen entegre nitelikte olmayan diğer tesisler</p>
                </div>
              </div>
            </section>

            <section className={styles.section}>
              <h2>📏 Asgari Tarımsal Arazi Büyüklüğü</h2>
              
              <div className={styles.subsection}>
                <div className={styles.highlight}>
                  <p>Asgari tarımsal arazi büyüklüğü:</p>
                  <ul>
                    <li>Mutlak tarım arazileri, marjinal tarım arazileri ve özel ürün arazilerinde <strong>2 hektar</strong></li>
                    <li>Dikili tarım arazilerinde <strong>0,5 hektar</strong></li>
                    <li>Örtü altı tarımı yapılan arazilerde <strong>0,3 hektar</strong></li>
                  </ul>
                  <p><strong>Tarım arazileri belirlenen büyüklüklerin altında ifraz edilemez, hisselendirilemez.</strong></p>
                </div>
              </div>

              <div className={styles.subsection}>
                <h3>⚡ İstisnalar</h3>
                <div className={styles.info}>
                  <ul>
                    <li>Tarım dışı kullanım izni verilen alanlar</li>
                    <li>Çay, fındık, zeytin gibi özel iklim ve toprak ihtiyaçları olan bitkilerin yetiştiği alanlarda Bakanlığın uygun görüşü ile daha küçük parseller oluşturulabilir</li>
                    <li>Yatırım programında yer alan kamu yatırımı projeleri</li>
                  </ul>
                </div>
              </div>
            </section>

            <section className={styles.section}>
              <h2>🛡️ Toprak Koruma Projeleri</h2>
              
              <div className={styles.subsection}>
                <div className={styles.highlight}>
                  <p><strong>Toprağın bulunduğu yerde, doğal fonksiyonlarını sürdürebilmesinin sağlanması amacıyla korunması esastır.</strong></p>
                </div>
              </div>

              <div className={styles.subsection}>
                <h3>📋 Proje Kapsamı</h3>
                <div className={styles.info}>
                  <p>Toprak koruma projeleri arazi bozulmalarını ve toprak kayıplarını önlemek için gerekli olan:</p>
                  <ul>
                    <li>Sekileme, çevirme, koruma duvarı</li>
                    <li>Bitkilendirme</li>
                    <li>Arıtma, drenaj</li>
                    <li>Diğer imalat, inşaat ve kültürel tedbirleri içerir</li>
                  </ul>
                  <p><strong>En az bir ziraat mühendisi sorumluluğunda hazırlanır ve valilik tarafından onaylanır.</strong></p>
                </div>
              </div>
            </section>

            <section className={styles.section}>
              <h2>🚫 Tarım Arazilerinin Amaç Dışı Kullanımı</h2>
              
              <div className={styles.subsection}>
                <div className={styles.highlight}>
                  <p><strong>Mutlak tarım arazileri, özel ürün arazileri, dikili tarım arazileri ile sulu tarım arazileri tarımsal üretim amacı dışında kullanılamaz.</strong></p>
                </div>
              </div>

              <div className={styles.subsection}>
                <h3>⚡ İstisnai Durumlar</h3>
                <div className={styles.warning}>
                  <p>Alternatif alan bulunmaması ve Kurulun uygun görmesi şartıyla:</p>
                  <ol>
                    <li>Savunmaya yönelik stratejik ihtiyaçlar</li>
                    <li>Doğal afet sonrası ortaya çıkan geçici yerleşim yeri ihtiyacı</li>
                    <li>Petrol ve doğal gaz arama ve işletme faaliyetleri</li>
                    <li>İlgili bakanlık tarafından kamu yararı kararı alınmış madencilik faaliyetleri</li>
                    <li>Bakanlıklarca kamu yararı kararı alınmış plân ve yatırımlar</li>
                    <li>Kamu yararı gözetilerek yol altyapı ve üstyapısı faaliyetlerinde bulunacak yatırımlar</li>
                    <li>EPDK talebi üzerine yenilenebilir enerji kaynak alanlarının kullanımı ile ilgili yatırımları</li>
                    <li>Jeotermal kaynaklı teknolojik sera yatırımları</li>
                  </ol>
                  <p><strong>Bu durumlar için toprak koruma projelerine uyulması kaydı ile Bakanlık tarafından izin verilebilir.</strong></p>
                </div>
              </div>

              <div className={styles.subsection}>
                <h3>🌿 Marjinal Tarım Arazileri</h3>
                <div className={styles.info}>
                  <p>Mutlak tarım arazileri, özel ürün arazileri, dikili tarım arazileri ile sulu tarım arazileri dışında kalan tarım arazileri; <strong>toprak koruma projelerine uyulması kaydı ile valilikler tarafından tarım dışı kullanımlara tahsis edilebilir</strong>.</p>
                </div>
              </div>

              <div className={styles.subsection}>
                <h3>🏗️ Tarımsal Amaçlı Yapılar</h3>
                <div className={styles.info}>
                  <p><strong>Tarımsal amaçlı yapılar için, projesine uyulması şartıyla ihtiyaç duyulan miktarda her sınıf ve özellikteki tarım arazisi valilik izni ile kullanılır.</strong></p>
                </div>
              </div>
            </section>

            <section className={styles.section}>
              <h2>🌾 Büyük Ovaların Korunması</h2>
              
              <div className={styles.subsection}>
                <div className={styles.highlight}>
                  <p><strong>Büyük ovalarda bulunan tarım arazileri hiçbir surette amacı dışında kullanılamaz.</strong></p>
                </div>
              </div>

              <div className={styles.subsection}>
                <h3>⚡ Sınırlı İstisnalar</h3>
                <div className={styles.warning}>
                  <p>Alternatif alan bulunmaması, kurul veya kurullarca uygun görüş bildirilmesi şartıyla:</p>
                  <ul>
                    <li>Tarımsal amaçlı yapılar</li>
                    <li>Bakanlık ve talebin ilgili olduğu Bakanlıkça ortaklaşa kamu yararı kararı alınmış faaliyetler</li>
                  </ul>
                  <p><strong>Bu durumlar için tarım dışı kullanımlara Bakanlıkça izin verilebilir.</strong></p>
                </div>
              </div>
            </section>

            <section className={styles.section}>
              <h2>⚖️ Cezalar ve Yükümlülükler</h2>
              
              <div className={styles.subsection}>
                <div className={styles.warning}>
                  <p>Tarım arazilerinin tarımsal amaçlı kullanımına dair yapılan plan ve projelere uymak zorunludur:</p>
                  <ul>
                    <li>Aykırı kullanım tespitinde valilik tarafından ceza uygulanır</li>
                    <li>Arazi sahibine düzeltilmesi için iki aya kadar süre verilir</li>
                    <li>Büyük ova koruma alanlarında para cezası iki katına çıkar</li>
                    <li>Süre sonunda aykırılık devam ederse faaliyet durdurulur ve para cezası üç katına çıkarılır</li>
                    <li>İzinsiz yapılar yıkılır ve arazi tekrar tarımsal üretime uygun hale getirilir</li>
                  </ul>
                </div>
              </div>

              <div className={styles.subsection}>
                <h3>📅 Mevcut Haklar</h3>
                <div className={styles.info}>
                  <p><strong>19/7/2005 tarihinden önce onaylanmış 1/5000 veya 1/1000 ölçekli imar planları veya arsa vasfı kazanmış parseller ile bu maddenin yürürlüğe girdiği tarihten önce belirlenen onaylı köy ve/veya mezraların yerleşik alanı ve civarı ile yerleşik alanlar izinli kabul edilir.</strong></p>
                </div>
              </div>
            </section>

            <section className={styles.section}>
              <h2>📚 Hukuki Dayanak</h2>
              <div className={styles.subsection}>
                <p><em>Bu kanun, 3/7/2005 tarihinde TBMM tarafından kabul edilmiş olup, 19/7/2005 tarihli Resmî Gazete'de yayımlanarak yürürlüğe girmiştir.</em></p>
              </div>
            </section>

            {/* Ana sayfaya dönüş butonu */}
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
