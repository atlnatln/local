# Ankadata: Google Maps API (Yeni) ile Doğrulanmış Veri Madenciliği Stratejisi

> **Not:** Bu doküman, Ankadata'nın "doğrulanmış veri" felsefesine uygun olarak, Google Maps Places API (New) kullanarak maliyet etkin ve yüksek doğruluklu sektörel veri toplama stratejisini açıklar.

## 1. Yönetici Özeti ve Felsefe
Coğrafi veri analizi ve sektörel pazar araştırması süreçlerinde, Google Haritalar Platformu (Places API - New), yapılandırılmamış veriyi iş zekasına dönüştürmek için kritik bir araçtır. Ankadata olarak amacımız, sadece "veri toplamak" değil, **doğrulanmış** ve **aksiyon alınabilir** veriye ulaşmaktır.

Bu strateji, üç aşamalı bir "huni" (funnel) mimarisine dayanır:
1.  **Geniş Kapsama (Discovery):** En düşük maliyetle maksimum aday işletme ID'si toplama.
2.  **Doğrulama (Verification):** Adayların gerçekten hedef sektörde ve aktif olduğunu doğrulama.
3.  **Zenginleştirme (Enrichment):** Yalnızca doğrulanmış işletmeler için pahalı iletişim verilerini çekme.

Bu metodoloji, gereksiz API maliyetlerini %80'e varan oranlarda düşürürken, veri kalitesini %95'in üzerine çıkarır.

> Not: Places API hunisinin ardından website alanı boş kayıtlar için Gemini Search Grounding tabanlı ek zenginleştirme kullanılır. Operasyonel adımlar için bkz. `docs/RUNBOOKS/gemini-search-grounding-enrichment.md`.

---

## 2. Yeni Nesil API Mimarisi ve Field Masking

Google Places API (v1), HTTP POST istekleri ve **Field Masking** (Alan Maskeleme) yapısı üzerine kuruludur. Bu yapı, geliştiricinin "kullandığın kadar öde" mantığıyla sadece ihtiyaç duyduğu veriyi talep etmesini sağlar.

### Üç Aşamalı Huni Mimarisi

| Aşama | API Metodu | Temel SKU | Birincil Hedef | Alan Maskesi (FieldMask) Yapısı |
| :--- | :--- | :--- | :--- | :--- |
| **1. Keşif** | `Text Search (New)` | Essentials (IDs Only) | Benzersiz ID Havuzu | `places.id`, `places.name`, `nextPageToken` |
| **2. Doğrulama** | `Place Details (New)` | Pro | Niteliksel Doğrulama | `id`, `displayName`, `formattedAddress`, `types`, `businessStatus` |
| **3. Zenginleştirme**| `Place Details (New)` | Enterprise | İletişim Verisi | `websiteUri`, `nationalPhoneNumber` |

---

## 3. Aşama 1: Text Search (New) ile Kitlesel ID Toplama

Sektörel araştırmanın temeli, hedeflenen sektördeki tüm işletmelerin benzersiz tanımlayıcılarını (Place ID) toplamaktır.

### Strateji
Bu aşamada amaç **veri zenginliği değil, veri kapsayıcılığıdır**. Bu nedenle sadece `places.id` talep edilerek maliyet "Essentials" (en düşük) seviyesinde tutulur.

### Arama Formatları (`textQuery`)

Sorgu kalitesi, başarının anahtarıdır. Üç ana format kullanılmalıdır:

1.  **Kategorik ve Bölgesel Format:**
    *   *Örnek:* "İzmir'de şehir plancısı".
    *   *Mantık:* API konum bilgisini sorgudan ayıklar.

2.  **Kategorik Filtreleme Formatı:**
    *   *Örnek:* "Ankara diş polikliniği" + `includedType: "dentist"`.
    *   *Mantık:* Google'ın "Table A" listesindeki sektörler için idealdir. Listede olmayan spesifik meslekler için metin varyasyonları kullanılır.

3.  **Yakınlık Odaklı Format:**
    *   *Örnek:* "Kadıköy yakınındaki mühendislik büroları".
    *   *Mantık:* `locationBias` parametresi ile desteklenmelidir.

