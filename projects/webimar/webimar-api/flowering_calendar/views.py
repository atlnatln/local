"""
Bitkilerin Çiçeklenme Takvimi API Views

Türkiye'nin tüm ilçelerinde hangi bitkilerin ne zaman çiçeklendiğini
gösteren API endpoint'leri.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from pathlib import Path
import json
from functools import lru_cache
import locale

# Data dosyası yolu
BASE_DIR = Path(__file__).resolve().parent
FLOWERING_DATA_PATH = BASE_DIR / 'data' / 'flowering_data.json'
BAL_CESITLERI_PATH = BASE_DIR.parent / 'bal_cesitleri.json'

# Bal türleri için alternatif arama terimleri
HONEY_SEARCH_TERMS = {
    "AYÇİÇEĞİ": ["AYÇİÇEĞİ", "AYÇİÇEK"],
    "ORMAN GÜLÜ": ["ORMAN GÜLÜ", "ORMANGÜLÜ"],
    "KEÇİBOYNUZU": ["KEÇİBOYNUZU", "HARNUP"],
}


@lru_cache(maxsize=1)
def load_flowering_data():
    """Çiçeklenme verilerini yükle ve cache'le"""
    if FLOWERING_DATA_PATH.exists():
        with open(FLOWERING_DATA_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


@lru_cache(maxsize=1)
def load_honey_power_data():
    """Bal yapma gücü verilerini yükle ve cache'le"""
    if BAL_CESITLERI_PATH.exists():
        with open(BAL_CESITLERI_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # İl bazlı lookup için dict oluştur
            result = {}
            for il_data in data.get('iller', []):
                il_name = turkish_upper(il_data['il'])
                result[il_name] = {}
                for bal in il_data.get('balCesitleri', []):
                    result[il_name][bal['balTuru']] = bal['oran']
            return result
    return {}


def turkish_upper(s):
    """Türkçe karakter duyarlı büyük harfe çevirme"""
    if not s:
        return ""
    return s.replace('i', 'İ').upper()


def normalize_plant_name(s: str) -> str:
    """Bitki adını karşılaştırma için normalize et"""
    if not s:
        return ""
    return " ".join(s.strip().lower().split())


def normalize_district_name(s: str) -> str:
    """İlçe adını karşılaştırma için normalize et"""
    if not s:
        return ""
    # Türkçe karakterleri ASCII'ye çevir
    normalized = s.strip()
    normalized = normalized.replace('İ', 'I').replace('ı', 'I').replace('i', 'I')
    normalized = normalized.replace('Ğ', 'G').replace('ğ', 'G')
    normalized = normalized.replace('Ü', 'U').replace('ü', 'U')
    normalized = normalized.replace('Ş', 'S').replace('ş', 'S')
    normalized = normalized.replace('Ç', 'C').replace('ç', 'C')
    normalized = normalized.replace('Ö', 'O').replace('ö', 'O')
    return " ".join(normalized.upper().split())


def normalize_province_name(s: str) -> str:
    """İl adını karşılaştırma için normalize et (GeoJSON/veri seti farklarını da kapsar)"""
    if not s:
        return ""
    normalized = s.strip()
    normalized = normalized.replace('İ', 'I').replace('ı', 'I').replace('i', 'I')
    normalized = normalized.replace('Ğ', 'G').replace('ğ', 'G')
    normalized = normalized.replace('Ü', 'U').replace('ü', 'U')
    normalized = normalized.replace('Ş', 'S').replace('ş', 'S')
    normalized = normalized.replace('Ç', 'C').replace('ç', 'C')
    normalized = normalized.replace('Ö', 'O').replace('ö', 'O')
    normalized = normalized.replace('Â', 'A').replace('â', 'A')
    normalized = normalized.replace('Î', 'I').replace('î', 'I')
    normalized = normalized.replace('Û', 'U').replace('û', 'U')

    normalized = "".join(normalized.upper().split())

    # Veri seti ile GeoJSON arasında isim farklılıkları
    if normalized == 'AFYONKARAHISAR':
        return 'AFYON'
    return normalized


def get_honey_power(province: str, honey_type: str) -> int:
    """Bir ilin belirli bal türü için güç değerini döndür (0-100)"""
    honey_data = load_honey_power_data()
    province_upper = turkish_upper(province)
    
    # İl ismini normalize et (AYDIN -> Aydın gibi durumlar için)
    for key in honey_data.keys():
        if turkish_upper(key) == province_upper:
            province_data = honey_data[key]
            return province_data.get(honey_type, 0)
    
    return 0


def turkish_sort(items, key_func=None):
    """Türkçe karakterlere göre sıralama"""
    try:
        locale.setlocale(locale.LC_ALL, 'tr_TR.UTF-8')
        if key_func:
            return sorted(items, key=lambda x: locale.strxfrm(key_func(x)))
        return sorted(items, key=locale.strxfrm)
    except:
        if key_func:
            return sorted(items, key=key_func)
        return sorted(items)


def date_ranges_overlap(start1, end1, start2, end2):
    """
    İki tarih aralığının kesişip kesişmediğini kontrol et.
    Yıl atlamalı (örn: 12. aydan 1. aya) aralıkları destekler.
    """
    def normalize_range(start, end):
        if start <= end:
            return [(start, end)]
        else:
            return [(start, (12, 31)), ((1, 1), end)]

    ranges1 = normalize_range(start1, end1)
    ranges2 = normalize_range(start2, end2)

    for s1, e1 in ranges1:
        for s2, e2 in ranges2:
            if s1 <= e2 and e1 >= s2:
                return True
    return False


def calculate_overlap_quality(user_start, user_end, plant_start, plant_end):
    """
    Kullanıcının seçtiği tarih aralığı ile bitki çiçeklenme döneminin
    ne kadar uyumlu olduğunu hesaplar.
    
    Returns:
        dict: {
            'overlap_type': 'full' | 'partial' | 'minimal' | 'none',
            'user_in_flowering': bool,  # Kullanıcı aralığı çiçeklenme içinde mi?
            'overlap_months': list,  # Kesişen aylar
            'warning': str | None  # Uyarı mesajı
        }
    """
    from datetime import date
    
    # Yılı sabit tutarak date objeleri oluştur (karşılaştırma için)
    def to_day_of_year(month, day):
        try:
            return date(2024, month, day).timetuple().tm_yday
        except:
            return date(2024, month, min(day, 28)).timetuple().tm_yday
    
    u_start_doy = to_day_of_year(user_start[0], user_start[1])
    u_end_doy = to_day_of_year(user_end[0], user_end[1])
    p_start_doy = to_day_of_year(plant_start[0], plant_start[1])
    p_end_doy = to_day_of_year(plant_end[0], plant_end[1])
    
    # Yıl atlama durumunu kontrol et
    if u_end_doy < u_start_doy:
        u_end_doy += 365
    if p_end_doy < p_start_doy:
        p_end_doy += 365
    
    # Kesişim hesapla
    overlap_start = max(u_start_doy, p_start_doy)
    overlap_end = min(u_end_doy, p_end_doy)
    
    if overlap_start > overlap_end:
        return {
            'overlap_type': 'none',
            'user_in_flowering': False,
            'overlap_months': [],
            'warning': 'Seçilen tarihler çiçeklenme dönemi dışında'
        }
    
    overlap_days = overlap_end - overlap_start + 1
    user_days = u_end_doy - u_start_doy + 1
    plant_days = p_end_doy - p_start_doy + 1
    
    # Kullanıcı aralığının ne kadarı çiçeklenme döneminde?
    user_coverage = overlap_days / user_days if user_days > 0 else 0
    
    # Kesişen ayları hesapla
    overlap_months = []
    for month in range(1, 13):
        month_start = to_day_of_year(month, 1)
        month_end = to_day_of_year(month, 28)  # Güvenli son gün
        if month_start <= overlap_end and month_end >= overlap_start:
            overlap_months.append(month)
    
    # Kullanıcı tamamen çiçeklenme döneminde mi?
    user_in_flowering = p_start_doy <= u_start_doy and u_end_doy <= p_end_doy
    
    # Overlap type belirleme
    if user_coverage >= 0.8:
        overlap_type = 'full'
        warning = None
    elif user_coverage >= 0.4:
        overlap_type = 'partial'
        warning = f'Seçilen tarihlerin sadece %{int(user_coverage*100)}\'i çiçeklenme dönemiyle örtüşüyor'
    elif user_coverage > 0:
        overlap_type = 'minimal'
        warning = f'⚠️ Seçilen tarihlerin sadece %{int(user_coverage*100)}\'i çiçeklenme dönemiyle örtüşüyor. Tarih aralığını gözden geçirin.'
    else:
        overlap_type = 'none'
        warning = 'Seçilen tarihler çiçeklenme dönemi dışında'
    
    return {
        'overlap_type': overlap_type,
        'user_in_flowering': user_in_flowering,
        'overlap_months': overlap_months,
        'overlap_percentage': int(user_coverage * 100),
        'warning': warning
    }


class FloweringDistrictsView(APIView):
    """Tarih aralığına göre çiçeklenen bitkilerin olduğu ilçeleri döndür"""
    
    def get(self, request):
        start_month = request.query_params.get('start_month')
        start_day = request.query_params.get('start_day')
        end_month = request.query_params.get('end_month')
        end_day = request.query_params.get('end_day')

        if not all([start_month, start_day, end_month, end_day]):
            return Response({
                'error': 'start_month, start_day, end_month, end_day parametreleri gerekli'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            start_m, start_d = int(start_month), int(start_day)
            end_m, end_d = int(end_month), int(end_day)
        except ValueError:
            return Response({
                'error': 'Geçersiz tarih parametreleri'
            }, status=status.HTTP_400_BAD_REQUEST)

        data = load_flowering_data()
        result = []

        for province, districts in data.items():
            for district, plants in districts.items():
                for plant_info in plants:
                    plant_start = tuple(plant_info['start'])
                    plant_end = tuple(plant_info['end'])

                    if date_ranges_overlap(
                        (start_m, start_d), (end_m, end_d),
                        plant_start, plant_end
                    ):
                        result.append({
                            'province': province,
                            'district': district,
                            'plant': plant_info['plant'],
                            'start': plant_start,
                            'end': plant_end
                        })
                        break  # Bu ilçe için birden fazla kayıt ekleme

        return Response({'districts': result, 'count': len(result)})


class PlantDistrictsView(APIView):
    """Belirli bir bitkinin hangi ilçelerde yetiştiğini döndür"""
    
    def get(self, request):
        plant_name = request.query_params.get('plant', '').strip()

        if not plant_name:
            return Response({
                'error': 'plant parametresi gerekli'
            }, status=status.HTTP_400_BAD_REQUEST)

        data = load_flowering_data()
        result = []
        plant_normalized = normalize_plant_name(plant_name)

        for province, districts in data.items():
            for district, plants in districts.items():
                for plant_info in plants:
                    if normalize_plant_name(plant_info.get('plant', '')) == plant_normalized:
                        result.append({
                            'province': province,
                            'district': district,
                            'plant': plant_info['plant'],
                            'start': plant_info['start'],
                            'end': plant_info['end']
                        })
                        break

        return Response({'districts': result, 'count': len(result)})


class PlantListView(APIView):
    """Tüm benzersiz bitki isimlerini döndür"""
    
    def get(self, request):
        data = load_flowering_data()
        plants = set()
        
        for province in data.values():
            for district in province.values():
                for p in district:
                    plants.add(p['plant'])

        sorted_plants = turkish_sort(list(plants))
        return Response(sorted_plants)


class DistrictPlantsView(APIView):
    """Bir ilçedeki tüm bitkileri ve çiçeklenme tarihlerini döndür"""
    
    def get(self, request):
        district_param = request.query_params.get('district', '').strip()
        province_param = request.query_params.get('province', '').strip()
        
        if not district_param:
            return Response({
                'error': 'district parametresi gerekli'
            }, status=status.HTTP_400_BAD_REQUEST)

        data = load_flowering_data()
        district_normalized = normalize_district_name(district_param)
        province_normalized = normalize_province_name(province_param) if province_param else None

        # İl parametresi varsa doğrudan il -> ilçe eşleştir
        if province_normalized:
            for province, districts in data.items():
                if normalize_province_name(province) != province_normalized:
                    continue
                for district, plants in districts.items():
                    if normalize_district_name(district) == district_normalized:
                        result = [{
                            'plant': p['plant'],
                            'start': p['start'],
                            'end': p['end']
                        } for p in plants]

                        result = turkish_sort(result, key_func=lambda x: x['plant'])
                        return Response({
                            'district': district,
                            'province': province,
                            'plants': result
                        })

            return Response({
                'error': 'İlçe bulunamadı',
                'plants': []
            })

        for province, districts in data.items():
            for district, plants in districts.items():
                if normalize_district_name(district) == district_normalized:
                    result = [{
                        'plant': p['plant'],
                        'start': p['start'],
                        'end': p['end']
                    } for p in plants]
                    
                    result = turkish_sort(result, key_func=lambda x: x['plant'])
                    return Response({
                        'district': district,
                        'province': province,
                        'plants': result
                    })

        return Response({
            'error': 'İlçe bulunamadı',
            'plants': []
        })


class DistrictDiversityView(APIView):
    """İlçelerdeki bitki çeşitliliğini döndür (heat map için)"""
    
    def get(self, request):
        # Opsiyonel tarih filtresi
        start_month = request.query_params.get('start_month')
        start_day = request.query_params.get('start_day')
        end_month = request.query_params.get('end_month')
        end_day = request.query_params.get('end_day')

        has_date_filter = all([start_month, start_day, end_month, end_day])
        
        if has_date_filter:
            try:
                start_m, start_d = int(start_month), int(start_day)
                end_m, end_d = int(end_month), int(end_day)
            except ValueError:
                return Response({
                    'error': 'Geçersiz tarih parametreleri'
                }, status=status.HTTP_400_BAD_REQUEST)

        data = load_flowering_data()
        result = []

        for province, districts in data.items():
            for district, plants in districts.items():
                if has_date_filter:
                    filtered_plants = []
                    for plant_info in plants:
                        plant_start = tuple(plant_info['start'])
                        plant_end = tuple(plant_info['end'])
                        if date_ranges_overlap(
                            (start_m, start_d), (end_m, end_d),
                            plant_start, plant_end
                        ):
                            filtered_plants.append(plant_info['plant'])
                    unique_plants = set(filtered_plants)
                else:
                    unique_plants = set(p['plant'] for p in plants)

                if len(unique_plants) > 0:
                    result.append({
                        'province': province,
                        'district': district,
                        'diversity': len(unique_plants),
                        'plants': list(unique_plants)
                    })

        result.sort(key=lambda x: x['diversity'], reverse=True)

        return Response({
            'districts': result,
            'max_diversity': result[0]['diversity'] if result else 0,
            'min_diversity': result[-1]['diversity'] if result else 0,
            'filtered': has_date_filter
        })


class ProvinceListView(APIView):
    """Tüm illeri döndür"""
    
    def get(self, request):
        data = load_flowering_data()
        provinces = turkish_sort(list(data.keys()))
        return Response(provinces)


class ProvinceDistrictsView(APIView):
    """Bir ildeki tüm ilçeleri döndür"""
    
    def get(self, request):
        province_param = request.query_params.get('province', '').strip()
        
        if not province_param:
            return Response({
                'error': 'province parametresi gerekli'
            }, status=status.HTTP_400_BAD_REQUEST)

        data = load_flowering_data()
        province_upper = province_param.upper()

        if province_upper in data:
            districts = turkish_sort(list(data[province_upper].keys()))
            return Response({
                'province': province_upper,
                'districts': districts
            })

        return Response({
            'error': 'İl bulunamadı',
            'districts': []
        })


class BeekeepingPlanView(APIView):
    """
    Arıcılık Planlama API
    
    Arıcı istediği bal çeşidini ve tarih aralığını seçer, 
    sistem 3-4 optimum bölge/rota planı döner.
    """
    
    def post(self, request):
        honey_type = request.data.get('honey_type', '').strip()
        honey_type = turkish_upper(honey_type)
        start_month = request.data.get('start_month')
        start_day = request.data.get('start_day')
        end_month = request.data.get('end_month')
        end_day = request.data.get('end_day')
        include_all = request.data.get('include_all', False)  # Tüm bölgeleri döndür
        
        # Validasyon
        if not honey_type:
            return Response({
                'error': 'honey_type parametresi gerekli (örn: KESTANE, ÇAM, NARENCİYE)'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not all([start_month, start_day, end_month, end_day]):
            return Response({
                'error': 'start_month, start_day, end_month, end_day parametreleri gerekli'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            start_m, start_d = int(start_month), int(start_day)
            end_m, end_d = int(end_month), int(end_day)
        except ValueError:
            return Response({
                'error': 'Geçersiz tarih parametreleri'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Çiçeklenme verisini yükle
        data = load_flowering_data()
        
        # 1. Bal çeşidine uygun bitkileri ve bölgeleri bul
        matching_districts = []
        
        for province, districts in data.items():
            # İl için bal yapma gücünü al
            honey_power = get_honey_power(province, honey_type)
            
            for district, plants in districts.items():
                district_plants = []
                all_plants = []  # İlçedeki tüm bitkiler
                
                for plant_info in plants:
                    plant_start = tuple(plant_info['start'])
                    plant_end = tuple(plant_info['end'])
                    
                    # Tüm bitkileri kaydet
                    all_plants.append({
                        'plant': plant_info['plant'],
                        'start': plant_start,
                        'end': plant_end
                    })
                    
                    # Bitkinin adı bal türünü içeriyor mu?
                    # Alternatif arama terimlerini kontrol et
                    search_terms = HONEY_SEARCH_TERMS.get(honey_type, [honey_type])
                    is_match = False
                    plant_upper = turkish_upper(plant_info['plant'])
                    
                    for term in search_terms:
                        if turkish_upper(term) in plant_upper:
                            is_match = True
                            break
                    
                    if is_match:
                        # Tarih aralığına uyuyor mu?
                        if date_ranges_overlap(
                            (start_m, start_d), (end_m, end_d),
                            plant_start, plant_end
                        ):
                            # Kesişim kalitesini hesapla
                            overlap_info = calculate_overlap_quality(
                                (start_m, start_d), (end_m, end_d),
                                plant_start, plant_end
                            )
                            district_plants.append({
                                'plant': plant_info['plant'],
                                'start': plant_start,
                                'end': plant_end,
                                'overlap_type': overlap_info['overlap_type'],
                                'overlap_percentage': overlap_info.get('overlap_percentage', 0),
                                'warning': overlap_info.get('warning')
                            })
                
                if district_plants:
                    # Bu ilçedeki toplam bitki çeşitliliğini hesapla
                    total_diversity = len(set(p['plant'] for p in plants))
                    
                    # Ortalama örtüşme yüzdesini hesapla
                    avg_overlap = sum(p.get('overlap_percentage', 0) for p in district_plants) / len(district_plants)
                    
                    # Kombine skor: bal gücü (%40) + örtüşme (%40) + çeşitlilik (%20)
                    combined_score = (honey_power * 0.4) + (avg_overlap * 0.4) + min(total_diversity, 50) * 0.4
                    
                    matching_districts.append({
                        'province': province,
                        'district': district,
                        'plants': district_plants,
                        'all_plants': all_plants,  # İlçedeki tüm bitkiler
                        'diversity_score': total_diversity,
                        'target_plant_count': len(district_plants),
                        'honey_power': honey_power,
                        'avg_overlap': round(avg_overlap),
                        'combined_score': round(combined_score, 1)
                    })
        
        if not matching_districts:
            return Response({
                'success': False,
                'message': f'{honey_type} balı için uygun bölge bulunamadı.',
                'plans': [],
                'all_districts': []
            })
        
        # 2. Kombine skora göre sırala
        matching_districts.sort(key=lambda x: x['combined_score'], reverse=True)
        
        # 3. En iyi 4 bölgeyi seç ve planlar oluştur
        top_districts = matching_districts[:4]
        
        plans = []
        for idx, district_info in enumerate(top_districts, 1):
            plan = {
                'plan_number': idx,
                'province': district_info['province'],
                'district': district_info['district'],
                'target_plants': district_info['plants'],
                'all_plants': district_info['all_plants'],
                'diversity_score': district_info['diversity_score'],
                'honey_power': district_info['honey_power'],
                'avg_overlap': district_info['avg_overlap'],
                'combined_score': district_info['combined_score'],
                'recommendation_reason': self._generate_reason(
                    idx, 
                    district_info, 
                    len(matching_districts)
                )
            }
            plans.append(plan)
        
        # Tüm bölgelerin özet listesi (frontend için)
        all_districts_summary = []
        for d in matching_districts:
            all_districts_summary.append({
                'province': d['province'],
                'district': d['district'],
                'honey_power': d['honey_power'],
                'avg_overlap': d['avg_overlap'],
                'diversity_score': d['diversity_score'],
                'combined_score': d['combined_score'],
                'target_plant_count': d['target_plant_count']
            })
        
        response_data = {
            'success': True,
            'honey_type': honey_type,
            'date_range': {
                'start': f'{start_d}/{start_m}',
                'end': f'{end_d}/{end_m}'
            },
            'total_matching_districts': len(matching_districts),
            'plans': plans,
            'all_districts': all_districts_summary if include_all else all_districts_summary[:20]
        }
        
        return Response(response_data)
    
    def _generate_reason(self, rank, district_info, total_count):
        """Plan önerisi için açıklama oluştur"""
        reasons = []
        
        if rank == 1:
            reasons.append("🥇 En yüksek hedef bitki yoğunluğu")
        elif rank == 2:
            reasons.append("🥈 İkinci en iyi hedef bitki yoğunluğu")
        elif rank == 3:
            reasons.append("🥉 Üçüncü en iyi hedef bitki yoğunluğu")
        else:
            reasons.append("⭐ Alternatif iyi lokasyon")
        
        # Bal yapma gücü bilgisi
        if district_info['honey_power'] >= 80:
            reasons.append(f"🍯 Yüksek bal potansiyeli (%{district_info['honey_power']})")
        elif district_info['honey_power'] >= 50:
            reasons.append(f"🍯 Orta bal potansiyeli (%{district_info['honey_power']})")
        elif district_info['honey_power'] > 0:
            reasons.append(f"🍯 Düşük bal potansiyeli (%{district_info['honey_power']})")
        
        if district_info['diversity_score'] > 50:
            reasons.append(f"Yüksek bitki çeşitliliği ({district_info['diversity_score']} tür)")
        elif district_info['diversity_score'] > 30:
            reasons.append(f"Orta düzey çeşitlilik ({district_info['diversity_score']} tür)")
        
        if district_info['target_plant_count'] > 1:
            reasons.append(f"{district_info['target_plant_count']} farklı hedef bitki mevcut")
        
        return ' | '.join(reasons)
