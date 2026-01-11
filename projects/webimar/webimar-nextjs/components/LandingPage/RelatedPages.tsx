import React from 'react';
import Link from 'next/link';
import styles from './RelatedPages.module.css';

interface RelatedPage {
  title: string;
  url: string;
  icon?: string;
}

interface RelatedPagesProps {
  pages: RelatedPage[];
}

const RelatedPages: React.FC<RelatedPagesProps> = ({ pages }) => {
  if (!pages || pages.length === 0) return null;

  return (
    <section className={styles.relatedPages}>
      <div className={styles.container}>
        <h2 className={styles.sectionTitle}>İlgili Hesaplamalar</h2>
        <div className={styles.pagesGrid}>
          {pages.map((page, index) => (
            <Link 
              key={index} 
              href={page.url} 
              className={styles.pageCard}
            >
              {page.icon && <div className={styles.pageIcon}>{page.icon}</div>}
              <h3 className={styles.pageTitle}>{page.title}</h3>
              <span className={styles.pageArrow}>→</span>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
};

export default RelatedPages;