### Kritik Teknik Detaylar
*   **Field Mask:** `places.id,nextPageToken,places.name` olmalıdır. `places.displayName` istenir ise maliyet Pro Tier'a çıkar.
*   **Field Mask Yazımı (Önemli):** `searchText` / `Text Search` çağrılarında alanların başına **`places.`** öneki gelir (örn. `places.id`), ancak `getPlace` / `Place Details` çağrılarında doğrudan alan adı kullanılır (örn. `id`, `displayName`). Bu fark geliştiricilerin sık yaptığı hataları engellemek için kritik bir nottur.
*   **Pagination / pageSize:** Text Search (New) maksimum 60 sonuç döndürür (sayfa başına maks. 20 kayıt için `pageSize` kullanılmalıdır). `nextPageToken` ile sayfalar arası geçiş yapılmalıdır. Not: Google `maxResultCount` parametresini kullanımdan kaldırmış olup, sayfa büyüklüğü için `pageSize` kullanılmalıdır.
*   **Konum Önceliği (Override Rule):** `textQuery` içinde açık bir konum (örn. "İstanbul'da ...", "Ankara ...") belirtildiğinde, API isteğin gövdesindeki `locationBias` parametresini **göz ardı eder** (ignore). Bu davranış, metin içindeki konumun sorguya öncelik verdiğini gösterir; kesin koordinat temelli sınırlama gerekiyorsa `locationRestriction` ile dikdörtgen sınır verin.
*   **LocationRestriction Notu:** Bu parametre sadece **kategorik** sorgular için çalışır ve sadece **dikdörtgen (Viewport)** formatını destekler.

---

## 4. Aşama 2: Place Details Pro ile Doğrulama

Toplanan binlerce ID hamdır ve gürültü içerir. Bu aşamada "gerçek" hedefler ayrıştırılır.

### Kriterler ve Veri Tazeliği
*   **`businessStatus`:** Sadece `OPERATIONAL` olanlar kabul edilir.
*   **`types`:** İşletmenin Table A (bkz. Ekler) üzerindeki kategorileri kontrol edilir.
*   **Place ID Refresh (Önemli):** Google, 12 aydan eski Place ID'lerin tazelenmesini önerir. İşletme taşınmış veya kapanmışsa ID "NOT_FOUND" dönebilir. Not: Bu tazeleme işlemi, yalnızca `id` alanı talep edildiğinde **tamamen ücretsizdir**; detay alanları talep edilirse ücret uygulanabilir.

---

## 5. Aşama 3: Place Details Enterprise ile İletişim Verisi

Sadece nitelikli kayıtlar için çalıştırılarak bütçe korunur.

### Hedef Veriler
*   **`websiteUri`:** Kurumsal web sitesi (Enterprise SKU).
*   **`nationalPhoneNumber`:** Yerel formatta telefon numarası (Enterprise SKU).

---

## 6. İleri Teknikler: Grid Search, Lokalizasyon ve Vektörel Haritalar

### Izgara Araması (Grid Search)
Google'ın 60 sonuç limitini aşmak için hedef bölge küçük parçalara bölünür.

*   **Matematik:** $$Izgara Adımı (D) = \sqrt{\frac{A_{toplam}}{N_{sorgu}}}$$
*   **Önlem:** Her kare için `locationRestriction` kullanılarak sonuçların çakışması önlenir.

### Türkiye İl ve İlçe Vektörel Verileri
Grid Search algoritmaları oluşturulurken, tarama alanlarının sınırlarını belirlemek için Türkiye idari sınırları kullanılmalıdır. Bu proje kapsamında referans alınacak GeoJSON dosyası:
*   **Dosya Yolu:** `[docs/turkey-districts.geojson](turkey-districts.geojson)`
*   **Kullanım Amacı:** Bu dosya, il ve ilçe bazlı poligonları içerir. Tarama algoritmaları bu poligonların sınırları dışına taşmayacak veya boş arazileri taramayacak şekilde optimize edilebilir.

### Türkçe Lokalizasyon ve Normalizasyon
*   **Karakter Kodlama:** Sorgular UTF-8 olmalıdır. Türkçe'deki "İ/ı" ve "I/ı" harfleri arama motorunda farklı eşleşmelere neden olabilir, bu yüzden `languageCode: "tr"` parametresi kritiktir.
*   **Header:** `Accept-Language: tr` eklenmelidir.
*   **Python Normalizasyon (Öneri):** Gönderilen `textQuery` değerlerinin Unicode NFC (Normalization Form C) formatında olması eşleşme oranlarını artırır. Örn: `import unicodedata\ntext = unicodedata.normalize('NFC', text)`.

---

## 6.1 Aşama 4 (Yeni): Gemini Search Grounding ile Website Tamamlama

Places API (Aşama 3) sonrası `website` alanı boş kalan doğrulanmış işletmeler için aşağıdaki prensip uygulanır:

*   **Model:** `gemini-2.5-flash`
*   **Araç:** Google Search Grounding (`google_search`)
*   **Hedef Çıktı:** Sadece resmi website URL'si veya `NONE`
*   **Filtreleme:** Sosyal medya/dizin domainleri kabul edilmez
*   **Maliyet Koruma:** kısa prompt + `max_output_tokens=64` + günlük request/token limitleri

Uygulama scripti: `services/backend/enrich_websites_with_gemini.py`

Kullanım, loglama ve limit uyarı detayları için runbook:

