import Head from 'next/head';
import Seo from '../../components/Seo';
import Layout from '../../components/Layout';
import styles from '../../styles/DocumentPage.module.css';

export default function TarimArazileriKullanimiGenelgesiPage() {
  return (
    <>
      <Seo
        title="Tarım Arazileri Kullanımı Genelgesi - Bağ Evi ve Yapılaşma Koşulları"
        description="5403 sayılı Kanun'a dayalı Tarım Arazilerinin Korunması Genelgesi - Bağ evi, sera, hayvancılık tesisi yapılaşma koşulları ve izin süreçleri"
        canonical="https://tarimimar.com.tr/documents/tarim-arazileri-kullanimi-genelgesi/"
        url="https://tarimimar.com.tr/documents/tarim-arazileri-kullanimi-genelgesi/"
        ogImage="https://tarimimar.com.tr/og-image.svg"
        type="article"
        keywords="tarım arazileri genelgesi, bağ evi koşulları, sera yapılaşma, hayvancılık tesisi, tarım mevzuatı, toprak koruma, arazi kullanımı"
      />
      <Layout>
        <div className={styles.container}>
          <div className={styles.header}>
            <h1>📋 Tarım Arazileri Kullanımı Genelgesi</h1>
            <p>5403 sayılı Toprak Koruma ve Arazi Kullanımı Kanunu'na Dayalı Genelge</p>
          </div>

          <div className={styles.content}>
            <section className={styles.section}>
              <h2>📋 Genelgenin Dayanağı</h2>
              <div className={styles.highlight}>
                <p>Bu Genelge, 3.7.2005 tarihli ve 5403 sayılı Toprak Koruma ve Arazi Kullanımı Kanunu ile 9.12.2017 tarihli ve 30265 sayılı Resmi Gazete'de yayımlanarak yürürlüğe giren Tarım Arazilerinin Korunması, Kullanılması ve Planlanmasına Dair Yönetmeliğin 23 üncü maddesine dayanılarak hazırlanmıştır.</p>
              </div>
            </section>

            <section className={styles.section}>
              <h2>📝 Tanımlar</h2>
              
              <div className={styles.subsection}>
                <div className={styles.info}>
                  <ul>
                    <li><strong>Aile:</strong> Karı - Koca ve birlikte oturan reşit olmayan çocuklardan meydana gelen müessese</li>
                    <li><strong>Avan proje:</strong> Başvuru konusu olan tesise ait vaziyet planı ile tesisin ihtiyaçlarına göre elde edilen verilere dayanılarak hazırlanan plan ve kesitlerin yer aldığı proje</li>
                    <li><strong>Bağ evi:</strong> Tarımsal faaliyetin yapılması için ihtiyaç duyulan barınmayı sağlayacak ve izin verilmesi halinde tarımsal üretimi artırıcı etkisi olan yapı</li>
                    <li><strong>Bakanlık:</strong> Tarım ve Orman Bakanlığı</li>
                    <li><strong>İl Müdürlüğü:</strong> İl Tarım ve Orman Müdürlüğü</li>
                    <li><strong>Kanun:</strong> 5403 sayılı Toprak Koruma ve Arazi Kullanımı Kanunu</li>
                    <li><strong>Kurul:</strong> İl Toprak Koruma Kurulu</li>
                    <li><strong>Yönetmelik:</strong> 9.12.2017 tarihli ve 30265 sayılı Resmi Gazete'de yayımlanarak yürürlüğe giren Tarım Arazilerinin Korunması, Kullanılması ve Planlanmasına Dair Yönetmelik</li>
                  </ul>
                </div>
              </div>
            </section>

            <section className={styles.section}>
              <h2>🏗️ İmar ve Yapılaşma Düzenlemeleri</h2>
              
              <div className={styles.subsection}>
                <h3>🏠 Bağ Evi Yapılaşma Koşulları</h3>
                <div className={styles.highlight}>
                  <h4>📏 Arazi Büyüklüğü Koşulları</h4>
                  <ul>
                    <li>Yüzölçümü <strong>5 hektar ve üzeri</strong> olan mutlak, özel ürün ve marjinal tarım arazisi</li>
                    <li>Yüzölçümü <strong>1 hektar ve üzeri</strong> olan dikili tarım arazisi</li>
                    <li><strong>0,3 hektar ve üzeri</strong> örtüaltı tarım arazisi</li>
                  </ul>
                  
                  <h4>🏘️ Yapılaşma Koşulları</h4>
                  <ul>
                    <li>Taban alanı: <strong>En fazla 30 metrekare</strong></li>
                    <li>Toplam inşaat alanı: <strong>En fazla 60 metrekare</strong></li>
                  </ul>

                  <h4>⚠️ Sınırlamalar ve Özel Durumlar</h4>
                  <ul>
                    <li>Kiralanan arazilere kiracılar tarafından bağ evi talebi yapılamaz</li>
                    <li>Her aile için aynı ilçe sınırları içerisinde <strong>sadece bir adet</strong> bağ evi izni verilebilir</li>
                    <li>Parselin hisseli olması durumunda diğer hissedarlardan muvafakatname alınması zorunludur</li>
                    <li>Alt katı tarımsal amaçlı depo üstü bağ evi taleplerinde, toplam arazi varlığının %1'i kadar tarımsal amaçlı depo üstü 30 metrekare bağ evi yapılabilir</li>
                  </ul>
                </div>
              </div>

              <div className={styles.subsection}>
                <h3>🌱 Sera Yapılaşma Koşulları</h3>
                <div className={styles.info}>
                  <ul>
                    <li>Asgari tarımsal arazi büyüklüğü (0,3 hektar) ve üzerindeki sera taleplerinde, sera ve müştemilatı ile birlikte bakıcı evi talebi olması durumunda birlikte yapılmasına izin verilebilir</li>
                    <li>Yapılmış veya yapılacak seralarda <strong>20 metrekareden az olmamak şartıyla</strong>, taban alanı sera alanının <strong>%5'ine kadar</strong> yapılan idari ve teknik bina tarımsal amaçlı yapı olarak kabul edilir</li>
                    <li>Sera üzerine GES tesisleri bitkisel üretim tekniği açısından uygun görülmemektedir</li>
                    <li>Marjinal tarım arazisinde proje alanının en fazla <strong>%1,5'ine zemine GES</strong> kurulmasına izin verilebilir</li>
                  </ul>
                </div>
              </div>

              <div className={styles.subsection}>
                <h3>🐄 Hayvancılık Tesislerine İlişkin Yapılaşma Koşulları</h3>
                <div className={styles.warning}>
                  <h4>🏢 Hayvan Başına Kapalı Alan Gereksinimleri</h4>
                  <ul>
                    <li><strong>Büyükbaş hayvanlar:</strong> Ahır ve yem deposunun toplam alanı hayvan başına 15 metrekare</li>
                    <li><strong>Süt hayvanları:</strong> Ahır dışında açık gezinti alanı hayvan başına 7 metrekare</li>
                    <li><strong>Küçükbaş hayvanlar:</strong> Ağıl ve yem deposunun toplam alanı hayvan başına 3 metrekare</li>
                  </ul>

                  <h4>🐔 Kanatlı Hayvan Üretiminde 1 Metrekare Alanda</h4>
                  <ul>
                    <li>Etçi tavuklar: <strong>14-18 adet</strong></li>
                    <li>Yumurtacı tavuklar: <strong>6-8 adet</strong></li>
                    <li>Hindi: <strong>3-4 adet</strong></li>
                    <li>Kaz: <strong>2-3 adet</strong></li>
                    <li>Gezen tavuk: <strong>4-6 adet</strong> (1 tavuk için 2 metrekare gezinti alanı)</li>
                  </ul>

                  <h4>🏠 Bakıcı Evi Yapılabilecek Tesis Büyüklükleri</h4>
                  <ul>
                    <li>Süt sığırcılığı: <strong>25 baş ve üzeri</strong></li>
                    <li>Besi sığırcılığı: <strong>50 baş ve üzeri</strong></li>
                    <li>Koyun keçi yetiştiriciliği: <strong>150 baş ve üzeri</strong></li>
                    <li>Yumurta tavukçuluğu: <strong>7500 adet ve üzeri</strong></li>
                    <li>Broiler: <strong>10000 adet ve üzeri</strong></li>
                    <li>Hindi: <strong>1000 adet ve üzeri</strong></li>
                    <li>Kaz: <strong>1000 adet ve üzeri</strong></li>
                    <li>Serbest dolaşan tavukçuluk: <strong>1000 adet ve üzeri</strong></li>
                  </ul>
                </div>
              </div>

              <div className={styles.subsection}>
                <h3>🏗️ Bakıcı Evi Yapım Koşulları</h3>
                <div className={styles.info}>
                  <h4>Büyükbaş Tesisler İçin:</h4>
                  <ul>
                    <li>Tesis alanı 550-1500 m² arasında: Taban alanı <strong>75 m²</strong>, toplam inşaat alanı <strong>150 m²</strong></li>
                    <li>Tesis alanı 1500 m²'den büyük: Taban alanı <strong>150 m²</strong>, toplam inşaat alanı <strong>300 m²</strong></li>
                  </ul>

                  <h4>Küçükbaş Tesisler İçin:</h4>
                  <ul>
                    <li>Tesis alanı 450-900 m² arasında: Taban alanı <strong>75 m²</strong>, toplam inşaat alanı <strong>150 m²</strong></li>
                    <li>Tesis alanı 900 m²'den büyük: Taban alanı <strong>150 m²</strong>, toplam inşaat alanı <strong>300 m²</strong></li>
                  </ul>

                  <h4>Kanatlı Tesisler İçin:</h4>
                  <ul>
                    <li>Tesis alanı 750-1500 m² arasında: Taban alanı <strong>75 m²</strong>, toplam inşaat alanı <strong>150 m²</strong></li>
                    <li>Tesis alanı 1500 m²'den büyük: Taban alanı <strong>150 m²</strong>, toplam inşaat alanı <strong>300 m²</strong></li>
                  </ul>

                  <div className={styles.warning}>
                    <p><strong>Önemli:</strong> Yapımına izin verilen hayvancılık tesislerinde asıl yapı olan ahır, ağıl ve kümes binası ile yem deposu ve gübre çukuru bakıcı evinden önce yapılmalıdır. Aksi durumda tarım dışı kullanım faaliyeti olarak değerlendirilir.</p>
                  </div>
                </div>
              </div>

              <div className={styles.subsection}>
                <h3>🐝 Arıcılık Yapıları</h3>
                <div className={styles.info}>
                  <ul>
                    <li>En az <strong>50 arılı kovana</strong> sahip arıcılık yapılması şartıyla, bal sağım/saklama ve arıcılık malzeme depolaması için bir işletmeye <strong>50 metrekare</strong> kapalı alanda arıhane veya arı kışlatma evi yapılabilir</li>
                    <li>İşletmeye ilave her 50 arılı kovanlık için ilave <strong>10 metrekare</strong> alan eklenebilir</li>
                  </ul>
                </div>
              </div>

              <div className={styles.subsection}>
                <h3>⛺ Geçici Barınma Yapıları</h3>
                <div className={styles.info}>
                  <p>Hayvanların geçici barınması için ahır/ağıl olarak ihtiyaç duyulan çadır tipi yapılar, aşağıdaki şartları sağlaması durumunda TAD Portala girişi yapılmadan kurulabilir:</p>
                  <ul>
                    <li>Arazide kazı-dolgu yapılmadan</li>
                    <li>Beton atılmadan</li>
                    <li>Bitkisel üretime engel olmayacak şekilde</li>
                    <li>Sabit olmadan sökülüp takılabilir</li>
                    <li>İstenildiği zaman kaldırılarak taşınabilir tarzda</li>
                    <li>Toprak zemin üzerine yapılması</li>
                  </ul>
                  <div className={styles.warning}>
                    <p><strong>Not:</strong> Bu tür yapılar için müştemilat yapılmasına izin verilmez.</p>
                  </div>
                </div>
              </div>
            </section>

            <section className={styles.section}>
              <h2>💧 Kapalı Su Havzalarında Özel Hükümler</h2>
              <div className={styles.warning}>
                <p>Aşağıdaki illerde kapalı su havzası olarak ilan edilen su kısıtının bulunduğu arazilerde hayvancılık tesisleri için:</p>
                <p><strong>İller:</strong> Afyonkarahisar, Aksaray, Amasya, Ankara, Antalya, Aydın, Balıkesir, Burdur, Bursa, Çanakkale, Çorum, Denizli, Edirne, Elazığ, Erzurum, Hatay, İstanbul, İzmir, Karaman, Kayseri, Kırklareli, Kırşehir, Kocaeli, Konya, Manisa, Mardin, Mersin, Muğla, Muş, Nevşehir, Niğde, Sakarya, Şanlıurfa, Tekirdağ, Uşak, Yalova, Yozgat</p>
                <ul>
                  <li>Su ihtiyacının şebeke suyundan karşılanması durumunda ilgili idareden yazı alınmalı</li>
                  <li>Yer altı ve yer üstü su kullanımında DSİ'den su tahsis yazısı alınmalı</li>
                  <li>Taşıma su ile karşılanacağının belirtilmesi kabul edilmez</li>
                </ul>
              </div>
            </section>

            <section className={styles.section}>
              <h2>☀️ Güneş Enerjisi Santralleri (GES) Düzenlemeleri</h2>
              
              <div className={styles.subsection}>
                <h3>🌾 Tarımsal Amaçlı GES</h3>
                <div className={styles.info}>
                  <h4>Marjinal Tarım Arazisinde:</h4>
                  <ul>
                    <li>Sulama kapasitesi ile sulayabildiği arazinin en fazla <strong>%1,5'i</strong> kadar alana kurulabilir</li>
                    <li>Parselin mümkün olduğunca bitkisel üretime engel olmayacak kısmı üzerine kurulmalı</li>
                  </ul>

                  <h4>Mutlak, Özel Ürün veya Dikili Tarım Arazisinde:</h4>
                  <ul>
                    <li>Talep sahibine ait aynı enerji dağıtım bölgesi sınırları içerisinde toplam <strong>20 hektar ve üzerinde</strong> tarım arazisi bulunmalı</li>
                    <li>Kuyu/kuyuların sulayabildiği toplam arazinin en fazla <strong>%1,5'i</strong> kadar alana kurulabilir</li>
                  </ul>
                </div>
              </div>

              <div className={styles.subsection}>
                <h3>⚡ Lisanslı/Lisansız GES Yatırımları</h3>
                <div className={styles.highlight}>
                  <ul>
                    <li>Talep edilen alanın <strong>kuru marjinal tarım arazisi</strong> sınıfında olması zorunludur</li>
                    <li>Diğer tarım arazisi sınıflarında GES kurulmasına izin verilmez</li>
                    <li>Güneş enerjisinden elektrik üreterek gelir elde etmek maksadıyla tarımsal üretimden vazgeçilmeyeceğine dair <strong>noter taahhütnamesi</strong> alınır</li>
                    <li>Taahhütnameye uyulmadığının tespit edilmesi durumunda verilen izin iptal edilir</li>
                  </ul>
                </div>
              </div>
            </section>

            <section className={styles.section}>
              <h2>🏙️ Tarım Dışı Yapılara İlişkin İmar Düzenlemeleri</h2>
              
              <div className={styles.subsection}>
                <div className={styles.info}>
                  <ul>
                    <li>10/7/2019 tarihinden sonra belirlenecek köy ve/veya mezraların yerleşik alanı ve civarı için Kanun kapsamında tarım dışı amaçlı kullanım izni alınması gerekmektedir</li>
                    <li>19/7/2005 tarihinden önce onaylanmış ve halen yürürlükte olan 1/5000 veya 1/1000 ölçekli imar planları izinli kabul edilir</li>
                    <li>Onaylı bir plana bağlı olarak arsa vasfı kazanmış parseller, planın yürürlükte olması şartıyla, izinli kabul edilir</li>
                    <li>İl İdare Kurulu kararı ile belirlenen köy yerleşik alanı sınırı içerisinde 10/07/2019 tarihinden önce onaylanmış alanlar için Kanun hükümleri uygulanmaz</li>
                    <li>Tesis kadastrosu ile "arsa" vasfı kazanmış yerler Kanunun 3'üncü maddesi (i) bendi kapsamında değerlendirilir</li>
                  </ul>
                </div>
              </div>
            </section>

            <section className={styles.section}>
              <h2>📋 İzinlendirme İşlemleri ve Genel Hükümler</h2>
              
              <div className={styles.subsection}>
                <div className={styles.warning}>
                  <ul>
                    <li>Tarımsal amaçlı yapılarda yapının tarımsal amaç dışında kullanılamayacağı, kamulaştırma dışında ifraz edilemeyeceği, arsaya dönüştürülemeyeceği belirtilir</li>
                    <li>Plan veya ruhsat zorunluluğu olan arazi kullanımına ilişkin verilen izinler, tebliğ tarihinden itibaren <strong>iki yıl içerisinde</strong> ruhsata bağlanmadığı durumda geçersiz kabul edilir</li>
                    <li>Verilen izinlerin plana veya ruhsata bağlandığı tarihten itibaren ilgili idare bu durumu <strong>bir ay içerisinde</strong> İl Müdürlüğüne bildirmelidir</li>
                    <li>Kamu yararı kararı alınarak izin verilen alanlar izinlendirme amacı doğrultusunda kullanılmak zorundadır</li>
                    <li>Amaç değişikliği yapılmak istenmesi durumunda Kanun kapsamında yeniden izin alınması gerekmektedir</li>
                  </ul>
                </div>
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
