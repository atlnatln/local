Web Sunucusu Uygulamaları için OAuth 2.0'ı Kullanma

Bu belgede, web sunucusu uygulamalarının Google API'lerine erişmek için OAuth 2.0 yetkilendirmesini uygulamak üzere Google API İstemci Kitaplıklarını veya Google OAuth 2.0 uç noktalarını nasıl kullandığı açıklanmaktadır.

OAuth 2.0 sayesinde kullanıcılar, bir uygulamayla belirli verileri paylaşırken kullanıcı adlarını, şifrelerini ve diğer bilgilerini gizli tutabilir. Örneğin, bir uygulama, kullanıcıların Google Drive'larına dosya depolamak için OAuth 2.0'ı kullanarak izin alabilir.

Bu OAuth 2.0 akışı, özellikle kullanıcı yetkilendirmesi için kullanılır. Gizli bilgileri depolayabilen ve durumu koruyabilen uygulamalar için tasarlanmıştır. Uygun şekilde yetkilendirilmiş bir web sunucusu uygulaması, kullanıcı uygulamayla etkileşimde bulunurken veya uygulamadan ayrıldıktan sonra bir API'ye erişebilir.

Web sunucusu uygulamaları da API isteklerini yetkilendirmek için sıklıkla hizmet hesaplarını kullanır. Bu durum özellikle kullanıcıya özel veriler yerine projeye dayalı verilere erişmek için Cloud API'leri çağrılırken geçerlidir. Web sunucusu uygulamaları, kullanıcı yetkilendirmesiyle birlikte hizmet hesaplarını kullanabilir.
Not: Uygulamanın doğru şekilde yapılmasıyla ilgili güvenlik etkileri göz önüne alındığında, Google'ın OAuth 2.0 uç noktalarıyla etkileşimde bulunurken OAuth 2.0 kitaplıklarını kullanmanızı önemle tavsiye ederiz. Başkaları tarafından sağlanan ve iyi bir şekilde hata ayıklanmış kodu kullanmak en iyi uygulamadır. Bu sayede kendinizi ve kullanıcılarınızı koruyabilirsiniz. Daha fazla bilgi için İstemci kitaplıkları başlıklı makaleyi inceleyin.
İstemci kitaplıkları

Bu sayfadaki dile özgü örneklerde, OAuth 2.0 yetkilendirmesini uygulamak için Google API İstemci Kitaplıkları kullanılır. Kod örneklerini çalıştırmak için öncelikle dilinize yönelik istemci kitaplığını yüklemeniz gerekir.

Uygulamanızın OAuth 2.0 akışını işlemek için Google API istemci kitaplığı kullandığınızda, istemci kitaplığı, uygulamanın aksi takdirde kendi başına işlemesi gereken birçok işlemi gerçekleştirir. Örneğin, uygulamanın depolanmış erişim jetonlarını ne zaman kullanabileceğini veya yenileyebileceğini ve izni ne zaman yeniden alması gerektiğini belirler. İstemci kitaplığı, doğru yönlendirme URL'leri de oluşturur ve yetkilendirme kodlarını erişim jetonlarıyla değiştiren yönlendirme işleyicilerinin uygulanmasına yardımcı olur.

Sunucu tarafı uygulamaları için Google API istemci kitaplıkları aşağıdaki dillerde kullanılabilir:

    Go
    Java
    .NET
    Node.js
    Dart
    PHP
    Python
    Ruby

Önemli: JavaScript için Google API istemci kitaplığı ve Google ile oturum açma yalnızca kullanıcının tarayıcısında OAuth 2.0'ı işlemek için tasarlanmıştır. Node.js kitaplığını kullanabilirsiniz.
Ön koşullar
Projeniz için API'leri etkinleştirme

Google API'lerini çağıran tüm uygulamaların bu API'leri API Console'de etkinleştirmesi gerekir.

Projenizde bir API'yi etkinleştirmek için:

    Open the API Library in the Google API Console.
    If prompted, select a project, or create a new one.
    API Library , ürün ailesine ve popülerliğe göre gruplandırılmış tüm kullanılabilir API'leri listeler. Etkinleştirmek istediğiniz API listede görünmüyorsa arama özelliğini kullanarak API'yi bulun veya ait olduğu ürün ailesinde Tümünü Göster'i tıklayın.
    Etkinleştirmek istediğiniz API'yi seçin ve Etkinleştir düğmesini tıklayın.
    If prompted, enable billing.
    If prompted, read and accept the API's Terms of Service.

Yetkilendirme kimlik bilgileri oluşturma

Google API'lerine erişmek için OAuth 2.0'ı kullanan tüm uygulamaların, uygulamayı Google'ın OAuth 2.0 sunucusuna tanıtan yetkilendirme kimlik bilgilerine sahip olması gerekir. Aşağıdaki adımlarda, projeniz için nasıl kimlik bilgisi oluşturacağınız açıklanmaktadır. Uygulamalarınız daha sonra bu kimlik bilgilerini kullanarak söz konusu proje için etkinleştirdiğiniz API'lere erişebilir.

    Go to the Credentials page.
    Create Client'ı (İstemci Oluştur) tıklayın.
    Web uygulaması uygulama türünü seçin.
    Formu doldurun ve Oluştur'u tıklayın. PHP, Java, Python, Ruby ve .NET gibi dilleri ve çerçeveleri kullanan uygulamalar, yetkili yönlendirme URI'lerini belirtmelidir. Yönlendirme URI'leri, OAuth 2.0 sunucusunun yanıt gönderebileceği uç noktalardır. Bu uç noktalar, Google'ın doğrulama kurallarına uymalıdır.

    Test için yerel makineye referans veren URI'ler (ör. http://localhost:8080) belirtebilirsiniz. Bu nedenle, bu belgedeki tüm örneklerde yönlendirme URI'si olarak http://localhost:8080 kullanıldığını lütfen unutmayın.

    Uygulamanızın yetkilendirme kodlarını sayfadaki diğer kaynaklara göstermemesi için uygulamanızın kimlik doğrulama uç noktalarını tasarlamanızı öneririz.

