import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { tokenStorage } from '../utils/tokenStorage';

interface UserSession {
  session_key: string;
  ip_address: string;
  user_agent: string;
  device_info: string;
  location: string;
  login_time: string;
  last_activity: string;
  is_active: boolean;
}

interface UserSessionsResponse {
  sessions: UserSession[];
  total_count: number;
  active_count: number;
}

interface UserSessionsModalProps {
  onClose: () => void;
}

const ModalOverlay = styled.div`
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.18);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  box-sizing: border-box;
  
  @media (max-width: 768px) {
    align-items: flex-start;
    padding: 8px;
    padding-top: 60px;
  }
`;

const ModalContent = styled.div`
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.13);
  padding: 32px 24px 24px 24px;
  min-width: 600px;
  max-width: 95vw;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
  width: 100%;
  max-width: 700px;
  
  @media (max-width: 768px) {
    min-width: unset;
    max-width: 100%;
    border-radius: 8px;
    padding: 24px 16px 16px 16px;
    margin: 0 auto;
    max-height: 85vh;
  }
`;

const CloseButton = styled.button`
  position: absolute;
  top: 10px;
  right: 16px;
  background: none;
  border: none;
  font-size: 22px;
  color: #888;
  cursor: pointer;
  z-index: 1;
  
  @media (max-width: 768px) {
    top: 8px;
    right: 12px;
    font-size: 24px;
    padding: 4px;
    &:hover {
      background: rgba(0,0,0,0.1);
      border-radius: 50%;
    }
  }
`;

const SessionCard = styled.div`
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
  background: #f9fafb;
  
  @media (max-width: 768px) {
    padding: 12px;
    margin-bottom: 10px;
    border-radius: 6px;
  }
`;

const SessionInfo = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  
  @media (max-width: 768px) {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
`;

const SessionDetails = styled.div`
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 4px;
  
  @media (max-width: 768px) {
    font-size: 13px;
    margin-bottom: 3px;
  }
`;

const TerminateButton = styled.button`
  background: #dc2626;
  color: #fff;
  border: none;
  border-radius: 4px;
  padding: 6px 12px;
  font-size: 12px;
  cursor: pointer;
  &:hover {
    background: #b91c1c;
  }
`;

const CurrentSessionBadge = styled.span`
  background: #10b981;
  color: #fff;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
`;

const LoadingDiv = styled.div`
  text-align: center;
  padding: 20px;
  color: #6b7280;
`;

const ErrorMsg = styled.div`
  color: #dc2626;
  font-size: 14px;
  text-align: center;
  margin-bottom: 16px;
`;

const UserSessionsModal: React.FC<UserSessionsModalProps> = ({ onClose }) => {
  const [sessions, setSessions] = useState<UserSession[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [activeCount, setActiveCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    try {
      const token = tokenStorage.getAccessToken();
      if (!token) {
        setError('Oturum süreniz dolmuş. Lütfen tekrar giriş yapın.');
        return;
      }
      
      const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api';
      const response = await fetch(`${API_BASE_URL}/accounts/me/sessions/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data: UserSessionsResponse = await response.json();
        setSessions(data.sessions);
        setTotalCount(data.total_count);
        setActiveCount(data.active_count);
      } else {
        setError('Oturumlar yüklenemedi.');
      }
    } catch (err) {
      setError('Sunucuya bağlanılamadı.');
    } finally {
      setLoading(false);
    }
  };

  const terminateSession = async (sessionKey: string) => {
    try {
      const token = tokenStorage.getAccessToken();
      if (!token) {
        setError('Oturum süreniz dolmuş. Lütfen tekrar giriş yapın.');
        return;
      }
      
      const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api';
      const response = await fetch(`${API_BASE_URL}/accounts/me/sessions/${sessionKey}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        // Oturumu pasif olarak işaretle ve count'ları güncelle
        setSessions(prevSessions => {
          return prevSessions.map(s => 
            s.session_key === sessionKey 
              ? { ...s, is_active: false }
              : s
          );
        });
        setActiveCount(prev => prev - 1);
      } else {
        setError('Oturum sonlandırılamadı.');
      }
    } catch (err) {
      setError('Sunucuya bağlanılamadı.');
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('tr-TR');
  };

  if (loading) {
    return (
      <ModalOverlay onClick={onClose}>
        <ModalContent onClick={e => e.stopPropagation()}>
          <CloseButton onClick={onClose} title="Kapat">×</CloseButton>
          <LoadingDiv>Oturumlar yükleniyor...</LoadingDiv>
        </ModalContent>
      </ModalOverlay>
    );
  }

  return (
    <ModalOverlay onClick={onClose}>
      <ModalContent onClick={e => e.stopPropagation()}>
        <CloseButton onClick={onClose} title="Kapat">×</CloseButton>
        <h2 style={{textAlign:'center', marginBottom: 16}}>Oturum Geçmişi (Son 1 Ay)</h2>
        
        <div style={{textAlign:'center', marginBottom: 24, color: '#666', fontSize: '14px'}}>
          Toplam {totalCount} oturum • {activeCount} aktif • {totalCount - activeCount} sona ermiş
        </div>
        
        {error && <ErrorMsg>{error}</ErrorMsg>}
        
        {sessions.length === 0 ? (
          <LoadingDiv>Son 1 ayda oturum bulunamadı.</LoadingDiv>
        ) : (
          sessions.map((session, index) => (
            <SessionCard key={session.session_key}>
              <SessionInfo>
                <div>
                  <strong>IP: {session.ip_address}</strong>
                  {session.is_active && <CurrentSessionBadge>Aktif</CurrentSessionBadge>}
                  {!session.is_active && <span style={{color: '#888', fontSize: '12px', marginLeft: '8px'}}>Sona ermiş</span>}
                </div>
                {session.is_active && (
                  <TerminateButton onClick={() => terminateSession(session.session_key)}>
                    Oturumu Sonlandır
                  </TerminateButton>
                )}
              </SessionInfo>
              <SessionDetails>
                <div><strong>Cihaz:</strong> {session.device_info || 'Bilinmeyen'}</div>
                <div><strong>Konum:</strong> {session.location || 'Bilinmeyen'}</div>
                <div><strong>Giriş:</strong> {formatDate(session.login_time)}</div>
                <div><strong>Son Aktivite:</strong> {formatDate(session.last_activity)}</div>
                <div><strong>Durum:</strong> <span style={{color: session.is_active ? '#059669' : '#888'}}>{session.is_active ? 'Aktif' : 'Sona ermiş'}</span></div>
              </SessionDetails>
            </SessionCard>
          ))
        )}
      </ModalContent>
    </ModalOverlay>
  );
};

export default UserSessionsModal;
