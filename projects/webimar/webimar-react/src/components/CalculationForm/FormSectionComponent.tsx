// Form Section Component for organizing form groups
import React from 'react';
import { FormSection, SectionTitle } from './styles';

interface FormSectionComponentProps {
  title?: string;
  children: React.ReactNode;
  className?: string;
}

const FormSectionComponent: React.FC<FormSectionComponentProps> = ({
  title,
  children,
  className
}) => {
  return (
    <FormSection className={className}>
      {title && <SectionTitle>{title}</SectionTitle>}
      {children}
    </FormSection>
  );
};

export default FormSectionComponent;