Kimlik bilgilerinizi oluşturduktan sonra client_secret.json dosyasını API Consolebölümünden indirin. Dosyayı yalnızca uygulamanızın erişebileceği bir konumda güvenli bir şekilde saklayın.
Önemli: client_secret.json dosyasını herkese açık bir konumda saklamayın. Ayrıca, uygulamanızın kaynak kodunu (ör. GitHub'da) paylaşırsanız istemci kimlik bilgilerinizin yanlışlıkla paylaşılmasını önlemek için client_secret.json dosyasını kaynak ağacınızın dışında saklayın.

Uygulamanızın istemci gizli anahtarı yalnızca istemciyi oluşturduktan sonra gösterilir. İstemci sırrını tekrar görüntüleyemez veya indiremezsiniz. Daha fazla bilgi edinin .
Erişim kapsamlarını belirleme

Kapsamlar, uygulamanızın yalnızca ihtiyaç duyduğu kaynaklara erişim isteğinde bulunmasını sağlar. Ayrıca, kullanıcıların uygulamanıza verdiği erişim miktarını kontrol etmesine de olanak tanır. Bu nedenle, istenen kapsam sayısı ile kullanıcı izni alma olasılığı arasında ters bir ilişki olabilir.

OAuth 2.0 yetkilendirmesini uygulamaya başlamadan önce, uygulamanızın erişim izni gerektireceği kapsamları belirlemenizi öneririz.

Ayrıca, uygulamanızın yetkilendirme kapsamlarına erişim isteğinde bulunmak için artımlı yetkilendirme sürecini kullanmasını öneririz. Bu süreçte uygulamanız, bağlam içinde kullanıcı verilerine erişim isteğinde bulunur. Bu en iyi uygulama, kullanıcıların uygulamanızın neden istediği erişime ihtiyacı olduğunu daha kolay anlamasına yardımcı olur.

OAuth 2.0 API Kapsamları dokümanında, Google API'lerine erişmek için kullanabileceğiniz kapsamların tam listesi yer alır.
Herkese açık uygulamanız, belirli kullanıcı verilerine erişime izin veren kapsamlar kullanıyorsa doğrulama sürecini tamamlaması gerekir. Uygulamanızı test ederken ekranda doğrulanmamış uygulama ifadesini görüyorsanız bu ifadeyi kaldırmak için doğrulama isteği göndermeniz gerekir. Doğrulanmamış uygulamalar hakkında daha fazla bilgi edinin ve Yardım Merkezi'nde uygulama doğrulama ile ilgili sık sorulan soruların yanıtlarını öğrenin.
Dile özgü koşullar

Bu belgedeki kod örneklerinden herhangi birini çalıştırmak için Google Hesabınızın olması, internete erişebilmeniz ve bir web tarayıcınızın olması gerekir. API istemci kitaplıklarından birini kullanıyorsanız aşağıdaki dile özgü şartlara da göz atın.
PHP
Python
Ruby
Node.js
HTTP/REST

Bu belgedeki Python kodu örneklerini çalıştırmak için şunlara ihtiyacınız vardır:

    Python 3.7 veya sonraki sürümler
    pip paket yönetimi aracı.
    Python 2.0 için Google API'leri İstemci Kitaplığı sürümü:

pip install --upgrade google-api-python-client

Kullanıcı yetkilendirmesi için google-auth, google-auth-oauthlib ve google-auth-httplib2.

pip install --upgrade google-auth google-auth-oauthlib google-auth-httplib2

Flask Python web uygulama çerçevesi.

pip install --upgrade flask

requests HTTP kitaplığı.

    pip install --upgrade requests

Python'u ve ilişkili taşıma kılavuzunu yükseltemiyorsanız Google API Python istemci kitaplığı sürüm notunu inceleyin.
OAuth 2.0 erişim jetonlarını edinme

Aşağıdaki adımlarda, uygulamanızın Google'ın OAuth 2.0 sunucusuyla nasıl etkileşimde bulunarak kullanıcı adına bir API isteği gerçekleştirmek için kullanıcının iznini aldığı gösterilmektedir. Uygulamanızın, kullanıcı yetkilendirmesi gerektiren bir Google API isteğini yürütebilmesi için bu izne sahip olması gerekir.

Aşağıdaki listede bu adımlar kısaca özetlenmiştir:

    Uygulamanız, ihtiyaç duyduğu izinleri tanımlar.
    Uygulamanız, kullanıcıyı istenen izinlerin listesiyle birlikte Google'a yönlendirir.
    Kullanıcı, uygulamanıza izin verip vermeyeceğine karar verir.
    Uygulamanız, kullanıcının neye karar verdiğini öğrenir.
    Kullanıcı istenen izinleri verdiyse uygulamanız, kullanıcı adına API istekleri yapmak için gereken jetonları alır.

1. adım: Yetkilendirme parametrelerini ayarlayın

İlk adım, yetkilendirme isteğini oluşturmaktır. Bu istek, uygulamanızı tanımlayan ve kullanıcıdan uygulamanıza vermesi istenecek izinleri tanımlayan parametreler ayarlar.

    OAuth 2.0 kimlik doğrulaması ve yetkilendirmesi için bir Google istemci kitaplığı kullanıyorsanız bu parametreleri tanımlayan bir nesne oluşturup yapılandırırsınız.
    Google OAuth 2.0 uç noktasını doğrudan çağırırsanız bir URL oluşturur ve bu URL'deki parametreleri ayarlarsınız.

Aşağıdaki sekmelerde, web sunucusu uygulamaları için desteklenen yetkilendirme parametreleri tanımlanmaktadır. Dile özgü örneklerde, bu parametreleri ayarlayan bir nesneyi yapılandırmak için istemci kitaplığının veya yetkilendirme kitaplığının nasıl kullanılacağı da gösterilmektedir.
PHP
Python
Ruby
Node.js
HTTP/REST

Aşağıdaki kod snippet'inde, yetkilendirme isteğini oluşturmak için google-auth-oauthlib.flow modülü kullanılmaktadır.

Kod, Flow nesnesi oluşturur. Bu nesne, yetkilendirme kimlik bilgilerini oluşturduktan sonra indirdiğiniz client_secret.json dosyasındaki bilgileri kullanarak uygulamanızı tanımlar. Bu nesne, uygulamanızın erişim izni istediği kapsamları ve Google'ın OAuth 2.0 sunucusundan gelen yanıtı işleyecek olan uygulamanızın kimlik doğrulama uç noktasının URL'sini de tanımlar. Son olarak, kod isteğe bağlı access_type ve include_granted_scopes parametrelerini ayarlar.

Örneğin, bu kod, bir kullanıcının Google Drive meta verilerine ve Takvim etkinliklerine salt okunur, çevrimdışı erişim isteğinde bulunur:

import google.oauth2.credentials
import google_auth_oauthlib.flow

# Required, call the from_client_secrets_file method to retrieve the client ID from a
# client_secret.json file. The client ID (from that file) and access scopes are required. (You can
# also use the from_client_config method, which passes the client configuration as it originally
# appeared in a client secrets file but doesn't access the file itself.)
flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file('client_secret.json',
    scopes=['https://www.googleapis.com/auth/drive.metadata.readonly',
            'https://www.googleapis.com/auth/calendar.readonly'])

# Required, indicate where the API server will redirect the user after the user completes
# the authorization flow. The redirect URI is required. The value must exactly
# match one of the authorized redirect URIs for the OAuth 2.0 client, which you
# configured in the API Console. If this value doesn't match an authorized URI,
# you will get a 'redirect_uri_mismatch' error.
flow.redirect_uri = 'https://www.example.com/oauth2callback'

# Generate URL for request to Google's OAuth 2.0 server.
# Use kwargs to set optional request parameters.
authorization_url, state = flow.authorization_url(
    # Recommended, enable offline access so that you can refresh an access token without
    # re-prompting the user for permission. Recommended for web server apps.
    access_type='offline',
    # Optional, enable incremental authorization. Recommended as a best practice.
    include_granted_scopes='true',
    # Optional, if your application knows which user is trying to authenticate, it can use this
    # parameter to provide a hint to the Google Authentication Server.
    login_hint='hint@example.com',
    # Optional, set prompt to 'consent' will prompt the user for consent
    prompt='consent')

Google yetkilendirme sunucusu, web sunucusu uygulamaları için aşağıdaki sorgu dizesi parametrelerini destekler:
Parametreler
client_id 	Zorunlu

Uygulamanızın istemci kimliği. Bu değeri bölümünde bulabilirsiniz.
redirect_uri 	Zorunlu

Kullanıcı yetkilendirme akışını tamamladıktan sonra API sunucusunun kullanıcıyı nereye yönlendireceğini belirler. Değer, istemcinizin bölümünde yapılandırdığınız OAuth 2.0 istemcisinin yetkili yönlendirme URI'lerinden biriyle tam olarak eşleşmelidir. Bu değer, sağlanan client_id için yetkili bir yönlendirme URI'siyle eşleşmezse redirect_uri_mismatch hatası alırsınız.

http veya https şemasının, büyük/küçük harf durumunun ve sondaki eğik çizginin ("/") eşleşmesi gerektiğini unutmayın.
response_type 	Zorunlu

Google OAuth 2.0 uç noktasının yetkilendirme kodu döndürüp döndürmeyeceğini belirler.

Web sunucusu uygulamaları için parametre değerini code olarak ayarlayın.
scope 	Zorunlu

Uygulamanızın kullanıcı adına erişebileceği kaynakları tanımlayan, boşlukla ayrılmış bir kapsam listesi. Bu değerler, Google'ın kullanıcıya gösterdiği izin ekranını bilgilendirir.

Kapsamlar, uygulamanızın yalnızca ihtiyaç duyduğu kaynaklara erişim isteğinde bulunmasını sağlar. Ayrıca, kullanıcıların uygulamanıza verdikleri erişim miktarını kontrol etmelerine de olanak tanır. Bu nedenle, istenen kapsam sayısı ile kullanıcı izni alma olasılığı arasında ters orantı vardır.

Uygulamanızın mümkün olduğunda bağlamdaki yetkilendirme kapsamlarına erişim isteğinde bulunmasını öneririz. Artımlı yetkilendirme aracılığıyla kullanıcı verilerine bağlam içinde erişim isteyerek kullanıcıların, uygulamanızın neden istediği erişime ihtiyacı olduğunu daha kolay anlamasına yardımcı olursunuz.
access_type 	Önerilen

Uygulamanızın, kullanıcı tarayıcıda bulunmadığında erişim jetonlarını yenileyip yenileyemeyeceğini belirtir. Geçerli parametre değerleri online (varsayılan değer) ve offline'dir.

Uygulamanızın, kullanıcı tarayıcıda bulunmadığında erişim jetonlarını yenilemesi gerekiyorsa değeri offline olarak ayarlayın. Bu, bu belgenin ilerleyen kısımlarında açıklanan erişim jetonlarını yenileme yöntemidir. Bu değer, Google yetkilendirme sunucusuna, uygulamanızın yetkilendirme kodunu jetonlarla ilk kez değiştirdiğinde yenileme jetonu ve erişim jetonu döndürmesini bildirir.
state 	Önerilen

Uygulamanızın, yetkilendirme isteğiniz ile yetkilendirme sunucusunun yanıtı arasındaki durumu korumak için kullandığı dize değerini belirtir. Kullanıcı, uygulamanızın erişim isteğini onayladıktan veya reddettikten sonra sunucu, URL sorgu bileşeninde (?) name=value çifti olarak gönderdiğiniz değeri tam olarak döndürür.redirect_uri

Bu parametreyi, kullanıcıyı uygulamanızdaki doğru kaynağa yönlendirme, tek kullanımlık rastgele sayılar gönderme ve siteler arası istek sahteciliğini azaltma gibi çeşitli amaçlarla kullanabilirsiniz. redirect_uri değeri tahmin edilebileceğinden, state değerini kullanmak gelen bağlantının bir kimlik doğrulama isteğinin sonucu olduğuna dair güvencenizi artırabilir. Rastgele bir dize oluşturur veya istemcinin durumunu yakalayan bir çerezin ya da başka bir değerin karmaşasını kodlarsanız isteğin ve yanıtın aynı tarayıcıdan geldiğinden emin olmak için yanıtı doğrulayabilirsiniz. Bu sayede siteler arası istek sahteciliği gibi saldırılara karşı koruma sağlanır. state jetonu oluşturma ve onaylama örneği için OpenID Connect dokümanlarına bakın.
Önemli: OAuth istemcisi, OAuth2 Spesifikasyonu 'nda belirtildiği gibi CSRF'yi engellemelidir. . Bunu yapmanın bir yolu, yetkilendirme isteğiniz ile yetkilendirme sunucusunun yanıtı arasındaki durumu korumak için state parametresini kullanmaktır.
include_granted_scopes 	İsteğe bağlı

Uygulamaların, bağlamda ek kapsamlara erişim isteğinde bulunmak için artımlı yetkilendirme kullanmasını sağlar. Bu parametrenin değerini true olarak ayarlarsanız ve yetkilendirme isteği verilirse yeni erişim jetonu, kullanıcının daha önce uygulamaya erişim izni verdiği tüm kapsamları da kapsar. Örnekler için kademeli yetkilendirme bölümüne bakın.
enable_granular_consent 	İsteğe bağlı

Varsayılan olarak true değerine ayarlanır. false olarak ayarlanırsa, 2019'dan önce oluşturulan OAuth istemci kimlikleri için daha ayrıntılı Google Hesabı izinleri devre dışı bırakılır. Daha ayrıntılı izinler her zaman etkin olduğundan yeni OAuth istemci kimlikleri etkilenmez.

Google, bir uygulama için ayrıntılı izinleri etkinleştirdiğinde bu parametrenin etkisi kalmaz.
login_hint 	İsteğe bağlı

Uygulamanız, kimliği doğrulamaya çalışan kullanıcının kim olduğunu biliyorsa Google kimlik doğrulama sunucusuna ipucu vermek için bu parametreyi kullanabilir. Sunucu, oturum açma formundaki e-posta alanını önceden doldurarak veya uygun çoklu oturum açma oturumunu seçerek oturum açma akışını basitleştirmek için ipucunu kullanır.

Parametre değerini, kullanıcının Google Kimliği'ne eşdeğer olan bir e-posta adresine veya sub tanımlayıcısına ayarlayın.
prompt 	İsteğe bağlı

Kullanıcıya sunulacak, boşlukla ayrılmış ve büyük/küçük harfe duyarlı istemler listesi. Bu parametreyi belirtmezseniz kullanıcıdan yalnızca projeniz ilk kez erişim istediğinde izin istenir. Daha fazla bilgi için Yeniden izin isteme başlıklı makaleyi inceleyin.

Olası değerler:
none 	Herhangi bir kimlik doğrulama veya izin ekranı göstermeyin. Diğer değerlerle birlikte belirtilmemelidir.
consent 	Kullanıcıdan izin isteyin.
select_account 	Kullanıcıdan bir hesap seçmesini isteyin.
2. adım: Google'ın OAuth 2.0 sunucusuna yönlendirin

Kimlik doğrulama ve yetkilendirme sürecini başlatmak için kullanıcıyı Google'ın OAuth 2.0 sunucusuna yönlendirin. Bu durum genellikle uygulamanızın ilk kez kullanıcı verilerine erişmesi gerektiğinde ortaya çıkar. Artımlı yetkilendirme durumunda bu adım, uygulamanızın henüz erişim izni olmayan ek kaynaklara ilk kez erişmesi gerektiğinde de gerçekleşir.
PHP
Python
Ruby
Node.js
HTTP/REST

Bu örnekte, Flask web uygulama çerçevesini kullanarak kullanıcının yetkilendirme URL'sine nasıl yönlendirileceği gösterilmektedir:

return flask.redirect(authorization_url)

Google'ın OAuth 2.0 sunucusu, kullanıcının kimliğini doğrular ve uygulamanızın istenen kapsamlara erişmesi için kullanıcının iznini alır. Yanıt, belirttiğiniz yönlendirme URL'si kullanılarak uygulamanıza geri gönderilir.
3. adım: Google, kullanıcıdan izin ister

Bu adımda kullanıcı, uygulamanıza istenen erişimi verip vermeyeceğine karar verir. Bu aşamada Google, uygulamanızın adını ve kullanıcının yetkilendirme kimlik bilgileriyle erişim izni istediği Google API hizmetlerini gösteren bir izin penceresi ile verilecek erişim kapsamlarının özetini gösterir. Kullanıcı daha sonra uygulamanızın istediği bir veya daha fazla kapsam için erişim izni vermeyi kabul edebilir ya da isteği reddedebilir.

Uygulamanızın, Google'ın OAuth 2.0 sunucusundan erişim izni verilip verilmediğini belirten yanıtı beklerken bu aşamada herhangi bir işlem yapması gerekmez. Bu yanıt, sonraki adımda açıklanmaktadır.
Hatalar

Google'ın OAuth 2.0 yetkilendirme uç noktasına yapılan istekler, beklenen kimlik doğrulama ve yetkilendirme akışları yerine kullanıcıya yönelik hata mesajları gösterebilir. Sık karşılaşılan hata kodları ve önerilen çözümler aşağıda listelenmiştir.
admin_policy_enforced

Google Hesabı, Google Workspace yöneticisinin politikaları nedeniyle istenen bir veya daha fazla kapsamı yetkilendiremiyor. Yöneticinin, OAuth istemci kimliğinize açıkça erişim izni verilene kadar tüm kapsamlar veya hassas ve kısıtlanmış kapsamlar için erişimi nasıl kısıtlayabileceği hakkında daha fazla bilgi edinmek için Google Workspace Yönetici Yardım Merkezi'ndeki Google Workspace verilerine hangi üçüncü taraf uygulamalar ve dahili uygulamaların erişebileceğini yönetme başlıklı makaleyi inceleyin.
disallowed_useragent

Yetkilendirme uç noktası, Google'ın OAuth 2.0 Politikaları tarafından izin verilmeyen yerleştirilmiş bir kullanıcı aracısı içinde gösteriliyor.
Android
iOS

Android geliştiriciler, yetkilendirme isteklerini android.webkit.WebView içinde açarken bu hata mesajıyla karşılaşabilir. Geliştiriciler bunun yerine Android için Google ile Oturum Açma veya OpenID Foundation'ın Android için AppAuth gibi Android kitaplıklarını kullanmalıdır.

Web geliştiriciler, bir Android uygulaması genel bir web bağlantısını yerleştirilmiş bir kullanıcı aracısında açtığında ve kullanıcı sitenizden Google'ın OAuth 2.0 yetkilendirme uç noktasına gittiğinde bu hatayla karşılaşabilir. Geliştiriciler, genel bağlantıların işletim sisteminin varsayılan bağlantı işleyicisinde açılmasına izin vermelidir. Bu işleyici, hem Android App Links işleyicilerini hem de varsayılan tarayıcı uygulamasını içerir. Android Özel Sekmeler kitaplığı da desteklenen bir seçenektir.
org_internal

İstekteki OAuth istemci kimliği, belirli bir Google Cloud kuruluşunda Google Hesaplarına erişimi sınırlayan bir projenin parçasıdır. Bu yapılandırma seçeneği hakkında daha fazla bilgi için OAuth izin ekranınızı ayarlama başlıklı yardım makalesindeki Kullanıcı türü bölümüne bakın.
invalid_client

OAuth istemci gizli anahtarı yanlış. Bu istek için kullanılan istemci kimliği ve gizli anahtar da dahil olmak üzere OAuth istemci yapılandırmasını inceleyin.
deleted_client

İsteği göndermek için kullanılan OAuth istemcisi silinmiştir. Silme işlemi manuel olarak veya kullanılmayan istemciler için otomatik olarak yapılabilir. Silinen müşteriler, silme işleminden sonraki 30 gün içinde geri yüklenebilir. Daha fazla bilgi edinin .
invalid_grant

Erişim jetonu yenilenirken veya artımlı yetkilendirme kullanılırken jetonun süresi dolmuş veya jeton geçersiz kılınmış olabilir. Kullanıcının kimliğini tekrar doğrulayın ve yeni jetonlar almak için kullanıcı izni isteyin. Bu hatayı görmeye devam ediyorsanız uygulamanızın doğru şekilde yapılandırıldığından ve isteğinizde doğru jetonları ve parametreleri kullandığınızdan emin olun. Aksi takdirde, kullanıcı hesabı silinmiş veya devre dışı bırakılmış olabilir.
redirect_uri_mismatch

Yetkilendirme isteğinde iletilen redirect_uri, OAuth istemci kimliği için yetkilendirilmiş bir yönlendirme URI'siyle eşleşmiyor. bölümündeki yetkilendirilmiş yönlendirme URI'lerini inceleyin.

redirect_uri parametresi, kullanımdan kaldırılmış ve artık desteklenmeyen bant dışı OAuth (OOB) akışını ifade edebilir. Entegrasyonunuzu güncellemek için taşıma kılavuzuna bakın.
invalid_request

Yaptığınız istekte bir sorun oluştu. Bunun birkaç nedeni olabilir:

    İstek doğru şekilde biçimlendirilmemiş
    İstek, gerekli parametreleri içermiyordu
    İstek, Google'ın desteklemediği bir yetkilendirme yöntemi kullanıyor. OAuth entegrasyonunuzun önerilen bir entegrasyon yöntemi kullandığını doğrulayın.

4. adım: OAuth 2.0 sunucu yanıtını işleyin
Önemli: OAuth 2.0 yanıtını sunucuda işlemeden önce, Google'dan alınan state değerinin yetkilendirme isteğinde gönderilen state değeriyle eşleştiğini onaylamanız gerekir. Bu doğrulama, isteği kötü amaçlı bir komut dosyasının değil, kullanıcının yaptığından emin olmaya yardımcı olur ve CSRF saldırısı riskini azaltır.

OAuth 2.0 sunucusu, uygulamanızın erişim isteğine yanıtta istekte belirtilen URL'yi kullanır.

Kullanıcı erişim isteğini onaylarsa yanıtta bir yetkilendirme kodu bulunur. Kullanıcı isteği onaylamazsa yanıtta hata mesajı yer alır. Web sunucusuna döndürülen yetkilendirme kodu veya hata mesajı, aşağıdaki örnekte gösterildiği gibi sorgu dizesinde görünür:

Hata yanıtı:

https://oauth2.example.com/auth?error=access_denied

Yetkilendirme kodu yanıtı:

https://oauth2.example.com/auth?code=4/P7q7W91a-oMsCeLvIaQm6bTrgtp7

Önemli: Yanıt uç noktanız bir HTML sayfası oluşturuyorsa bu sayfadaki tüm kaynaklar URL'deki yetkilendirme kodunu görebilir. Komut dosyaları URL'yi doğrudan okuyabilir ve Referer HTTP üstbilgisindeki URL, sayfadaki kaynakların herhangi birine veya tümüne gönderilebilir.

Yetkilendirme kimlik bilgilerini o sayfadaki tüm kaynaklara (özellikle sosyal eklentiler ve analizler gibi üçüncü taraf komut dosyaları) göndermek isteyip istemediğinizi dikkatlice değerlendirin. Bu sorunu önlemek için sunucunun önce isteği işlemesini, ardından yanıt parametrelerini içermeyen başka bir URL'ye yönlendirmesini öneririz.
Örnek OAuth 2.0 sunucu yanıtı

Bu akışı, Google Drive'ınızdaki dosyaların meta verilerini görüntülemek için salt okunur erişim ve Google Takvim etkinliklerinizi görüntülemek için salt okunur erişim isteyen aşağıdaki örnek URL'yi tıklayarak test edebilirsiniz:

https://accounts.google.com/o/oauth2/v2/auth?
 scope=https%3A//www.googleapis.com/auth/drive.metadata.readonly%20https%3A//www.googleapis.com/auth/calendar.readonly&
 access_type=offline&
 include_granted_scopes=true&
 response_type=code&
 state=state_parameter_passthrough_value&
 redirect_uri=https%3A//oauth2.example.com/code&
 client_id=client_id

OAuth 2.0 akışını tamamladıktan sonra http://localhost/oauth2callback adresine yönlendirilmeniz gerekir. Yerel makineniz bu adreste bir dosya sunmadığı sürece büyük olasılıkla 404 NOT FOUND hatasıyla karşılaşırsınız. Bir sonraki adımda, kullanıcı uygulamanıza geri yönlendirildiğinde URI'de döndürülen bilgiler hakkında daha ayrıntılı bilgi verilmektedir.
5. adım: Yetkilendirme kodunu yenileme ve erişim jetonlarıyla değiştirin

Web sunucusu yetkilendirme kodunu aldıktan sonra yetkilendirme kodunu erişim jetonuyla değiştirebilir.
PHP
Python
Ruby
Node.js
HTTP/REST

Geri çağırma sayfanızda, yetkilendirme sunucusu yanıtını doğrulamak için google-auth kitaplığını kullanın. Ardından, bu yanıttaki yetkilendirme kodunu erişim jetonuyla değiştirmek için flow.fetch_token yöntemini kullanın:

state = flask.session['state']
flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    'client_secret.json',
    scopes=['https://www.googleapis.com/auth/drive.metadata.readonly'],
    state=state)
flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

authorization_response = flask.request.url
flow.fetch_token(authorization_response=authorization_response)

# Store the credentials in the session.
# ACTION ITEM for developers:
#     Store user's access and refresh tokens in your data store if
#     incorporating this code into your real app.
credentials = flow.credentials
flask.session['credentials'] = {
    'token': credentials.token,
    'refresh_token': credentials.refresh_token,
    'token_uri': credentials.token_uri,
    'client_id': credentials.client_id,
    'client_secret': credentials.client_secret,
    'granted_scopes': credentials.granted_scopes}

Hatalar

Yetkilendirme kodunu erişim jetonuyla değiştirirken beklenen yanıt yerine aşağıdaki hatayla karşılaşabilirsiniz. Sık karşılaşılan hata kodları ve önerilen çözümler aşağıda listelenmiştir.
invalid_grant

Sağlanan yetkilendirme kodu geçersiz veya yanlış biçimde. Kullanıcıdan tekrar izin istemek için OAuth sürecini yeniden başlatarak yeni bir kod isteyin.
6. adım: Kullanıcıların hangi kapsamları verdiğini kontrol edin

Kullanıcılar, birden fazla izin (kapsam) istediğinizde uygulamanızın hepsine erişmesine izin vermeyebilir. Uygulamanız, hangi kapsamların gerçekten verildiğini doğrulamalı ve bazı izinlerin reddedildiği durumları sorunsuz bir şekilde ele almalıdır. Bu genellikle reddedilen kapsamları kullanan özelliklerin devre dışı bırakılmasıyla yapılır.

