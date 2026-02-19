import { useState } from 'react';
import styled from 'styled-components';

type Props = {
  calculationType: string;
  sourceApp?: 'nextjs-pages';
};

const Wrapper = styled.section`
  margin: 0 0 20px;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  background: #ffffff;
  overflow: hidden;
`;

const HeaderButton = styled.button`
  width: 100%;
  border: none;
  background: #f8fafc;
  color: #1f2937;
  font-size: 14px;
  font-weight: 600;
  padding: 12px 14px;
  text-align: left;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;

  &:hover {
    background: #f1f5f9;
  }
`;

const Content = styled.div`
  border-top: 1px solid #e5e7eb;
  padding: 12px 14px 14px;
`;

const Description = styled.p`
  margin: 0 0 10px;
  color: #4b5563;
  font-size: 13px;
  line-height: 1.5;
`;

const TextArea = styled.textarea`
  width: 100%;
  min-height: 96px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  padding: 10px;
  box-sizing: border-box;
  font-size: 14px;
  resize: vertical;

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
  color: #6b7280;
  font-size: 12px;
`;

const SubmitButton = styled.button`
  border: none;
  border-radius: 8px;
  background: #2563eb;
  color: #ffffff;
  font-size: 13px;
  font-weight: 600;
  padding: 10px 14px;
  cursor: pointer;

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const StatusText = styled.div<{ $isError: boolean }>`
  margin-top: 8px;
  font-size: 13px;
  color: ${(props) => (props.$isError ? '#b91c1c' : '#065f46')};
`;

export default function CalculationFeedbackAccordion({ calculationType, sourceApp = 'nextjs-pages' }: Props) {
  const [isOpen, setIsOpen] = useState(false);
  const [message, setMessage] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [status, setStatus] = useState<{ text: string; isError: boolean } | null>(null);

  const handleSubmit = async () => {
    const trimmed = message.trim();
    if (trimmed.length < 5) {
      setStatus({ text: 'Lütfen en az 5 karakterlik bir geri bildirim yazın.', isError: true });
      return;
    }

    setIsSending(true);
    setStatus(null);

    try {
      const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || '/api';
      const response = await fetch(`${apiBaseUrl}/calculations/feedback/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: trimmed,
          calculation_type: calculationType,
          source_app: sourceApp,
          page_path: window.location.pathname,
        }),
      });

      const data = await response.json();
      if (!response.ok || !data?.success) {
        setStatus({ text: data?.detail || 'Geri bildirim gönderilemedi.', isError: true });
        return;
      }

      setMessage('');
      setStatus({ text: 'Teşekkürler, geri bildiriminiz alındı.', isError: false });
    } catch {
      setStatus({ text: 'Bağlantı hatası. Lütfen daha sonra tekrar deneyin.', isError: true });
    } finally {
      setIsSending(false);
    }
  };

  return (
    <Wrapper>
      <HeaderButton type="button" onClick={() => setIsOpen((prev) => !prev)}>
        <span>💬 Sistemi geliştirmemize yardımcı olun</span>
        <span>{isOpen ? '▾' : '▸'}</span>
      </HeaderButton>

      {isOpen && (
        <Content>
          <Description>Mesajınız doğrudan ekibimize iletilir.</Description>
          <TextArea
            value={message}
            onChange={(event) => setMessage(event.target.value.slice(0, 2000))}
            maxLength={2000}
            placeholder="Örn: Şu alanda daha net bir açıklama olursa çok iyi olur..."
          />
          <Footer>
            <Counter>{message.length}/2000</Counter>
            <SubmitButton type="button" disabled={isSending} onClick={handleSubmit}>
              {isSending ? 'Gönderiliyor...' : 'Geri Bildirimi Gönder'}
            </SubmitButton>
          </Footer>
          {status && <StatusText $isError={status.isError}>{status.text}</StatusText>}
        </Content>
      )}
    </Wrapper>
  );
}
