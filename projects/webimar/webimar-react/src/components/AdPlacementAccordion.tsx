/**
 * AdPlacementAccordion — İl Bazlı Reklam Alanı Bileşeni
 *
 * Hesaplama sonucu başarılı geldiğinde, seçilen ile göre:
 * - Aktif reklam veren varsa → açık akordionla reklam kartları gösterilir.
 * - Aktif reklam veren yoksa → kapalı akordionla "Buraya reklam verebilirsiniz" CTA'sı gösterilir.
 *
 * İl bilgisi: LocationValidationContext → kmlCheckResult.province
 */

import React, { useState, useMemo } from 'react';
import styled, { css, keyframes } from 'styled-components';
import { AdPlacementProps, Advertiser, CATEGORY_LABELS } from '../types/ads';
import {
  getActiveAdvertisersForProvince,
  AD_CONTACT_INFO,
} from '../constants/adsConfig';

/* ─────────────── Styled Components ─────────────── */

const fadeIn = keyframes`
  from { opacity: 0; transform: translateY(-6px); }
  to   { opacity: 1; transform: translateY(0); }
`;

const Wrapper = styled.section`
  margin-top: 20px;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  background: #ffffff;
  overflow: hidden;
  transition: box-shadow 0.2s ease;

  &:hover {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  }
`;

