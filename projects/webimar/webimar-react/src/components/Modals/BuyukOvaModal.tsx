import React, { useRef } from 'react';
import styled from 'styled-components';
import { MapContainer, TileLayer, Marker } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Leaflet marker icon fix
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

interface BuyukOvaModalProps {
  isOpen: boolean;
  onClose: () => void;
  calculationType?: string;
  selectedPoint?: { lat: number; lng: number } | null;
}

const ModalOverlay = styled.div<{ $isOpen: boolean }>`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: ${props => props.$isOpen ? 'flex' : 'none'};
  align-items: center;
  justify-content: center;
  z-index: 10001;
  padding: 20px;
`;

const ModalContent = styled.div`
  background: white;
  border-radius: 12px;
  max-width: 600px;
  width: 100%;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
`;

const ModalHeader = styled.div`
  padding: 24px 24px 16px 24px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const ModalTitle = styled.h2`
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #111827;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #6b7280;
  transition: color 0.2s;
  
  &:hover {
    color: #374151;
  }
`;

const ModalBody = styled.div`
  padding: 24px;
`;

const InfoCard = styled.div`
  background: linear-gradient(135deg, #fffbeb, #fef3c7);
  border: 2px solid #f59e0b;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
`;

const InfoText = styled.p`
  margin: 0 0 12px 0;
  color: #92400e;
  font-weight: 500;
  line-height: 1.5;
`;

const WarningCard = styled.div`
  background: linear-gradient(135deg, #fef2f2, #fecaca);
  border: 2px solid #ef4444;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
`;

const WarningText = styled.p`
  margin: 0;
  color: #991b1b;
  font-weight: 500;
  line-height: 1.5;
`;

const LegalSection = styled.div`
  background: #f8fafc;
  border-radius: 8px;
  padding: 20px;
  border-left: 4px solid #3b82f6;
`;

const LegalTitle = styled.h3`
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #1e40af;
`;

const LegalText = styled.div`
  color: #374151;
  font-size: 14px;
  line-height: 1.6;
  
  p {
    margin: 0 0 12px 0;
  }
  
  strong {
    color: #111827;
    font-weight: 600;
  }
`;

const MapSection = styled.div`
  margin: 20px 0;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e5e7eb;
  
  .leaflet-container {
    height: 200px;
    width: 100%;
  }
`;

const MapTitle = styled.h4`
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  display: flex;
  align-items: center;
  gap: 6px;
`;

const BuyukOvaModal: React.FC<BuyukOvaModalProps> = ({ 
  isOpen, 
  onClose, 
  calculationType,
  selectedPoint
}) => {
  const mapRef = useRef<L.Map | null>(null);

  // Bağ evi ve sera hariç diğer yapılar için alternatif alan uyarısı
  const showAlternativeWarning = calculationType && 
    !['bag-evi', 'sera'].includes(calculationType);

  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <ModalOverlay $isOpen={isOpen} onClick={handleOverlayClick}>
      <ModalContent>
        <ModalHeader>
          <ModalTitle>
            🌾 Büyük Ova Koruma Alanı Bilgilendirmesi
          </ModalTitle>
          <CloseButton onClick={onClose}>×</CloseButton>
        </ModalHeader>
        
        <ModalBody>
          <InfoCard>
            <InfoText>
              📍 Harita üzerinde seçtiğiniz nokta <strong>büyük ova koruma alanı</strong> içerisinde 
              kaldığı için işlemler normalden daha uzun sürecektir.
            </InfoText>
          </InfoCard>

          {showAlternativeWarning && (
            <WarningCard>
              <WarningText>
                ⚠️ Harita üzerinden seçtiğiniz yerdeki arazinizin alternatifi büyük ova dışında 
                bulunuyorsa talebiniz reddedilecektir.
              </WarningText>
            </WarningCard>
          )}

          <LegalSection>
            <LegalTitle>📋 5403 Sayılı Kanun - Madde 14</LegalTitle>
            <LegalText>
              <p>
                <strong>Büyük Ovalar ve Koruma İlkeleri:</strong>
              </p>
              <p>
                Tarımsal üretim potansiyeli yüksek, erozyon, kirlenme, amaç dışı veya yanlış 
                kullanımlar gibi çeşitli nedenlerle toprak kaybı ve arazi bozulmalarının hızlı 
                geliştiği ovalar; kurul veya kurulların görüşü alınarak, Cumhurbaşkanı kararı 
                ile büyük ova koruma alanı olarak belirlenir.
              </p>
              <p>
                <strong>
                  Büyük ovalarda bulunan tarım arazileri hiçbir surette amacı dışında kullanılamaz. 
                  Ancak alternatif alan bulunmaması, kurul veya kurullarca uygun görüş bildirilmesi 
                  şartıyla;
                </strong>
              </p>
              <p>
                a) Tarımsal amaçlı yapılar,<br/>
                b) Bakanlık ve talebin ilgili olduğu Bakanlıkça ortaklaşa kamu yararı kararı 
                alınmış faaliyetler,<br/>
                İçin tarım dışı kullanımlara Bakanlıkça izin verilebilir.
              </p>
              <p>
                Bu madde kapsamında izin verilen yerler, yeniden izin alınmaksızın bu amaç 
                dışında kullanılamaz ve planlanamaz.
              </p>
            </LegalText>
          </LegalSection>

          {/* Seçilen nokta haritası - tüm yapı türleri için göster */}
          {selectedPoint && (
            <>
              <MapTitle>
                📍 Seçtiğiniz Konum
              </MapTitle>
              <MapSection>
                <MapContainer
                  center={[selectedPoint.lat, selectedPoint.lng]}
                  zoom={15}
                  style={{ height: '100%', width: '100%' }}
                  ref={mapRef}
                  whenReady={() => {
                    console.log('🗺️ Modal haritası hazır');
                    if (mapRef.current) {
                      // Modal açıldıktan sonra zoom yap
                      setTimeout(() => {
                        if (mapRef.current) {
                          mapRef.current.setView([selectedPoint.lat, selectedPoint.lng], 18);
                          console.log('🗺️ Modal haritası zoom yapıldı:', selectedPoint);
                        }
                      }, 100);
                    }
                  }}
                >
                  <TileLayer
                    url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                    attribution='&copy; <a href="https://www.esri.com/">Esri</a>'
                  />
                  <Marker 
                    position={[selectedPoint.lat, selectedPoint.lng]}
                    eventHandlers={{
                      add: () => {
                        // Marker eklendiğinde haritayı merkeze odakla
                        console.log('🗺️ Modal haritası marker eklendi - Zoom: 18');
                      }
                    }}
                  />
                </MapContainer>
              </MapSection>
            </>
          )}

          {showAlternativeWarning && (
            <LegalSection style={{ marginTop: '16px' }}>
              <LegalTitle>🔍 Alternatif Alan Değerlendirmesi</LegalTitle>
              <LegalText>
                <p>
                  <strong>Tarımsal amaçlı yapı talepleri için</strong>, büyük ova koruma alanlarında 
                  alternatif alan değerlendirmesinde, talebin öncelikle ova sınırları dışındaki 
                  yatırımcıya ait arazilerden karşılanması esastır.
                </p>
                <p>
                  Talebin büyük ova koruma alanı dışından karşılanamaması durumunda, alternatif 
                  alanlar öncelikle büyük ova sınırları içerisinde kalan ve bu amaç için planlı 
                  alanlarda uygun yer bulunup bulunmadığına bakılır.
                </p>
                <p>
                  Uygun alan bulunmaması halinde, gerçek veya tüzel kişiler için, aynı ilçe idari 
                  sınırları içerisinde büyük ova koruma alanı dışında ve/veya büyük ova koruma 
                  alanı içinde tarımsal üretim potansiyeli düşük alanlarda arazisinin bulunmaması 
                  durumunda ise bu tür talepler için <strong>alternatif alan bulunmadığı kabul edilir</strong>.
                </p>
                <p>
                  <em>Not: Alternatif alan araştırmasında hisseli parseller değerlendirmeye alınmaz.</em>
                </p>
              </LegalText>
            </LegalSection>
          )}
        </ModalBody>
      </ModalContent>
    </ModalOverlay>
  );
};

export default BuyukOvaModal;
