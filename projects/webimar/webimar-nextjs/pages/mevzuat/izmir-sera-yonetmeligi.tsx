import React from 'react';
import Head from 'next/head';
import Layout from '../../components/Layout';

export default function IzmirSeraYonetmeligi() {
  return (
    <Layout>
      <Head>
        <title>İzmir Büyükşehir Belediyesi Sera Yapımı Mevzuatı | Tarım İmar</title>
        <meta name="description" content="İzmir Büyükşehir Belediyesi kırsal yerleşme alanlarında sera yapımı ile ilgili resmi yazı ve mevzuat detayları." />
      </Head>

      <div style={{ maxWidth: '900px', margin: '0 auto', padding: '4rem 2rem' }}>
        <div style={{ marginBottom: '2rem' }}>
          <a 
            href="/sera"
            style={{
              color: '#667eea',
              textDecoration: 'none',
              fontSize: '0.95rem',
              fontWeight: '500',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem',
              transition: 'color 0.3s ease'
            }}
          >
            ← Sera Sayfasına Dön
          </a>
        </div>

        <h1 style={{ fontSize: '2.5rem', fontWeight: '800', marginBottom: '2rem', color: '#2d3748', textAlign: 'center' }}>
          İzmir Büyükşehir Belediyesi<br/>Sera Yapımı Mevzuatı
        </h1>

        <div style={{ background: '#fff', padding: '2rem', borderRadius: '12px', boxShadow: '0 4px 6px rgba(0,0,0,0.05)', border: '1px solid #e2e8f0' }}>
          <div style={{ borderBottom: '1px solid #e2e8f0', paddingBottom: '1rem', marginBottom: '2rem', textAlign: 'center' }}>
            <p style={{ fontWeight: 'bold', color: '#4a5568' }}>T.C.<br/>İZMİR BÜYÜKŞEHİR BELEDİYE BAŞKANLIĞI<br/>Yapı Kontrol Dairesi Başkanlığı</p>
            <p style={{ fontSize: '0.9rem', color: '#718096', marginTop: '1rem' }}>
              Sayı : E-23444165-045.01-2409752<br/>
              Tarih: 29.01.2025
            </p>
          </div>

          <div style={{ lineHeight: '1.8', color: '#2d3748' }}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: '700', marginBottom: '1rem' }}>Konu : Kırsal Yerleşme Alanlarında Sera Yapımı</h3>
            
            <p style={{ marginBottom: '1.5rem' }}>
              <strong>BAYINDIR BELEDİYE BAŞKANLIĞINA<br/>İZMİR</strong>
            </p>

            <p style={{ marginBottom: '1.5rem' }}>
              <strong>İlgi :</strong> İmar ve Şehircilik Dairesi Başkanlığının 30.12.2024 tarihli ve E-91587970-115.01.02- 2365301 sayılı yazısı ve eki.
            </p>

            <p style={{ marginBottom: '1.5rem' }}>
              İlgi yazı ile; 21.11.2024 tarihli ve E-15481264-115.99-42272 sayılı yazınız ile Bayındır ilçe sınırları içerisinde 1/25.000 ölçekli İzmir Büyükşehir Bütünü Çevre Düzeni Planı ve Doğu Bölgesi Nazım İmar Planı kapsamında "Kırsal Yerleşme Alanları" olarak belirlenen alanlar içerisinde sera yapımına ilişkin taleplerin bulunduğu belirtilerek, 3194 sayılı İmar Kanunu, Plansız Alanlar İmar Yönetmeliği, Planlı Alanlar İmar Yönetmeliği ve 1/25.000 ölçekli Plan Uygulama Hükümleri kapsamında yapılan değerlendirmeler göz önünde bulundurularak Kırsal Yerleşme Alanlarında entegre nitelikte olmayan tarımsal amaçlı seraların yapılıp yapılamayacağı, yapılabiliyor ise tarım alanlarında ve imar planı içerisinde belirtilen koşulların kırsal yerleşim alanlarında da geçerli olup olmadığı, yapı ruhsatı, yapılaşma emsali, yola cephe şartı, çekme mesafesine ilişkin hususlarda kurum görüşümüzün Belediye Başkanlığınıza iletilmesi talep edilmektedir.
            </p>

            <h4 style={{ fontSize: '1.1rem', fontWeight: '700', marginTop: '2rem', marginBottom: '1rem' }}>Konuyla ilgili olarak;</h4>

            <ul style={{ listStyleType: 'disc', paddingLeft: '1.5rem', marginBottom: '1.5rem' }}>
              <li style={{ marginBottom: '1rem' }}>
                <strong>3194 sayılı İmar Kanununun 8 inci maddesinin (ğ) bendinde;</strong> "Büyükşehir belediyesi sınırının il sınırı olması nedeniyle mahalleye dönüşen ve nüfusu 5.000'in altında kalan yerlerin, kırsal yerleşim özelliğinin devam edip etmediğine büyükşehir belediye meclisince karar verilir... Kırsal alanlarda iş yeri açma ve çalışma izni; kadimden kalan veya yapıldığı tarihteki mevzuat kapsamında yola cephesi olmaksızın inşa edilen yapılar ile köy yerleşik alanlarda kalan yapılara kırsal yapı belgesine, yerleşik alan sınırı dışındaki diğer yapılara ise yapı kullanma izin belgesine göre verilir... Kamuya ait bir yaya veya taşıt yoluna cephe sağlanmadan yapı inşa edilemez, parsel oluşturulamaz..." hükmü,
              </li>
              <li style={{ marginBottom: '1rem' }}>
                <strong>27 nci maddesinin birinci fıkrasında;</strong> "Belediye ve mücavir alanlar dışında köylerin köy yerleşik alanlarında, civarında ve mezralarda yapılacak konut, entegre tesis niteliğinde olmayan ve imar planı gerektirmeyen tarım ve hayvancılık amaçlı yapılar... için yapı ruhsatı aranmaz. Ancak etüt ve projelerin valilik onayını müteakip muhtarlığa bildirimi ve bu yapıların yöresel doku ve mimari özelliklere, fen, sanat ve sağlık kurallarına uygun olması zorunludur..." hükmü,
              </li>
              <li style={{ marginBottom: '1rem' }}>
                <strong>Üçüncü fıkrasında;</strong> "Belediye ve mücavir alanlar içinde veya dışındaki iskan dışı alanlarda yapılacak tarımsal amaçlı seralar, entegre tesis niteliğinde olmamak ve ilgili il tarım ve orman müdürlüğünden uygun görüş alınmak koşuluyla yapı ruhsatı aranmadan yapılabilir. Ancak etüt ve projelerinin ruhsat vermeye yetkili idarece incelenmesi, fen, sanat ve sağlık kurallarına uygun olması zorunludur... Bu alanlarda yapılacak seralar için, yola cephesi olan komşu parsellerden süresiz geçiş hakkı alınmış ve bu konuda tapu kayıtlarına şerh konulmuş olmak kaydıyla 8 inci maddede belirtilen yola cephe sağlama koşulu aranmaz." hükmü bulunmakta olup,
              </li>
            </ul>

            <h4 style={{ fontSize: '1.1rem', fontWeight: '700', marginTop: '2rem', marginBottom: '1rem' }}>Plan Hükümleri İncelemesi</h4>
            
            <p style={{ marginBottom: '1rem' }}>
              Yürürlükteki 1/25000 ölçekli İzmir Büyükşehir Bütünü Çevre Düzeni Planı ve Doğu Bölgesi Nazım İmar Planı Plan Uygulama Hükümleri üzerinden yapılan incelemede:
            </p>

            <ul style={{ listStyleType: 'disc', paddingLeft: '1.5rem', marginBottom: '1.5rem' }}>
              <li style={{ marginBottom: '1rem' }}>
                <strong>Tarımsal Amaçlı Yapılar;</strong> "...örtü altı seralar... entegre nitelikte olmayan tesislerdir." şeklinde tanımlanmış,
              </li>
              <li style={{ marginBottom: '1rem' }}>
                <strong>Kırsal yerleşme alanlarına yönelik;</strong> "7.2.4. Bu alanlarda yapılacak uygulamalar... Plansız Alanlar İmar Yönetmeliği'nin 5. Bölümünde belirtilen esaslara göre yapılır." ve "7.2.5... tarım ve hayvancılık amaçlı yapılar yapılabilir... Yapılaşma koşulları; Emaks: 0,50 , Yençok: 2 kat..." hükmü ile yapılaşma koşulları tanımlanmış, ancak tarımsal amaçlı seralara ilişkin herhangi bir hüküm getirilmemiş olup,
              </li>
              <li style={{ marginBottom: '1rem' }}>
                <strong>Tarım Alanlarına ilişkin;</strong> "...Plansız Alanlar İmar Yönetmeliği'nin 6. bölümünde belirtilen esaslara göre yapılır." hükmü getirilmiş, 1/25000 ölçekli İzmir Büyükşehir Bütünü Çevre Düzeni Planı Plan Uygulama hükümlerinin 7.12.15. 3. maddesinde; "Örtü Altı Tarım (Seralar): Her tür tarım alanında, örtü altı tarım yapılmak istenmesi durumunda, seralar yukarıda belirtilen yapılaşma emsallerine dahil değildir... Seralar karayolundan en az 25 metre, diğer yollardan en az 10 metre, komşu parsellerden ise en az 5 metre çekerek yapılabilir. Örtü altı tarım yapılan parsellerde, sera zemininde ve çevresinde betonlama yapılamaz" hükmü yer almaktadır.
              </li>
            </ul>

            <h4 style={{ fontSize: '1.1rem', fontWeight: '700', marginTop: '2rem', marginBottom: '1rem' }}>Yönetmelik İncelemesi</h4>

            <p style={{ marginBottom: '1rem' }}>
              Yürürlükteki Plansız Alanlar İmar Yönetmeliğinin:
            </p>

            <ul style={{ listStyleType: 'disc', paddingLeft: '1.5rem', marginBottom: '1.5rem' }}>
              <li style={{ marginBottom: '1rem' }}>
                <strong>5 inci Bölümünde (Madde 47, 51, 57);</strong> Tarımsal amaçlı seralara ilişkin herhangi bir hüküm getirilmemiş,
              </li>
              <li style={{ marginBottom: '1rem' }}>
                <strong>6 ncı Bölümünde (Madde 63, 64);</strong> "Beton temel ve çelik çatılı ser'alar mahreç aldığı yola 5.00 metreden ve parsel hudutlarına ise 2.00 metreden fazla yaklaşmamak şartı ile inşaat alanı katsayısına tabi değildir... İskan dışı alanlarda yapılacak entegre tesis niteliğinde olmayan tarımsal amaçlı seralar... ilgili il tarım ve orman müdürlüğünün uygun görüşü ve ilgili idarenin izni alınmak koşuluyla yapı ruhsatı aranmadan yapılabilir... Bu alanlarda yapılacak seralar için, yola cephesi olan komşu parsellerden süresiz geçiş hakkı alınmış ve bu konuda tapu kayıtlarına şerh konulmuş olmak kaydıyla Kanunun 8 inci maddesinde belirtilen yola cephe sağlama koşulu aranmaz." hükmünün bulunduğu anlaşılmıştır.
              </li>
            </ul>

            <div style={{ background: '#f0fff4', padding: '1.5rem', borderRadius: '8px', borderLeft: '4px solid #48bb78', marginTop: '2rem' }}>
              <h4 style={{ fontSize: '1.2rem', fontWeight: '800', color: '#2f855a', marginBottom: '1rem' }}>SONUÇ VE DEĞERLENDİRME</h4>
              <p style={{ fontWeight: '500' }}>
                Bu kapsamda; Plansız Alanlar İmar Yönetmeliğinin 6 ncı Bölümünde ve 1/25000 ölçekli İzmir Büyükşehir Bütünü Çevre Düzeni Planında yalnızca tarım alanlarında ve iskan dışı alanlarda yapılacak seralara ilişkin yola cephe şartı olmadan ve yapılaşma emsaline dahil edilmeden yapılabileceğine yönelik istisnai hüküm getirildiği anlaşılmış olup,
              </p>
              <p style={{ marginTop: '1rem', fontWeight: 'bold' }}>
                1/25000 ölçekli İmar Planı Plan Notlarında örtü altı seraların tarımsal amaçlı yapı olarak tanımlandığı ve kırsal yerleşme alanlarında entegre tesis niteliğinde olmayan ve imar planı gerektirmeyen tarımsal amaçlı yapıların yapılabileceği dikkate alındığında, entegre tesis niteliğinde olmayan örtü altı seraların kırsal yerleşme alanlarındaki yola cephesi olan parsellerde 1/25000 ölçekli İzmir Büyükşehir Bütünü Çevre Düzeni Planı ve Doğu Bölgesi Nazım İmar Planı ile Plansız Alanlar İmar Yönetmeliğinde tariflenen yapılaşma koşullarına uygun olarak yapılaşma emsaline dahil edilmek ve yapı projelerinin fen ve sağlık kurallarına uygun olduğuna dair ilgili belediye onayı alınması kaydıyla yapı ruhsatı aranmadan yapılabileceği, ayrıca komşu mesafelerin Plansız Alanlar İmar Yönetmeliğinin 47 nci maddesi uyarınca Belediye Başkanlığınızca belirlenmesi gerektiği hususunda bilgi edinilmesini ve gereğini rica ederim.
              </p>
              <p style={{ marginTop: '1.5rem', textAlign: 'right', fontStyle: 'italic' }}>
                Zeki YILDIRIM<br/>
                Büyükşehir Belediye Başkanı a.<br/>
                Genel Sekreter Yardımcısı
              </p>
            </div>

            <div style={{ marginTop: '2rem', textAlign: 'center' }}>
              <a 
                href="https://www.resmigazete.gov.tr/eskiler/2024/03/20240316-1.htm" 
                target="_blank" 
                rel="noopener noreferrer"
                style={{
                  display: 'inline-block',
                  padding: '0.75rem 1.5rem',
                  background: '#e2e8f0',
                  color: '#4a5568',
                  borderRadius: '6px',
                  textDecoration: 'none',
                  fontWeight: '600',
                  fontSize: '0.9rem'
                }}
              >
                Resmi Gazete İlgili Yönetmelik ↗
              </a>
            </div>

          </div>
        </div>
      </div>
    </Layout>
  );
}