*   `docs/RUNBOOKS/gemini-search-grounding-enrichment.md`

---

## 7. Güncel Maliyet ve Kota Yönetimi (2025 Sonrası)
Mart 2025 itibarıyla Google, 200 dolarlık genel krediyi kaldırarak SKU bazlı ücretsiz kota sistemine geçmiştir:

*   **Essentials:** Ayda 10.000 ücretsiz billable event.
*   **Pro:** Ayda 5.000 ücretsiz billable event.
*   **Enterprise:** Ayda 1.000 ücretsiz billable event.

**Ankadata Tasarrufu:** 1.000 ID toplama (Ücretsiz) -> 500 Nitelik Kontrolü (Ücretsiz) -> 100 İletişim Verisi (Ücretsiz). Bu huni ile orta ölçekli tüm projeler $0 maliyetle tamamlanabilir.

---

## 8. Örnek Uygulama (Python)

```python
import requests
import time

# --- AŞAMA 1: Keşif (Essentials) ---
def stage_1_collect_ids(query, api_key):
    import unicodedata
    # Unicode NFC normalizasyonu (Türkçe karakter eşleşmelerini artırır)
    query = unicodedata.normalize('NFC', query)

    url = "https://places.googleapis.com/v1/places:searchText"
    all_ids = []
    next_token = None
    
    while True:
        payload = {"textQuery": query, "languageCode": "tr", "regionCode": "tr", "pageSize": 20}
        if next_token:
            payload["pageToken"] = next_token
        
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "Accept-Language": "tr",
            # places.name teknik Kaynak Adıdır (Resource Name)
            "X-Goog-FieldMask": "places.id,nextPageToken,places.name"
        }
        
        response = requests.post(url, json=payload, headers=headers).json()
        if "places" in response:
            all_ids.extend([p["id"] for p in response["places"]])
            
        next_token = response.get("nextPageToken")
        if not next_token:
            break
        time.sleep(2) # Token aktivasyonu için zorunlu bekleme 
        
    return list(set(all_ids))

# --- AŞAMA 2-3: Detay ve Zenginleştirme ---
def get_verified_data(place_id, api_key, enterprise=False):
    # Pro ve Enterprise alanlarını huniye göre maskele
    mask = "id,displayName,types,businessStatus"
    if enterprise:
        mask += ",websiteUri,nationalPhoneNumber"
        
    url = f"https://places.googleapis.com/v1/places/{place_id}"
    headers = {"X-Goog-Api-Key": api_key, "X-Goog-FieldMask": mask}
    
    return requests.get(url, headers=headers).json()
```

---

## 9. Sonuç

Ankadata stratejisi, Google Maps API'nin ham gücünü maliyet disipliniyle birleştirir. Grid Search ile kapsamı genişletilen (GeoJSON destekli), huni mimarisiyle maliyeti düşürülen ve normalizasyonla doğruluğu artırılan bu yöntem, sektördeki en yüksek veri kalitesi standartlarını sağlar.

---

## EK-A: Google Places Türleri (Table A)

Bu tablo, `includedPrimaryTypes`, `includedTypes` gibi filtreleme parametrelerinde ve Arama/Detay yanıtlarında kullanılan standart türleri içerir.

### Otomotiv
`car_dealer`, `car_rental`, `car_repair`, `car_wash`, `electric_vehicle_charging_station`, `gas_station`, `parking`, `rest_stop`

### İşletme
`corporate_office`, `farm`, `ranch`

### Kültür
`art_gallery`, `art_studio`, `auditorium`, `cultural_landmark`, `historical_place`, `monument`, `museum`, `performing_arts_theater`, `sculpture`

### Eğitim
`library`, `preschool`, `primary_school`, `school`, `secondary_school`, `university`

### Eğlence ve Dinlence
`amusement_center`, `amusement_park`, `aquarium`, `banquet_hall`, `bowling_alley`, `casino`, `community_center`, `convention_center`, `cultural_center`, `dog_park`, `event_venue`, `hiking_area`, `historical_landmark`, `marina`, `movie_rental`, `movie_theater`, `national_park`, `night_club`, `park`, `tourist_attraction`, `visitor_center`, `wedding_venue`, `zoo`, `spa`, `sauna`

### Finans
`accounting`, `atm`, `bank`

