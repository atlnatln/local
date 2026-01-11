import React from 'react';
import styled from 'styled-components';

const WarningContainer = styled.div`
  background-color: #fffbe6;
  border: 1px solid #ffe58f;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 12px;
`;

const WarningIcon = styled.span`
  font-size: 24px;
  color: #faad14;
`;

const WarningText = styled.p`
  margin: 0;
  font-size: 16px;
  color: #874d00;
  line-height: 1.5;

  strong {
    font-weight: 600;
  }
`;

const WaterPermitWarning: React.FC = () => {
  return (
    <WarningContainer>
      <WarningIcon>⚠️</WarningIcon>
      <WarningText>
        <strong>Uyarı:</strong> Seçtiğiniz konum kapalı su havzası içinde yer almaktadır. 
        Su tahsis belgesi olmadan yapacağınız başvurunun ilgili kurum tarafından <strong>reddedilebileceğini</strong> unutmayın.
      </WarningText>
    </WarningContainer>
  );
};

export default WaterPermitWarning;