const Toggle = styled.button<{ $hasAds: boolean }>`
  width: 100%;
  border: none;
  text-align: left;
  font-size: 14px;
  font-weight: 600;
  padding: 14px 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  transition: background 0.15s ease;

  ${({ $hasAds }) =>
    $hasAds
      ? css`
          background: linear-gradient(135deg, #eff6ff, #dbeafe);
          color: #1e40af;
          &:hover { background: linear-gradient(135deg, #dbeafe, #bfdbfe); }
        `
      : css`
          background: #f8fafc;
          color: #64748b;
          &:hover { background: #f1f5f9; }
        `}

  @media (max-width: 768px) {
    padding: 12px 14px;
    font-size: 13px;
  }
`;

const ToggleLeft = styled.span`
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
`;

const ProvinceBadge = styled.span`
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: rgba(37, 99, 235, 0.1);
  color: #2563eb;
  font-size: 12px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 12px;
  white-space: nowrap;

  @media (max-width: 768px) {
    font-size: 11px;
    padding: 2px 6px;
  }
`;

const Chevron = styled.span<{ $isOpen: boolean }>`
  display: inline-flex;
  transition: transform 0.25s ease;
  transform: rotate(${({ $isOpen }) => ($isOpen ? '180deg' : '0deg')});
  font-size: 16px;
  flex-shrink: 0;
`;

const Content = styled.div`
  border-top: 1px solid #e5e7eb;
  animation: ${fadeIn} 0.2s ease;
`;

/* ─── Reklam Veren Yok / CTA Durumu ─── */

const CTAContainer = styled.div`
  padding: 20px 16px;
  text-align: center;
`;

const CTAIcon = styled.div`
  font-size: 32px;
  margin-bottom: 8px;
`;

const CTATitle = styled.h4`
  margin: 0 0 6px;
  font-size: 15px;
  font-weight: 600;
  color: #374151;
`;

const CTADescription = styled.p`
  margin: 0 0 12px;
  font-size: 13px;
  color: #6b7280;
  line-height: 1.5;
`;

const CTAButton = styled.a`
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: #ffffff;
  font-size: 13px;
  font-weight: 600;
  padding: 10px 20px;
  border-radius: 8px;
  text-decoration: none;
  transition: all 0.2s ease;

  &:hover {
    background: linear-gradient(135deg, #1d4ed8, #1e3a8a);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
  }

  &:active {
    transform: translateY(0);
  }
`;

/* ─── Reklam Veren Var Durumu ─── */

const AdsGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
  padding: 16px;

  @media (min-width: 640px) {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  }
`;

const AdCard = styled.div`
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 16px;
  background: #f8fafc;
  display: flex;
  flex-direction: column;
  gap: 8px;
  transition: all 0.2s ease;

  &:hover {
    border-color: #93c5fd;
    box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1);
    transform: translateY(-1px);
  }
`;

const AdCardHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
`;

const AdName = styled.h4`
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: #111827;
`;

const CategoryTag = styled.span`
  display: inline-flex;
  align-items: center;
  font-size: 11px;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: 10px;
  background: #e0f2fe;
  color: #0369a1;
  white-space: nowrap;
`;

const AdDescription = styled.p`
  margin: 0;
  font-size: 13px;
  color: #4b5563;
  line-height: 1.5;
`;

const AdActions = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 4px;
  flex-wrap: wrap;
`;

const AdLink = styled.a`
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  font-weight: 500;
  color: #2563eb;
  text-decoration: none;

  &:hover {
    text-decoration: underline;
  }
`;

const SponsoredLabel = styled.div`
  padding: 6px 16px;
  text-align: right;
  font-size: 11px;
  color: #9ca3af;
  font-style: italic;
  border-top: 1px solid #f3f4f6;
`;

/* ─────────────── Component ─────────────── */

export default function AdPlacementAccordion({
  selectedProvince,
  calculationType,
}: AdPlacementProps) {
  const activeAds = useMemo(
    () => getActiveAdvertisersForProvince(selectedProvince),
    [selectedProvince]
  );

  const hasAds = activeAds.length > 0;

  const [isOpen, setIsOpen] = useState(hasAds); // Reklam varsa açık, yoksa kapalı

  // İl bilgisi yoksa render etme
  if (!selectedProvince) return null;

  const toggleLabel = hasAds
    ? `📢 ${selectedProvince} bölgesinde hizmet verenler`
    : '📢 Bölgesel Tanıtım ve İş Ortaklığı Alanı';

  return (
    <Wrapper>
      <Toggle
        type="button"
        $hasAds={hasAds}
        onClick={() => setIsOpen(prev => !prev)}
        aria-expanded={isOpen}
      >
        <ToggleLeft>
          <span>{toggleLabel}</span>
          {selectedProvince && (
            <ProvinceBadge>
              📍 {selectedProvince}
            </ProvinceBadge>
          )}
        </ToggleLeft>
        <Chevron $isOpen={isOpen}>▾</Chevron>
      </Toggle>

      {isOpen && (
        <Content>
          {hasAds ? (
            <>
              <AdsGrid>
                {activeAds.map((ad: Advertiser) => (
                  <AdCard key={ad.id}>
                    <AdCardHeader>
                      <AdName>{ad.name}</AdName>
                      <CategoryTag>
                        {CATEGORY_LABELS[ad.category]}
                      </CategoryTag>
                    </AdCardHeader>

                    <AdDescription>{ad.description}</AdDescription>

                    <AdActions>
                      {ad.phone && (
                        <AdLink href={`tel:${ad.phone.replace(/\s/g, '')}`}>
                          📞 {ad.phone}
                        </AdLink>
                      )}
                      {ad.website && (
                        <AdLink
                          href={ad.website}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          🌐 Web Sitesi
                        </AdLink>
                      )}
                    </AdActions>
                  </AdCard>
                ))}
              </AdsGrid>
              <SponsoredLabel>Sponsorlu içerik</SponsoredLabel>
            </>
          ) : (
            <CTAContainer>
              <CTAIcon>📍</CTAIcon>
              <CTATitle>
                {selectedProvince} bölgesinde reklam verin
              </CTATitle>
              <CTADescription>
                {selectedProvince} ilinde tarımsal yapı hesaplaması yapan
                kullanıcılara hizmetlerinizi tanıtın.
                <br />
                Emlakçılar, şehir planlamacıları, ziraat mühendisleri ve daha fazlası
                için uygun reklam alanı.                              
              </CTADescription>
              <CTAButton href={`mailto:${AD_CONTACT_INFO.email}?subject=${encodeURIComponent(`Reklam Talebi - ${selectedProvince}`)}&body=${encodeURIComponent(`Merhaba,\n\n${selectedProvince} ili için reklam vermek istiyorum.\n\nFirma Adı:\nFaaliyet Alanı:\nİletişim:\n`)}`}>
                ✉️ Reklam Vermek İstiyorum
              </CTAButton>
            </CTAContainer>
          )}
        </Content>
      )}
    </Wrapper>
  );
}
