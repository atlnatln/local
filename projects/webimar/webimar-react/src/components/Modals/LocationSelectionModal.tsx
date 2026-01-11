import React from 'react';
import styled from 'styled-components';

interface LocationSelectionModalProps {
  isOpen: boolean;
  onClose: () => void;
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
  z-index: 1000;
`;

const ModalContent = styled.div`
  background: white;
  border-radius: 12px;
  padding: 24px;
  max-width: 500px;
  width: 90%;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  text-align: center;
`;

const ModalTitle = styled.h3`
  color: #2563eb;
  margin: 0 0 16px 0;
  font-size: 20px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
`;

const ModalText = styled.p`
  color: #64748b;
  line-height: 1.6;
  margin: 0 0 20px 0;
  font-size: 16px;
`;

const InstructionList = styled.ul`
  list-style: none;
  padding: 0;
  margin: 16px 0;
  text-align: left;
`;

const InstructionItem = styled.li`
  color: #374151;
  margin: 8px 0;
  padding: 8px 12px;
  background: #f8fafc;
  border-radius: 6px;
  border-left: 3px solid #3b82f6;
  font-size: 14px;
`;

const CloseButton = styled.button`
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;

  &:hover {
    background: #2563eb;
  }
`;

const LocationSelectionModal: React.FC<LocationSelectionModalProps> = ({ isOpen, onClose }) => {
  return (
    <ModalOverlay $isOpen={isOpen} onClick={onClose}>
      <ModalContent onClick={(e) => e.stopPropagation()}>
        <ModalTitle>
          🗺️ Önce Harita Noktası Seçin
        </ModalTitle>
        
        <ModalText>
          Hesaplama yapabilmek için öncelikle harita üzerinden arazinizin konumunu seçmeniz gerekiyor.
        </ModalText>
        
        <InstructionList>
          <InstructionItem>
            📍 Yukarıdaki harita üzerinde arazinizin bulunduğu noktaya tıklayın
          </InstructionItem>
          <InstructionItem>
            🔍 İlçe/mahalle arama kutusunu kullanarak konumunuzu kolayca bulabilirsiniz
          </InstructionItem>
          <InstructionItem>
            ✅ Nokta seçildikten sonra hesaplama formu aktif hale gelecektir
          </InstructionItem>
        </InstructionList>

        <CloseButton onClick={onClose}>
          Anladım
        </CloseButton>
      </ModalContent>
    </ModalOverlay>
  );
};

export default LocationSelectionModal;