### Yiyecek ve İçecek
`american_restaurant`, `bakery`, `bar`, `barbecue_restaurant`, `brazilian_restaurant`, `breakfast_restaurant`, `cafe`, `chinese_restaurant`, `coffee_shop`, `fast_food_restaurant`, `french_restaurant`, `greek_restaurant`, `hamburger_restaurant`, `ice_cream_shop`, `indian_restaurant`, `indonesian_restaurant`, `italian_restaurant`, `japanese_restaurant`, `lebanese_restaurant`, `meal_delivery`, `meal_takeaway`, `mediterranean_restaurant`, `mexican_restaurant`, `middle_eastern_restaurant`, `pizza_restaurant`, `ramen_restaurant`, `restaurant`, `sandwich_shop`, `seafood_restaurant`, `spanish_restaurant`, `steak_house`, `sushi_restaurant`, `thai_restaurant`, `turkish_restaurant`, `vegan_restaurant`, `vegetarian_restaurant`, `vietnamese_restaurant`

### Coğrafi Alanlar
`administrative_area_level_1`, `administrative_area_level_2`, `country`, `locality`, `postal_code`, `school_district`

### Resmi Kurumlar
`city_hall`, `courthouse`, `embassy`, `fire_station`, `local_government_office`, `police`, `post_office`

### Sağlık ve Zindelik
`dental_clinic`, `dentist`, `doctor`, `drugstore`, `hospital`, `pharmacy`, `physiotherapist`, `veterinary_care`

### Konaklama
`bed_and_breakfast`, `campground`, `camping_cabin`, `cottage`, `extended_stay_hotel`, `farmstay`, `guest_house`, `hostel`, `hotel`, `lodging`, `motel`, `private_guest_room`, `resort_hotel`, `rv_park`

### İbadet Yerleri
`church`, `hindu_temple`, `mosque`, `synagogue`

### Hizmetler
`barber_shop`, `beauty_salon`, `cemetery`, `child_care_agency`, `consultant`, `courier_service`, `electrician`, `florist`, `funeral_home`, `hair_care`, `hair_salon`, `insurance_agency`, `lawyer`, `locksmith`, `moving_company`, `painter`, `plumber`, `real_estate_agency`, `roofing_contractor`, `storage`, `tailor`, `telecommunications_service_provider`, `travel_agency`

### Alışveriş
`auto_parts_store`, `bicycle_store`, `book_store`, `cell_phone_store`, `clothing_store`, `convenience_store`, `department_store`, `discount_store`, `electronics_store`, `furniture_store`, `gift_shop`, `grocery_store`, `hardware_store`, `home_goods_store`, `home_improvement_store`, `jewelry_store`, `liquor_store`, `market`, `pet_store`, `shoe_store`, `shopping_mall`, `sporting_goods_store`, `store`, `supermarket`, `wholesaler`

### Spor
`athletic_field`, `fitness_center`, `golf_course`, `gym`, `ski_resort`, `sports_club`, `sports_complex`, `stadium`, `swimming_pool`

### Ulaşım
`airport`, `bus_station`, `bus_stop`, `ferry_terminal`, `heliport`, `light_rail_station`, `subway_station`, `taxi_stand`, `train_station`, `transit_depot`, `transit_station`, `truck_stop`

---

## EK-B: Google Places Türleri (Table B)

Bu tablo, API yanıtlarında (`types`) dönebilen ancak filtreleme (`includedTypes`) için **kullanılamayan** ek türleri içerir (Sadece Otomatik Tamamlama'da hariç).

`administrative_area_level_3`, `administrative_area_level_4`, `administrative_area_level_5`, `colloquial_area`, `continent`, `establishment`, `finance`, `food`, `general_contractor`, `geocode`, `health`, `intersection`, `landmark`, `natural_feature`, `neighborhood`, `place_of_worship`, `point_of_interest`, `political`, `postal_code_prefix`, `postal_town`, `premise`, `route`, `street_address`, `sublocality`, `sublocality_level_1`, `sublocality_level_2`, `town_square`

---

## EK-C: Adres ve Bileşen Türleri

Yanıtların `addressComponents` bölümünde dönen tür etiketleri.

*   `street_address`: Açık adres.
*   `route`: Adlandırılmış rota (Cadde/Sokak adı).
*   `intersection`: Kavşak.
*   `political`: Siyasi tüzel kişilik (Mahalle idaresi vb.).
*   `country`: Ülke.
*   `administrative_area_level_1`: İl (Türkiye için).
*   `administrative_area_level_2`: İlçe (Türkiye için).
*   `administrative_area_level_4`: Mahalle/Köy (Türkiye'de bazen kullanılır).
*   `locality`: Şehir/Kasaba tüzel kişiliği.
*   `sublocality`: Semt.
*   `neighborhood`: Mahalle.
*   `premise`: Bina/Site adı.
*   `subpremise`: İç kapı numarası (Daire, Ofis).
*   `postal_code`: Posta kodu.
*   `street_number`: Dış kapı numarası.
*   `floor`: Kat.
*   `room`: Oda.

> **Not:** Yıldız işareti (*) olan veya yeni eklenen türler Google tarafından zamanla güncellenebilir. En güncel liste için Google Places API resmi dokümantasyonunu takip ediniz.