Ancak istisnalar bulunmaktadır. Google Workspace Enterprise uygulamaları, alanda yetki devri özelliğiyle veya Güvenilir olarak işaretlenmiş uygulamalar, ayrıntılı izinler kullanıcı rızası ekranını atlar. Bu uygulamalarda kullanıcılar ayrıntılı izin rızası ekranını görmez. Bunun yerine, uygulamanız istenen tüm kapsamları veya hiçbirini almaz.

Daha ayrıntılı bilgi için Ayrıntılı izinleri yönetme başlıklı makaleyi inceleyin.
PHP
Python
Ruby
Node.js
HTTP/REST

Döndürülen credentials nesnesinde, kullanıcının uygulamanıza verdiği kapsamların listesi olan bir granted_scopes özelliği bulunur.

credentials = flow.credentials
flask.session['credentials'] = {
    'token': credentials.token,
    'refresh_token': credentials.refresh_token,
    'token_uri': credentials.token_uri,
    'client_id': credentials.client_id,
    'client_secret': credentials.client_secret,
    'granted_scopes': credentials.granted_scopes}

Aşağıdaki işlev, kullanıcının uygulamanıza hangi kapsamları verdiğini kontrol eder.

def check_granted_scopes(credentials):
  features = {}
  if 'https://www.googleapis.com/auth/drive.metadata.readonly' in credentials['granted_scopes']:
    features['drive'] = True
  else:
    features['drive'] = False

  if 'https://www.googleapis.com/auth/calendar.readonly' in credentials['granted_scopes']:
    features['calendar'] = True
  else:
    features['calendar'] = False

  return features

