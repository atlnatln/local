import React from 'react';
import styles from './Requirements.module.css';

interface LegalRequirements {
  minArea?: number;
  minAreaUnit?: string;
  maxBuildingArea?: number;
  maxFloorArea?: number;
  restrictions: string[];
  genelge: string[];
  specialConditions?: string[];
}

interface TechnicalRequirements {
  specifications: string[];
  capacity?: {
    unit: string;
    perUnit?: number;
    minCapacity?: number;
    maxCapacity?: number;
  };
  materials?: string[];
  infrastructure?: string[];
}

interface RequirementsProps {
  legal: LegalRequirements;
  technical?: TechnicalRequirements;
}

const Requirements: React.FC<RequirementsProps> = ({ legal, technical }) => {
  const hasTechnical = Boolean(
    technical && (
      technical.capacity ||
      (technical.specifications && technical.specifications.length > 0) ||
      (technical.materials && technical.materials.length > 0) ||
      (technical.infrastructure && technical.infrastructure.length > 0)
    )
  );
  return (
    <section className={styles.requirements}>
      <div className={styles.container}>
        <h2 className={styles.sectionTitle}>Gereksinimler ve Koşullar</h2>
        
        <div className={styles.requirementsGrid}>
          {/* Yasal Gereksinimler */}
          <div className={styles.requirementCard}>
            <div className={styles.cardHeader}>
              <span className={styles.cardIcon}>⚖️</span>
              <h3 className={styles.cardTitle}>Yasal Gereksinimler</h3>
            </div>
            <div className={styles.cardContent}>
              {legal.minArea && (
                <div className={styles.requirement}>
                  <strong>Minimum Alan:</strong> {legal.minArea} {legal.minAreaUnit || 'm²'}
                </div>
              )}
              {legal.maxFloorArea && (
                <div className={styles.requirement}>
                  <strong>Maksimum Taban Alanı:</strong> {legal.maxFloorArea} m²
                </div>
              )}
              {legal.maxBuildingArea && (
                <div className={styles.requirement}>
                  <strong>Maksimum İnşaat Alanı:</strong> {legal.maxBuildingArea} m²
                </div>
              )}
              
              {legal.restrictions.length > 0 && (
                <div className={styles.list}>
                  <strong>Kısıtlamalar:</strong>
                  <ul>
                    {legal.restrictions.map((restriction, index) => (
                      <li key={index}>{restriction}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {legal.specialConditions && legal.specialConditions.length > 0 && (
                <div className={styles.list}>
                  <strong>Özel Koşullar:</strong>
                  <ul>
                    {legal.specialConditions.map((condition, index) => (
                      <li key={index}>{condition}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>

          {/* Teknik Gereksinimler */}
          {hasTechnical && (
          <div className={styles.requirementCard}>
            <div className={styles.cardHeader}>
              <span className={styles.cardIcon}>🔧</span>
              <h3 className={styles.cardTitle}>Teknik Gereksinimler</h3>
            </div>
            <div className={styles.cardContent}>
              {technical?.capacity && (
                <div className={styles.requirement}>
                  <strong>Kapasite:</strong>
                  {technical.capacity.perUnit && (
                    <span> {technical.capacity.perUnit} m² / {technical.capacity.unit}</span>
                  )}
                  {technical.capacity.minCapacity && (
                    <span> (Min: {technical.capacity.minCapacity} {technical.capacity.unit})</span>
                  )}
                </div>
              )}
              
              {technical?.specifications && technical.specifications.length > 0 && (
                <div className={styles.list}>
                  <strong>Teknik Özellikler:</strong>
                  <ul>
                    {technical.specifications.map((spec, index) => (
                      <li key={index}>{spec}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {technical?.materials && technical.materials.length > 0 && (
                <div className={styles.list}>
                  <strong>Malzeme Gereksinimleri:</strong>
                  <ul>
                    {technical.materials.map((material, index) => (
                      <li key={index}>{material}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {technical?.infrastructure && technical.infrastructure.length > 0 && (
                <div className={styles.list}>
                  <strong>Altyapı İhtiyaçları:</strong>
                  <ul>
                    {technical.infrastructure.map((infra, index) => (
                      <li key={index}>{infra}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
          )}
        </div>

        {/* Genelge Bilgileri */}
        {legal.genelge.length > 0 && (
          <div className={styles.genelgeCard}>
            <div className={styles.cardHeader}>
              <span className={styles.cardIcon}>📋</span>
              <h3 className={styles.cardTitle}>Mevzuat ve Genelge</h3>
            </div>
            <div className={styles.cardContent}>
              <ul className={styles.genelgeList}>
                {legal.genelge.map((item, index) => (
                  <li key={index}>{item}</li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>
    </section>
  );
};

export default Requirements;
