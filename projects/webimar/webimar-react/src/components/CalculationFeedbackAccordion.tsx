import React, { useState } from 'react';
import styled from 'styled-components';
import { toast } from 'react-toastify';
import { submitCalculationFeedback } from '../services/api';
import { StructureType } from '../types';

type Props = {
  calculationType: StructureType;
};

const Wrapper = styled.section`
  margin-bottom: 18px;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  background: #ffffff;
  overflow: hidden;
`;

const Toggle = styled.button`
  width: 100%;
  border: none;
  background: #f8fafc;
  color: #1f2937;
  text-align: left;
  font-size: 14px;
  font-weight: 600;
  padding: 12px 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;

  &:hover {
    background: #f1f5f9;
  }
`;

const Content = styled.div`
  padding: 12px 14px 14px;
  border-top: 1px solid #e5e7eb;
`;

const Description = styled.p`
  margin: 0 0 10px 0;
  color: #4b5563;
  font-size: 13px;
  line-height: 1.5;
`;

const Textarea = styled.textarea`
  width: 100%;
  min-height: 96px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  padding: 10px;
  font-size: 14px;
  resize: vertical;
  box-sizing: border-box;

  &:focus {
    outline: none;
    border-color: #2563eb;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
  }
`;

const Footer = styled.div`
  margin-top: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
`;

const Counter = styled.span`
  font-size: 12px;
  color: #6b7280;
`;

const SendButton = styled.button`
  border: none;
  border-radius: 8px;
  padding: 10px 14px;
  background: #2563eb;
  color: #ffffff;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

export default function CalculationFeedbackAccordion({ calculationType }: Props) {
  const [isOpen, setIsOpen] = useState(false);
  const [message, setMessage] = useState('');
  const [isSending, setIsSending] = useState(false);

  const handleSend = async () => {
    const normalized = message.trim();
    if (normalized.length < 5) {
      toast.warn('Lütfen en az 5 karakterlik bir geri bildirim yazın.');
      return;
    }

    setIsSending(true);
    try {
      await submitCalculationFeedback({
        message: normalized,
        calculation_type: calculationType,
        source_app: 'react-spa',
        page_path: window.location.pathname,
      });
      setMessage('');
      toast.success('Teşekkürler, geri bildiriminiz alındı.');
    } catch (error: any) {
      const detail = error?.response?.data?.detail;
      toast.error(detail || 'Geri bildirim gönderilemedi.');
    } finally {
      setIsSending(false);
    }
  };

  return (
    <Wrapper>
      <Toggle type="button" onClick={() => setIsOpen((prev) => !prev)}>
        <span>💬 Sistemi geliştirmemize yardımcı olun</span>
        <span>{isOpen ? '▾' : '▸'}</span>
      </Toggle>

      {isOpen && (
        <Content>
          <Description>
            Deneyiminizi kısaca yazın. Mesajınız doğrudan ekibimize iletilir.
          </Description>
          <Textarea
            value={message}
            onChange={(event) => setMessage(event.target.value.slice(0, 2000))}
            placeholder="Örn: Sonuç ekranında şu bilgiyi görmek isterdim..."
            maxLength={2000}
          />
          <Footer>
            <Counter>{message.length}/2000</Counter>
            <SendButton type="button" onClick={handleSend} disabled={isSending}>
              {isSending ? 'Gönderiliyor...' : 'Geri Bildirimi Gönder'}
            </SendButton>
          </Footer>
        </Content>
      )}
    </Wrapper>
  );
}