Google API'lerini çağırma
PHP
Python
Ruby
Node.js
HTTP/REST

Erişim jetonu aldıktan sonra uygulamanız, belirli bir kullanıcı hesabı veya hizmet hesabı adına API isteklerini yetkilendirmek için bu jetonu kullanabilir. Çağırmak istediğiniz API için bir hizmet nesnesi oluşturmak üzere kullanıcıya özel yetkilendirme kimlik bilgilerini kullanın ve ardından yetkili API istekleri göndermek için bu nesneyi kullanın.

    Çağırmak istediğiniz API için bir hizmet nesnesi oluşturun. API'nin adı ve sürümü ile kullanıcı kimlik bilgileriyle googleapiclient.discovery kitaplığının build yöntemini çağırarak bir hizmet nesnesi oluşturursunuz: Örneğin, Drive API'nin 3. sürümünü çağırmak için:

from googleapiclient.discovery import build

drive = build('drive', 'v2', credentials=credentials)

Hizmet nesnesi tarafından sağlanan arayüzü kullanarak API hizmetine istekte bulunun. Örneğin, kimliği doğrulanmış kullanıcının Google Drive'ındaki dosyaları listelemek için:

    files = drive.files().list().execute()

Eksiksiz örnek

Aşağıdaki örnekte, kullanıcı kimliğini doğruladıktan ve uygulamanın kullanıcının Drive meta verilerine erişmesine izin verdikten sonra kullanıcının Google Drive'ındaki dosyaların JSON biçimli bir listesi yazdırılır.
PHP
Python
Ruby
Node.js
HTTP/REST

