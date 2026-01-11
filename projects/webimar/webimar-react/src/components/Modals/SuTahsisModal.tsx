import React, { useState } from 'react';
import styled from 'styled-components';

interface SuTahsisModalProps {
  isOpen: boolean;
  onClose: () => void;
  onResponse: (hasSuTahsis: boolean) => void;
  calculationType?: string;
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
  max-width: 700px;
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

const AlertCard = styled.div`
  background: linear-gradient(135deg, #fef3c7, #fde68a);
  border: 2px solid #f59e0b;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 24px;
`;

const AlertText = styled.p`
  margin: 0;
  color: #92400e;
  font-weight: 500;
  line-height: 1.5;
`;

const QuestionSection = styled.div`
  background: #f8fafc;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 24px;
  border-left: 4px solid #3b82f6;
`;

const QuestionTitle = styled.h3`
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 600;
  color: #1e40af;
`;

const QuestionText = styled.p`
  margin: 0 0 20px 0;
  color: #374151;
  font-size: 16px;
  line-height: 1.5;
`;

const ButtonContainer = styled.div`
  display: flex;
  gap: 12px;
  justify-content: center;
`;

const ResponseButton = styled.button<{ $variant: 'yes' | 'no' }>`
  padding: 12px 32px;
  border-radius: 8px;
  border: none;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 120px;
  
  ${props => props.$variant === 'yes' ? `
    background: linear-gradient(135deg, #10b981, #059669);
    color: white;
    
    &:hover {
      background: linear-gradient(135deg, #059669, #047857);
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    }
  ` : `
    background: linear-gradient(135deg, #ef4444, #dc2626);
    color: white;
    
    &:hover {
      background: linear-gradient(135deg, #dc2626, #b91c1c);
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
    }
  `}
`;

const LegalSection = styled.div`
  background: #f1f5f9;
  border-radius: 8px;
  padding: 20px;
  border-left: 4px solid #64748b;
  margin-top: 24px;
`;

const LegalTitle = styled.h4`
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #475569;
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const LegalText = styled.div`
  color: #475569;
  font-size: 13px;
  line-height: 1.6;
  
  p {
    margin: 0 0 8px 0;
  }
  
  strong {
    color: #334155;
    font-weight: 600;
  }
`;

const SuTahsisModal: React.FC<SuTahsisModalProps> = ({ 
  isOpen, 
  onClose, 
  onResponse,
  calculationType 
}) => {
  const [showResult, setShowResult] = useState(false);
  const [userResponse, setUserResponse] = useState<boolean | null>(null);

  const handleResponse = (hasSuTahsis: boolean) => {
    setUserResponse(hasSuTahsis);
    setShowResult(true);
    onResponse(hasSuTahsis);
    
    if (!hasSuTahsis) {
      // Su tahsis belgesi yoksa modal açık kalır, kullanıcı reddi görebilir
      return;
    }
    
    // Su tahsis belgesi varsa modal kapanır
    setTimeout(() => {
      handleClose();
    }, 2000);
  };

  const handleClose = () => {
    setShowResult(false);
    setUserResponse(null);
    onClose();
  };

  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      handleClose();
    }
  };

  return (
    <ModalOverlay $isOpen={isOpen} onClick={handleOverlayClick}>
      <ModalContent>
        <ModalHeader>
          <ModalTitle>
            💧 Kapalı Su Havzası Kontrol
          </ModalTitle>
          <CloseButton onClick={handleClose}>×</CloseButton>
        </ModalHeader>
        
        <ModalBody>
          <AlertCard>
            <AlertText>
              📍 Seçtiğiniz konum <strong>kapalı su havzası</strong> içerisinde bulunmaktadır. 
              Bu bölgede {calculationType} kurabilmek için özel izinler gereklidir.
            </AlertText>
          </AlertCard>

          {!showResult ? (
            <QuestionSection>
              <QuestionTitle>💧 Su Tahsis Belgesi Kontrolü</QuestionTitle>
              <QuestionText>
                Hayvancılık tesisleri ve tarımsal ürün yıkama tesisleri için gerekli olan 
                <strong> su tahsis belgeniz </strong> bulunmakta mıdır?
              </QuestionText>
              
              <ButtonContainer>
                <ResponseButton 
                  $variant="yes" 
                  onClick={() => handleResponse(true)}
                >
                  ✅ Evet, Var
                </ResponseButton>
                <ResponseButton 
                  $variant="no" 
                  onClick={() => handleResponse(false)}
                >
                  ❌ Hayır, Yok
                </ResponseButton>
              </ButtonContainer>
            </QuestionSection>
          ) : (
            <QuestionSection>
              {userResponse ? (
                <div>
                  <QuestionTitle style={{ color: '#059669' }}>
                    ✅ Su Tahsis Belgesi Mevcut
                  </QuestionTitle>
                  <QuestionText style={{ color: '#047857' }}>
                    Su tahsis belgeniz bulunduğu için işleminize devam edebilirsiniz. 
                    Modal otomatik olarak kapanacaktır.
                  </QuestionText>
                </div>
              ) : (
                <div>
                  <QuestionTitle style={{ color: '#dc2626' }}>
                    ❌ İzin Verilemez
                  </QuestionTitle>
                  <QuestionText style={{ color: '#b91c1c' }}>
                    <strong>Su tahsis belgesi bulunmadığı için</strong> seçtiğiniz bölgede 
                    {calculationType} kurmanıza izin verilemez. Öncelikle gerekli su tahsis 
                    belgesini almanız gerekmektedir.
                  </QuestionText>
                </div>
              )}
            </QuestionSection>
          )}

          <LegalSection>
            <LegalTitle>📋 Yasal Dayanak - Genelge Hükümleri</LegalTitle>
            <LegalText>
              <p>
                <strong>Kapalı Su Havzalarında Su Tahsisi ile İlgili Özel Hüküm:</strong>
              </p>
              <p>
                Kanunun 13 ve 14'üncü maddeleri kapsamında Afyonkarahisar, Aksaray, Amasya, 
                Ankara, Antalya, Aydın, Balıkesir, Burdur, Bursa, Çanakkale, Çorum, Denizli, 
                Edirne, Elazığ, Erzurum, Hatay, İstanbul, İzmir, Karaman, Kayseri, Kırklareli, 
                Kırşehir, Kocaeli, Konya, Manisa, Mardin, Mersin, Muğla, Muş, Nevşehir, Niğde, 
                Sakarya, Şanlıurfa, Tekirdağ, Uşak, Yalova, Yozgat illeri sınırları içinde 
                yapılmak istenen ve Devlet Su İşleri Genel Müdürlüğü tarafından kapalı su havzası 
                olarak ilan edilen su kısıtının bulunduğu arazilerde...
              </p>
              <p>
                <strong>
                  1'inci fıkrada belirtilen hayvancılık tesisleri ile tarımsal ürün yıkama 
                  tesislerinin ihtiyaç duyduğu suyun şebeke suyundan karşılanacak olması 
                  durumunda ilgili idareden (il özel idaresi veya belediyelerden) şebeke 
                  suyunun kullanılabileceğine dair yazının veya kaynağının yer altı ve 
                  yer üstü sular olması durumunda ise "Su Tahsisleri Hakkında Yönetmelik" 
                  gereği ilgili DSİ'den suyun tahsis edilebileceğine dair yazının talep 
                  sahibi tarafından alınarak müracaat dosyasına eklenmelidir.
                </strong>
              </p>
              <p>
                <strong>
                  Hayvancılık tesisleri için gerekli olan suyun taşıma su ile karşılanacağının 
                  belirtilmesi durumunda, kabul edilmemelidir.
                </strong>
              </p>
            </LegalText>
          </LegalSection>
        </ModalBody>
      </ModalContent>
    </ModalOverlay>
  );
};

export default SuTahsisModal;
