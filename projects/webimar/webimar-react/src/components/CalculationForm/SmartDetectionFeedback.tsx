import React from 'react';
import { SmartDetectionFeedback as StyledFeedback, ResetToMapButton } from './styles';

interface SmartDetectionFeedbackProps {
  variant: 'manual' | 'map' | 'reset';
  icon: string;
  text: string;
  onResetToMap?: () => void;
}

const SmartDetectionFeedback: React.FC<SmartDetectionFeedbackProps> = ({
  variant,
  icon,
  text,
  onResetToMap
}) => {
  return (
    <StyledFeedback $variant={variant}>
      <span>{icon} {text}</span>
      {variant === 'manual' && onResetToMap && (
        <ResetToMapButton onClick={onResetToMap}>
          Harita bilgisini kullan
        </ResetToMapButton>
      )}
    </StyledFeedback>
  );
};

export default SmartDetectionFeedback;