Bu örnekte Flask çerçevesi kullanılmaktadır. http://localhost:8080 adresinde bir web uygulaması çalıştırarak OAuth 2.0 akışını test etmenizi sağlar. Bu URL'ye giderseniz beş bağlantı görürsünüz:

    Drive API'yi çağırın: Bu bağlantı, kullanıcılar izin verdiyse örnek bir API isteğini yürütmeye çalışan bir sayfaya yönlendirir. Gerekirse yetkilendirme akışını başlatır. İşlem başarılı olursa sayfada API yanıtı gösterilir.
    Takvim API'sini çağıran sahte sayfa: Bu bağlantı, kullanıcılar izin verirse örnek bir Takvim API isteğini yürütmeye çalışan bir sahte sayfaya yönlendirir. Gerekirse yetkilendirme akışını başlatır. İşlem başarılı olursa sayfada API yanıtı gösterilir.
    Doğrudan kimlik doğrulama akışını test edin: Bu bağlantı, kullanıcıyı yetkilendirme akışından geçirmeye çalışan bir sayfaya yönlendirir. Uygulama, kullanıcı adına yetkili API istekleri göndermek için izin istiyor.
    Mevcut kimlik bilgilerini iptal et: Bu bağlantı, kullanıcının uygulamaya daha önce verdiği izinleri iptal eden bir sayfaya yönlendirir.
    Flask oturumu kimlik bilgilerini temizle: Bu bağlantı, Flask oturumunda depolanan yetkilendirme kimlik bilgilerini temizler. Bu sayede, uygulamanıza daha önce izin vermiş bir kullanıcı yeni bir oturumda API isteği yürütmeye çalışırsa ne olacağını görebilirsiniz. Ayrıca, bir kullanıcı uygulamanıza verilen izinleri iptal ettiğinde ve uygulamanız iptal edilmiş bir erişim jetonuyla isteği yetkilendirmeye çalıştığında uygulamanızın alacağı API yanıtını görmenizi sağlar.

Not: Bu kodu yerel olarak çalıştırmak için ön koşullar bölümündeki talimatları uygulamanız gerekir. Bu talimatlar arasında http://localhost:8080 öğesini kimlik bilgileriniz için geçerli bir yönlendirme URI'si olarak ayarlama ve bu kimlik bilgilerine ait client_secret.json dosyasını çalışma dizininize indirme yer alır.

# -*- coding: utf-8 -*-

import os
import flask
import requests

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
CLIENT_SECRETS_FILE = "client_secret.json"

# The OAuth 2.0 access scope allows for access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly',
          'https://www.googleapis.com/auth/calendar.readonly']
API_SERVICE_NAME = 'drive'
API_VERSION = 'v2'

app = flask.Flask(__name__)
# Note: A secret key is included in the sample so that it works.
# If you use this code in your application, replace this with a truly secret
# key. See https://flask.palletsprojects.com/quickstart/#sessions.
app.secret_key = 'REPLACE ME - this value is here as a placeholder.'

@app.route('/')
def index():
  return print_index_table()

@app.route('/drive')
def drive_api_request():
  if 'credentials' not in flask.session:
    return flask.redirect('authorize')

  features = flask.session['features']

  if features['drive']:
    # Load credentials from the session.
    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])

    drive = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)

    files = drive.files().list().execute()

    # Save credentials back to session in case access token was refreshed.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    flask.session['credentials'] = credentials_to_dict(credentials)

    return flask.jsonify(**files)
  else:
    # User didn't authorize read-only Drive activity permission.
    # Update UX and application accordingly
    return '<p>Drive feature is not enabled.</p>'

@app.route('/calendar')
    def calendar_api_request():
      if 'credentials' not in flask.session:
        return flask.redirect('authorize')

      features = flask.session['features']

      if features['calendar']:
        # User authorized Calendar read permission.
        # Calling the APIs, etc.
        return ('<p>User granted the Google Calendar read permission. '+
                'This sample code does not include code to call Calendar</p>')
      else:
        # User didn't authorize Calendar read permission.
        # Update UX and application accordingly
        return '<p>Calendar feature is not enabled.</p>'

@app.route('/authorize')
def authorize():
  # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES)

  # The URI created here must exactly match one of the authorized redirect URIs
  # for the OAuth 2.0 client, which you configured in the API Console. If this
  # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
  # error.
  flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

  authorization_url, state = flow.authorization_url(
      # Enable offline access so that you can refresh an access token without
      # re-prompting the user for permission. Recommended for web server apps.
      access_type='offline',
      # Enable incremental authorization. Recommended as a best practice.
      include_granted_scopes='true')

  # Store the state so the callback can verify the auth server response.
  flask.session['state'] = state

  return flask.redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
  # Specify the state when creating the flow in the callback so that it can
  # verified in the authorization server response.
  state = flask.session['state']

  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
  flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

  # Use the authorization server's response to fetch the OAuth 2.0 tokens.
  authorization_response = flask.request.url
  flow.fetch_token(authorization_response=authorization_response)

  # Store credentials in the session.
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
  credentials = flow.credentials
  
  credentials = credentials_to_dict(credentials)
  flask.session['credentials'] = credentials

  # Check which scopes user granted
  features = check_granted_scopes(credentials)
  flask.session['features'] = features
  return flask.redirect('/')
  

@app.route('/revoke')
def revoke():
  if 'credentials' not in flask.session:
    return ('You need to <a href="/authorize">authorize</a> before ' +
            'testing the code to revoke credentials.')

  credentials = google.oauth2.credentials.Credentials(
    **flask.session['credentials'])

  revoke = requests.post('https://oauth2.googleapis.com/revoke',
      params={'token': credentials.token},
      headers = {'content-type': 'application/x-www-form-urlencoded'})

  status_code = getattr(revoke, 'status_code')
  if status_code == 200:
    return('Credentials successfully revoked.' + print_index_table())
  else:
    return('An error occurred.' + print_index_table())

@app.route('/clear')
def clear_credentials():
  if 'credentials' in flask.session:
    del flask.session['credentials']
  return ('Credentials have been cleared.<br><br>' +
          print_index_table())

def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'granted_scopes': credentials.granted_scopes}

def check_granted_scopes(credentials):
  features = {}
  if 'https://www.googleapis.com/auth/drive.metadata.readonly' in credentials['granted_scopes']:
    features['drive'] = True
  else:
    features['drive'] = False

  if 'https://www.googleapis.com/auth/calendar.readonly' in credentials['granted_scopes']:
    features['calendar'] = True
  else:
    features['calendar'] = False

  return features

def print_index_table():
  return ('<table>' +
          '<tr><td><a href="/test">Test an API request</a></td>' +
          '<td>Submit an API request and see a formatted JSON response. ' +
          '    Go through the authorization flow if there are no stored ' +
          '    credentials for the user.</td></tr>' +
          '<tr><td><a href="/authorize">Test the auth flow directly</a></td>' +
          '<td>Go directly to the authorization flow. If there are stored ' +
          '    credentials, you still might not be prompted to reauthorize ' +
          '    the application.</td></tr>' +
          '<tr><td><a href="/revoke">Revoke current credentials</a></td>' +
          '<td>Revoke the access token associated with the current user ' +
          '    session. After revoking credentials, if you go to the test ' +
          '    page, you should see an <code>invalid_grant</code> error.' +
          '</td></tr>' +
          '<tr><td><a href="/clear">Clear Flask session credentials</a></td>' +
          '<td>Clear the access token currently stored in the user session. ' +
          '    After clearing the token, if you <a href="/test">test the ' +
          '    API request</a> again, you should go back to the auth flow.' +
          '</td></tr></table>')

