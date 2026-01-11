import React from 'react';
import { formatArea } from '../../utils/areaCalculation';
import { getDefaultTreeData } from '../../modules/BagEvi';
import {
  FormSection,
  SectionTitle,
  FormGroup,
  Label,
  Input,
  Select,
  Button,
  AgacListesi,
  AgacItem,
  HighlightBox,
  FlexContainer,
  InfoText
} from './styles';

interface ManuelTabProps {
  // Form state
  dikiliAlan: number;
  tarlaAlani: number;
  zeytinlikAlani: number;
  secilenAgacTuru: string;
  secilenAgacTipi: string;
  agacSayisi: number;
  
  // Arazi bilgileri
  araziVasfi?: string;
  calculationType?: string;
  
  // Tree data
  agacVerileri: any[];
  eklenenAgaclar: any[];
  
  // Polygon data
  tarlaPolygon: any;
  dikiliPolygon: any;
  zeytinlikPolygon: any;
  
  // Edit state
  editingIndex: number | null;
  editingAgacSayisi: number;
  
  // Results
  hesaplamaSonucu?: any;
  
  // Actions
  updateField: (field: string, value: any) => void;
  agacEkle: () => void;
  agacEdit: (index: number) => void;
  agacEditSave: (index: number) => void;
  agacEditCancel: () => void;
  agacSil: (index: number) => void;
  updateEditCount: (count: number) => void;
  hesaplamaYap: () => void;
  temizleVeriler: () => void;
  devamEt: () => void;
  getMevcutTipler: (agacTuruId: string) => { value: string; label: string; }[];
  agacTuruSecimiSadeceDut?: boolean;
}