if __name__ == '__main__':
  # When running locally, disable OAuthlib's HTTPs verification.
  # ACTION ITEM for developers:
  #     When running in production *do not* leave this option enabled.
  os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

  # This disables the requested scopes and granted scopes check.
  # If users only grant partial request, the warning would not be thrown.
  os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

  # Specify a hostname and port that are set as a valid redirect URI
  # for your API project in the Google API Console.
  app.run('localhost', 8080, debug=True)

Yönlendirme URI'si doğrulama kuralları

Google, geliştiricilerin uygulamalarının güvenliğini sağlamasına yardımcı olmak için yönlendirme URI'lerine aşağıdaki doğrulama kurallarını uygular. Yönlendirme URI'leriniz bu kurallara uymalıdır. Aşağıda bahsedilen alan, ana makine, yol, sorgu, şema ve kullanıcı bilgisi tanımları için RFC 3986 bölüm 3'e bakın.
Doğrulama kuralları
Şema 	

Yönlendirme URI'leri düz HTTP değil, HTTPS şemasını kullanmalıdır. Localhost URI'leri (localhost IP adresi URI'leri dahil) bu kuraldan muaftır.
Düzenleyen 	

Ana makineler ham IP adresleri olamaz. Localhost IP adresleri bu kuraldan muaftır.
Alan 	
Ana makine TLD'leri (Üst Düzey Alanlar) herkese açık ek listesinde yer almalıdır.
Barındırıcı alanlar “googleusercontent.com” olamaz.
Uygulama alana sahip olmadığı sürece, yönlendirme URI'leri URL kısaltıcı alanları (ör. goo.gl) içeremez. Ayrıca, kısaltma alanına sahip bir uygulama bu alana yönlendirme yapmayı seçerse yönlendirme URI'si yolunda “/google-callback/” içermeli veya “/google-callback” ile bitmelidir.
Userinfo 	

Yönlendirme URI'leri, userinfo alt bileşenini içeremez.
Yol 	

Yönlendirme URI'leri, “/..” veya “\..” ya da bunların URL kodlamasıyla gösterilen bir yol geçişi (dizin geri izleme olarak da adlandırılır) içeremez.
Sorgu 	

Yönlendirme URI'leri açık yönlendirme içeremez.
Fragment 	

Yönlendirme URI'leri, parça bileşenini içeremez.
Karakterler 	Yönlendirme URI'leri aşağıdakiler dahil belirli karakterleri içeremez:

    Joker karakterler ('*')
    Yazdırılamayan ASCII karakterleri
    Geçersiz yüzde kodlamaları (URL kodlaması biçiminde olmayan tüm yüzde kodlamaları: yüzde işareti ve ardından iki onaltılık rakam)
    Null karakterler (kodlanmış bir NULL karakteri, ör. %00, %C0%80)

Aşamalı yetkilendirme

OAuth 2.0 protokolünde uygulamanız, kapsamlarla tanımlanan kaynaklara erişmek için yetkilendirme ister. Kaynaklar için yetkilendirme isteğinde bulunmak, kullanıcı deneyimi açısından en iyi uygulamalardan biri olarak kabul edilir. Google'ın yetkilendirme sunucusu, bu uygulamayı etkinleştirmek için artımlı yetkilendirmeyi destekler. Bu özellik, kapsamları gerektiği şekilde istemenize olanak tanır ve kullanıcı yeni kapsam için izin verirse kullanıcının projeye verdiği tüm kapsamları içeren bir jetonla değiştirilebilecek bir yetkilendirme kodu döndürür.

Örneğin, kullanıcıların müzik parçalarını örneklemelerine ve miks oluşturmalarına olanak tanıyan bir uygulamanın, oturum açma sırasında çok az kaynağa ihtiyacı olabilir. Belki de oturum açan kişinin adından başka bir bilgiye gerek yoktur. Ancak, tamamlanmış bir miksin kaydedilmesi için kullanıcının Google Drive'ına erişim izni gerekir. Çoğu kullanıcı, uygulamadan yalnızca gerçekten ihtiyaç duyduğu zaman Google Drive'ına erişim izni istenmesini doğal karşılar.

Bu durumda, uygulama oturum açma sırasında temel oturum açma işlemini gerçekleştirmek için openid ve profile kapsamlarını isteyebilir, ardından bir karışımı kaydetmek için ilk istek sırasında https://www.googleapis.com/auth/drive.file kapsamını isteyebilir.

Artımlı yetkilendirmeyi uygulamak için erişim jetonu istemek üzere normal akışı tamamlarsınız ancak yetkilendirme isteğinin daha önce verilmiş kapsamları içerdiğinden emin olursunuz. Bu yaklaşım, uygulamanızın birden fazla erişim jetonunu yönetmek zorunda kalmasını önler.

Artımlı yetkilendirmeden alınan erişim jetonları için aşağıdaki kurallar geçerlidir:

    Jeton, yeni ve birleştirilmiş yetkilendirmeye dahil edilen kapsamların herhangi birine karşılık gelen kaynaklara erişmek için kullanılabilir.
    Erişim jetonu almak için birleşik yetkilendirme için yenileme jetonunu kullandığınızda erişim jetonu, birleşik yetkilendirmeyi temsil eder ve yanıtta yer alan scope değerlerinden herhangi biri için kullanılabilir.
    Birleştirilmiş yetkilendirme, izinler farklı istemcilerden istenmiş olsa bile kullanıcının API projesine verdiği tüm kapsamları içerir. Örneğin, bir kullanıcı uygulamanın masaüstü istemcisini kullanarak bir kapsama erişim izni verdiyse ve ardından mobil istemci aracılığıyla aynı uygulamaya başka bir kapsam için izin verdiyse birleştirilmiş yetkilendirme her iki kapsamı da içerir.
    Birleşik yetkilendirmeyi temsil eden bir jetonu iptal ederseniz ilişkili kullanıcı adına bu yetkilendirmenin tüm kapsamlarına erişim aynı anda iptal edilir.

Dikkat: Verilen kapsamları dahil etmeyi seçtiğinizde, daha önce kullanıcı tarafından verilen kapsamlar yetkilendirme isteğinize otomatik olarak eklenir. Uygulamanız şu anda yanıtta döndürülebilecek tüm kapsamları istemek için onaylanmamışsa bir uyarı veya hata sayfası gösterilebilir. Daha fazla bilgi için Doğrulanmamış uygulamalar başlıklı makaleyi inceleyin.

1. adım: Yetkilendirme parametrelerini ayarlayın bölümündeki dile özgü kod örnekleri ve 2. adım: Google'ın OAuth 2.0 sunucusuna yönlendirin bölümündeki örnek HTTP/REST yönlendirme URL'si, artımlı yetkilendirme kullanır. Aşağıdaki kod örneklerinde, artımlı yetkilendirmeyi kullanmak için eklemeniz gereken kod da gösterilmektedir.
PHP
Python
Ruby
Node.js
HTTP/REST

Python'da, yetkilendirme isteğinin daha önce verilmiş kapsamları içerdiğinden emin olmak için include_granted_scopes anahtar kelime bağımsız değişkenini true olarak ayarlayın. Aşağıdaki örnekte gösterildiği gibi, include_granted_scopes öğesinin ayarladığınız tek anahtar kelime bağımsız değişkeni olmaması çok olasıdır.

authorization_url, state = flow.authorization_url(
    # Enable offline access so that you can refresh an access token without
    # re-prompting the user for permission. Recommended for web server apps.
    access_type='offline',
    # Enable incremental authorization. Recommended as a best practice.
    include_granted_scopes='true')

Erişim jetonunu yenileme (çevrimdışı erişim)

Erişim jetonlarının süresi düzenli olarak dolar ve ilgili API isteği için geçersiz kimlik bilgileri haline gelir. Jetonla ilişkili kapsamlar için çevrimdışı erişim isteğinde bulunduysanız kullanıcıdan izin istemeden (kullanıcı mevcut değilken de dahil olmak üzere) erişim jetonunu yenileyebilirsiniz.

    Google API istemci kitaplığı kullanıyorsanız istemci nesnesi, bu nesneyi çevrimdışı erişim için yapılandırdığınız sürece erişim jetonunu gerektiğinde yeniler.
    Bir istemci kitaplığı kullanmıyorsanız kullanıcıyı Google'ın OAuth 2.0 sunucusuna yönlendirirken access_type HTTP sorgu parametresini offline olarak ayarlamanız gerekir. Bu durumda, Google'ın yetkilendirme sunucusu, erişim jetonu için yetkilendirme kodu değiş tokuşu yaptığınızda yenileme jetonu döndürür. Ardından, erişim jetonunun süresi dolarsa (veya başka bir zamanda) yeni bir erişim jetonu almak için yenileme jetonu kullanabilirsiniz.

Kullanıcı mevcut değilken bir Google API'sine erişmesi gereken tüm uygulamaların çevrimdışı erişim isteğinde bulunması gerekir. Örneğin, yedekleme hizmetleri gerçekleştiren veya önceden belirlenmiş zamanlarda işlemler yürüten bir uygulamanın, kullanıcı mevcut değilken erişim jetonunu yenileyebilmesi gerekir. Varsayılan erişim stiline online adı verilir.

Sunucu tarafı web uygulamaları, yüklü uygulamalar ve cihazlar, yetkilendirme işlemi sırasında yenileme jetonları alır. Yenileme jetonları genellikle istemci tarafı (JavaScript) web uygulamalarında kullanılmaz.
PHP
Python
Ruby
Node.js
HTTP/REST

Python'da, kullanıcıdan tekrar izin istemek zorunda kalmadan erişim jetonunu yenileyebilmek için access_type anahtar kelime bağımsız değişkenini offline olarak ayarlayın. Aşağıdaki örnekte gösterildiği gibi, access_type'nın ayarladığınız tek anahtar kelime bağımsız değişkeni olmaması çok olasıdır.

authorization_url, state = flow.authorization_url(
    # Enable offline access so that you can refresh an access token without
    # re-prompting the user for permission. Recommended for web server apps.
    access_type='offline',
    # Enable incremental authorization. Recommended as a best practice.
    include_granted_scopes='true')

Kullanıcı, istenen kapsamlar için çevrimdışı erişim izni verdikten sonra, kullanıcı çevrimdışıyken kullanıcı adına Google API'lerine erişmek için API istemcisini kullanmaya devam edebilirsiniz. İstemci nesnesi, gerektiğinde erişim jetonunu yeniler.
Jeton iptali

Bazı durumlarda kullanıcılar, bir uygulamaya verilen erişimi iptal etmek isteyebilir. Kullanıcı, Hesap Ayarları'nı ziyaret ederek erişimi iptal edebilir. Daha fazla bilgi için Hesabınıza erişimi olan üçüncü taraf site ve uygulamalar başlıklı destek belgesinin Site veya uygulama erişimini kaldırma bölümüne bakın.

Bir uygulamanın, kendisine verilen erişimi programatik olarak iptal etmesi de mümkündür. Kullanıcının e-posta listesinden çıktığı, bir uygulamayı kaldırdığı veya bir uygulamanın ihtiyaç duyduğu API kaynaklarının önemli ölçüde değiştiği durumlarda programatik iptal önemlidir. Diğer bir deyişle, kaldırma işleminin bir parçası olarak, daha önce uygulamaya verilen izinlerin kaldırıldığından emin olmak için bir API isteği gönderilebilir.
PHP
Python
Ruby
Node.js
HTTP/REST

Bir jetonu programatik olarak iptal etmek için https://oauth2.googleapis.com/revoke adresine bir istek gönderin. Bu istek, jetonu parametre olarak içerir ve Content-Type üstbilgisini ayarlar:

requests.post('https://oauth2.googleapis.com/revoke',
    params={'token': credentials.token},
    headers = {'content-type': 'application/x-www-form-urlencoded'})

Not: Başarılı bir iptal yanıtının ardından, iptalin tam olarak geçerli olması biraz zaman alabilir.
Zamana dayalı erişim

Zamana dayalı erişim, kullanıcının bir işlemi tamamlamak için sınırlı bir süre boyunca uygulamanıza verilerine erişim izni vermesine olanak tanır. İzin verme akışı sırasında belirli Google ürünlerinde kullanılabilen zamana dayalı erişim, kullanıcılara sınırlı bir süre için erişim izni verme seçeneği sunar. Örneğin, Data Portability API, tek seferlik veri aktarımına olanak tanır.

Kullanıcı, uygulamanıza zamana dayalı erişim izni verdiğinde yenileme jetonunun süresi belirtilen süre sonunda dolar. Yenileme jetonlarının belirli durumlarda daha erken geçersiz kılınabileceğini unutmayın. Ayrıntılar için bu durumlara bakın. Yetkilendirme kodu değiştirme yanıtında döndürülen refresh_token_expires_in alanı, bu gibi durumlarda yenileme jetonunun süresinin dolmasına kadar kalan süreyi gösterir.
Hesaplar Arası Koruma'yı uygulama

Kullanıcılarınızın hesaplarını korumak için atmanız gereken ek bir adım da Google'ın hesaplar arası koruma hizmetinden yararlanarak hesaplar arası korumayı uygulamaktır. Bu hizmet, kullanıcı hesabında yapılan önemli değişiklikler hakkında uygulamanıza bilgi sağlayan güvenlik etkinliği bildirimlerine abone olmanıza olanak tanır. Ardından, etkinliklere nasıl yanıt vereceğinize bağlı olarak işlem yapmak için bu bilgileri kullanabilirsiniz.

Google'ın hesaplar arası koruma hizmeti tarafından uygulamanıza gönderilen etkinlik türlerine ilişkin bazı örnekler:

    https://schemas.openid.net/secevent/risc/event-type/sessions-revoked
    https://schemas.openid.net/secevent/oauth/event-type/token-revoked
    https://schemas.openid.net/secevent/risc/event-type/account-disabled

Hesaplar Arası Koruma'yı uygulama ve kullanılabilir etkinliklerin tam listesi hakkında daha fazla bilgi için Hesaplar Arası Koruma ile kullanıcı hesaplarını koruma sayfasını inceleyin. 