const ManuelTab: React.FC<ManuelTabProps> = ({
  dikiliAlan,
  tarlaAlani,
  zeytinlikAlani,
  secilenAgacTuru,
  secilenAgacTipi,
  agacSayisi,
  araziVasfi,
  calculationType = 'bag-evi',
  agacVerileri,
  eklenenAgaclar,
  tarlaPolygon,
  dikiliPolygon,
  zeytinlikPolygon,
  editingIndex,
  editingAgacSayisi,
  hesaplamaSonucu,
  updateField,
  agacEkle,
  agacEdit,
  agacEditSave,
  agacEditCancel,
  agacSil,
  updateEditCount,
  hesaplamaYap,
  temizleVeriler,
  devamEt,
  getMevcutTipler,
  agacTuruSecimiSadeceDut = false
}) => {

  // Helper fonksiyon: ID'den ağaç adını al
  const getAgacAdiById = (idOrName: string): string => {
    // Eğer sayısal ID ise ağaç adını bul
    const numericId = parseInt(idOrName, 10);
    if (!isNaN(numericId)) {
      const treeData = getDefaultTreeData();
      const agac = treeData.find(a => a.sira === numericId);
      return agac ? agac.tur : `ID:${numericId}`;
    }
    // Eğer zaten isim ise olduğu gibi döndür
    return idOrName;
  };

  return (
    <>
      <FormSection>
        <SectionTitle>📏 Alan Bilgisi</SectionTitle>
        
        {/* Haritadan gelen alan bilgisi uyarısı */}
        {(tarlaPolygon || dikiliPolygon || zeytinlikPolygon) && (
          <HighlightBox $variant="success">
            <div style={{ fontWeight: '600', marginBottom: '8px' }}>
              🗺️ Haritadan Alınan Veriler
            </div>
            {tarlaPolygon && (
              <div>✅ Tarla Alanı: {formatArea(tarlaAlani).m2} m² ({formatArea(tarlaAlani).donum} dönüm)</div>
            )}
            {dikiliPolygon && (
              <div>✅ Dikili Alan: {formatArea(dikiliAlan).m2} m² ({formatArea(dikiliAlan).donum} dönüm)</div>
            )}
            {zeytinlikPolygon && (
              <div>✅ Zeytinlik Alanı: {formatArea(zeytinlikAlani).m2} m² ({formatArea(zeytinlikAlani).donum} dönüm)</div>
            )}
            {(tarlaPolygon || dikiliPolygon || zeytinlikPolygon) && (
              <div style={{ fontWeight: '600', color: '#2563eb' }}>
                📊 Toplam Parsel: {formatArea((dikiliAlan || 0) + (tarlaAlani || 0) + (zeytinlikAlani || 0)).m2} m² ({formatArea((dikiliAlan || 0) + (tarlaAlani || 0) + (zeytinlikAlani || 0)).donum} dönüm)
              </div>
            )}
            <InfoText size="12px">
              Bu değerler harita üzerinden çizilen poligonlardan otomatik hesaplanmıştır.
            </InfoText>
          </HighlightBox>
        )}
        {/* Sera arazi tipi için özel alan girişi - sadece sera alanı */}
        {araziVasfi === 'Sera' ? (
          <FormGroup>
            <Label htmlFor="sera-alani-input">Kurulu Sera Alanı (m²)</Label>
            <Input
              id="sera-alani-input"
              type="number"
              value={dikiliAlan}
              onChange={(e) => updateField('dikiliAlan', Number(e.target.value))}
              placeholder="Örn: 8000"
              min="1"
            />
            <InfoText>
              Sera arazi tipinde sadece kurulu sera alanı bilgisi gereklidir.
              {dikiliAlan > 0 && (
                <div style={{ color: '#2563eb', marginTop: '2px', fontWeight: '600' }}>
                  📊 Toplam Sera: {dikiliAlan.toLocaleString()} m² ({(dikiliAlan / 1000).toFixed(1)} dönüm)
                </div>
              )}
            </InfoText>
          </FormGroup>
        ) : araziVasfi === 'Ham toprak, taşlık, kıraç, palamutluk, koruluk gibi diğer vasıflı' ? (
          /* Ham toprak arazi tipi için özel alan girişi - sadece toplam alan */
          <FormGroup>
            <Label htmlFor="ham-toprak-alani-input">Toplam Arazi Alanı (m²)</Label>
            <Input
              id="ham-toprak-alani-input"
              type="number"
              value={dikiliAlan}
              onChange={(e) => updateField('dikiliAlan', Number(e.target.value))}
              placeholder="Örn: 25000"
              min="1"
            />
            <InfoText>
              Ham toprak arazi tipinde sadece toplam arazi alanı bilgisi gereklidir (min 20.000 m²).
              {dikiliAlan > 0 && (
                <div style={{ color: '#2563eb', marginTop: '2px', fontWeight: '600' }}>
                  📊 Toplam Alan: {dikiliAlan.toLocaleString()} m² ({(dikiliAlan / 1000).toFixed(1)} dönüm)
                </div>
              )}
            </InfoText>
          </FormGroup>
        ) : araziVasfi === 'Tarla' ? (
          /* Tarla arazi tipi için özel alan girişi - sadece toplam alan */
          <FormGroup>
            <Label htmlFor="sadece-tarla-alani-input">Toplam Tarla Alanı (m²)</Label>
            <Input
              id="sadece-tarla-alani-input"
              type="number"
              value={dikiliAlan}
              onChange={(e) => updateField('dikiliAlan', Number(e.target.value))}
              placeholder="Örn: 25000"
              min="1"
            />
            <InfoText>
              Tarla arazi tipinde sadece toplam tarla alanı bilgisi gereklidir (min 20.000 m²).
              {dikiliAlan > 0 && (
                <div style={{ color: '#2563eb', marginTop: '2px', fontWeight: '600' }}>
                  📊 Toplam Tarla: {dikiliAlan.toLocaleString()} m² ({(dikiliAlan / 1000).toFixed(1)} dönüm)
                </div>
              )}
            </InfoText>
          </FormGroup>
        ) : (
          /* Diğer arazi tipleri için normal dikili alan input'u */
          <FormGroup>
            <Label htmlFor="dikili-alan-input">Dikili Alan (m²)</Label>
            <Input
              id="dikili-alan-input"
              type="number"
              value={dikiliAlan}
              onChange={(e) => updateField('dikiliAlan', Number(e.target.value))}
              placeholder="Örn: 12000"
              min="1"
            />
          </FormGroup>
        )}
        {/* Tarla alanı inputunu göster (belirtilen arazi tipleri hariç) */}
        {!agacTuruSecimiSadeceDut &&
          araziVasfi !== 'Tarla + Zeytinlik' && 
          araziVasfi !== 'Zeytin ağaçlı + herhangi bir dikili vasıf' && 
          araziVasfi !== '… Adetli Zeytin Ağacı bulunan + herhangi bir dikili vasıf' &&
          araziVasfi !== 'Dikili vasıflı' && 
          araziVasfi !== 'Sera' && 
          araziVasfi !== 'Ham toprak, taşlık, kıraç, palamutluk, koruluk gibi diğer vasıflı' &&
          araziVasfi !== 'Tarla' && (
            <FormGroup>
              <Label htmlFor="tarla-alani-input">Tarla Alanı (m²)</Label>
              <Input
                id="tarla-alani-input"
                type="number"
                value={tarlaAlani}
                onChange={(e) => updateField('tarlaAlani', Number(e.target.value))}
                placeholder="Örn: 15000"
                min="1"
              />
              <InfoText>
                Toplam parsel alanı (dikili alan + tarla alanı)
                {dikiliAlan > 0 && tarlaAlani > 0 && (
                  <div style={{ color: '#2563eb', marginTop: '2px', fontWeight: '600' }}>
                    📊 Toplam: {(dikiliAlan + tarlaAlani).toLocaleString()} m² ({((dikiliAlan + tarlaAlani) / 1000).toFixed(1)} dönüm)
                  </div>
                )}
              </InfoText>
            </FormGroup>
        )}

        {/* "… Adetli Zeytin Ağacı bulunan tarla" arazi tipi için tarla alanı girişi - ÖZEL */}
        {araziVasfi === '… Adetli Zeytin Ağacı bulunan tarla' && (
          <FormGroup>
            <Label htmlFor="tarla-alani-zeytin-input">Tarla Alanı (m²)</Label>
            <Input
              id="tarla-alani-zeytin-input"
              type="number"
              value={tarlaAlani}
              onChange={(e) => updateField('tarlaAlani', Number(e.target.value))}
              placeholder="Örn: 25000"
              min="1"
            />
            <InfoText>
              "… Adetli Zeytin Ağacı bulunan tarla" arazi tipi için tarla alanı bilgisi gereklidir.
              {tarlaAlani > 0 && (
                <div style={{ color: '#2563eb', marginTop: '2px', fontWeight: '600' }}>
                  📊 Toplam Tarla: {tarlaAlani.toLocaleString()} m² ({(tarlaAlani / 1000).toFixed(1)} dönüm)
                </div>
              )}
            </InfoText>
          </FormGroup>
        )}

        {/* "Tarla + Zeytinlik" arazi tipi için özel alan girişleri */}
        {araziVasfi === 'Tarla + Zeytinlik' && (
          <>
            <FormGroup>
              <Label htmlFor="tarla-alani-input">Tarla Alanı (m²)</Label>
              <Input
                id="tarla-alani-input"
                type="number"
                value={tarlaAlani}
                onChange={(e) => updateField('tarlaAlani', Number(e.target.value))}
                placeholder="Örn: 15000"
                min="1"
              />
              <InfoText>
                Tarla kullanımındaki alan büyüklüğü
              </InfoText>
            </FormGroup>

            <FormGroup>
              <Label htmlFor="zeytinlik-alani-input">Zeytinlik Alanı (m²)</Label>
              <Input
                id="zeytinlik-alani-input"
                type="number"
                value={zeytinlikAlani}
                onChange={(e) => updateField('zeytinlikAlani', Number(e.target.value))}
                placeholder="Örn: 6000"
                min="1"
              />
              <InfoText>
                Zeytinlik kullanımındaki alan büyüklüğü
                {tarlaAlani > 0 && zeytinlikAlani > 0 && (
                  <div style={{ color: '#2563eb', marginTop: '2px', fontWeight: '600' }}>
                    📊 Toplam: {(tarlaAlani + zeytinlikAlani).toLocaleString()} m² ({((tarlaAlani + zeytinlikAlani) / 1000).toFixed(1)} dönüm)
                  </div>
                )}
              </InfoText>
            </FormGroup>
          </>
        )}
      </FormSection>

      {/* Ağaç Bilgileri - "Tarla + Zeytinlik" ve "… Adetli Zeytin Ağacı bulunan tarla" için gizli */}
      {araziVasfi !== 'Tarla + Zeytinlik' && araziVasfi !== '… Adetli Zeytin Ağacı bulunan tarla' && (
        <FormSection>
          <SectionTitle>🌱 Ağaç Bilgileri</SectionTitle>
          
          {/* "Zeytin ağaçlı + herhangi bir dikili vasıf" için özel açıklama */}
          {araziVasfi === 'Zeytin ağaçlı + herhangi bir dikili vasıf' && (
            <HighlightBox $variant="info">
              <div style={{ fontWeight: '600', marginBottom: '8px' }}>
                🫒 Zeytin Ağaçlı + Dikili Vasıf Kontrolü
              </div>
              <InfoText>
                Bu arazi tipinde hem zeytin ağacı hem de diğer dikili ürünler bulunabilir. 
                Arazideki tüm ağaç türlerini ve sayılarını belirtiniz. Sistem fiili dikili durumu bu bilgilerden tespit edecektir.
              </InfoText>
            </HighlightBox>
          )}
          
          {/* "… Adetli Zeytin Ağacı bulunan + herhangi bir dikili vasıf" için özel açıklama */}
          {araziVasfi === '… Adetli Zeytin Ağacı bulunan + herhangi bir dikili vasıf' && (
            <HighlightBox $variant="info">
              <div style={{ fontWeight: '600', marginBottom: '8px' }}>
                🫒 Adetli Zeytin Ağacı + Dikili Vasıf Kontrolü
              </div>
              <InfoText>
                Zeytin ağacı bilgileri form üzerinden alınmıştır. Bu alanda zeytin dışında başka dikili vasıf ağaçları da bulunuyorsa 
                (meyve ağaçları, asma vs.) onları da ekleyiniz. Sistem toplam dikili vasıf yoğunluğunu hesaplayacaktır.
              </InfoText>
            </HighlightBox>
          )}
          
          <FormGroup>
            <Label htmlFor="agac-turu-select">Ağaç Türü</Label>
            <Select
              id="agac-turu-select"
              value={secilenAgacTuru}
              onChange={(e) => {
                updateField('secilenAgacTuru', e.target.value);
                updateField('secilenAgacTipi', 'normal');
              }}
            >
              <option value="">Ağaç türü seçin...</option>
              {(agacTuruSecimiSadeceDut
                ? agacVerileri.filter(agac => agac.tur === 'Dut')
                : agacVerileri
              )
              .sort((a, b) => a.tur.localeCompare(b.tur, 'tr'))
              .map(agac => (
                <option key={agac.sira} value={agac.sira.toString()}>
                  {agac.tur}
                </option>
              ))}
            </Select>
          </FormGroup>

          {secilenAgacTuru && (
            <FormGroup>
              <Label htmlFor="agac-tipi-select">Ağaç Tipi</Label>
              <Select
                id="agac-tipi-select"
                value={secilenAgacTipi}
                onChange={(e) => updateField('secilenAgacTipi', e.target.value as any)}
              >
                {getMevcutTipler(secilenAgacTuru).map(tip => (
                  <option key={tip.value} value={tip.value}>
                    {tip.label}
                  </option>
                ))}
              </Select>
            </FormGroup>
          )}

          <FormGroup>
            <Label htmlFor="agac-sayisi-input">Ağaç Sayısı</Label>
            <Input
              id="agac-sayisi-input"
              type="number"
              value={agacSayisi || ''}
              onChange={(e) => updateField('agacSayisi', Number(e.target.value))}
              placeholder="Ağaç sayısını girin"
              min="1"
            />
          </FormGroup>

          <Button onClick={agacEkle} $variant="success">
            ➕ Ağaç Ekle
          </Button>
        </FormSection>
      )}

      {eklenenAgaclar.length > 0 && araziVasfi !== 'Tarla + Zeytinlik' && (
        <FormSection>
          <SectionTitle>📋 Eklenen Ağaçlar</SectionTitle>
          <AgacListesi>
            {eklenenAgaclar.map((agac, index) => (
              <AgacItem key={index}>
                {editingIndex === index ? (
                  <>
                    <span>
                      <strong>{getAgacAdiById(agac.turAdi)}</strong> ({agac.tipi}) - 
                      <input
                        type="number"
                        value={editingAgacSayisi}
                        onChange={(e) => updateEditCount(Number(e.target.value))}
                        min="1"
                        style={{
                          width: '60px',
                          margin: '0 8px',
                          padding: '4px',
                          border: '1px solid #ccc',
                          borderRadius: '4px'
                        }}
                      />
                      adet
                    </span>
                    <FlexContainer $gap="4px">
                      <Button onClick={() => agacEditSave(index)} $variant="success" style={{ fontSize: '12px', padding: '4px 8px' }}>
                        ✓
                      </Button>
                      <Button onClick={agacEditCancel} $variant="secondary" style={{ fontSize: '12px', padding: '4px 8px' }}>
                        ✕
                      </Button>
                    </FlexContainer>
                  </>
                ) : (
                  <>
                    <span>
                      <strong>{getAgacAdiById(agac.turAdi)}</strong> ({agac.tipi}) - {agac.sayi} adet
                    </span>
                    <FlexContainer $gap="4px">
                      <Button onClick={() => agacEdit(index)} $variant="primary" style={{ fontSize: '12px', padding: '4px 8px' }}>
                        ✏️
                      </Button>
                      <Button onClick={() => agacSil(index)} $variant="danger" style={{ fontSize: '12px', padding: '4px 8px' }}>
                        🗑️
                      </Button>
                    </FlexContainer>
                  </>
                )}
              </AgacItem>
            ))}
          </AgacListesi>

          <FlexContainer style={{ marginTop: '16px' }}>
            <Button onClick={devamEt} $variant="primary">
              📤 Verileri Hesaplama Formuna Aktar
            </Button>
            <Button onClick={temizleVeriler} $variant="secondary">
              🗑️ Temizle
            </Button>
          </FlexContainer>
        </FormSection>
      )}
    </>
  );
};

export default ManuelTab;
