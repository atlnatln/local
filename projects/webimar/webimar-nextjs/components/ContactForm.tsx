import React, { useState } from 'react';
import styles from '../styles/ContactForm.module.css';

const ContactForm = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [status, setStatus] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isAgreed, setIsAgreed] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setStatus('Gönderiliyor...');
    
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api';
      const response = await fetch(`${apiUrl}/accounts/contact/`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json' 
        },
        body: JSON.stringify({ name, email, message })
      });
      
      const data = await response.json();
      
      if (data.success) {
        setStatus('✅ Mesajınız başarıyla gönderildi! En kısa sürede size dönüş yapacağız.');
        setName('');
        setEmail('');
        setMessage('');
      } else {
        setStatus('❌ Hata oluştu: ' + (data.detail || 'Bilinmeyen bir hata oluştu.'));
      }
    } catch (error) {
      console.error('Contact form error:', error);
      setStatus('❌ Bağlantı hatası. Lütfen daha sonra tekrar deneyin.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.contactSection} id="contact-section">
      <div className={styles.contactContainer}>
        <h2>İletişim</h2>
        <p>Sorularınız, önerileriniz veya destek ihtiyaçlarınız için bize ulaşın.</p>
        
        <form onSubmit={handleSubmit} className={styles.contactForm}>
          <div className={styles.formGroup}>
            <label htmlFor="name">Adınız Soyadınız</label>
            <input
              id="name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Adınız ve soyadınızı yazın"
              required
              disabled={isLoading}
              className={styles.formInput}
            />
          </div>
          
          <div className={styles.formGroup}>
            <label htmlFor="email">E-posta Adresiniz</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="ornek@email.com"
              required
              disabled={isLoading}
              className={styles.formInput}
            />
          </div>
          
          <div className={styles.formGroup}>
            <label htmlFor="message">Mesajınız</label>
            <textarea
              id="message"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Mesajınızı buraya yazın..."
              required
              disabled={isLoading}
              rows={5}
              className={styles.formTextarea}
            />
          </div>

          <div className={styles.formGroup}>
            <div className={styles.checkboxContainer}>
              <input
                type="checkbox"
                id="kvkk-consent"
                checked={isAgreed}
                onChange={(e) => setIsAgreed(e.target.checked)}
                required
                className={styles.checkbox}
              />
              <label htmlFor="kvkk-consent" className={styles.checkboxLabel}>
                <a href="/kvkk-aydinlatma" target="_blank" className={styles.link}>KVKK Aydınlatma Metni</a>'ni okudum ve kabul ediyorum.
              </label>
            </div>
          </div>
          
          <button 
            type="submit" 
            disabled={isLoading || !isAgreed}
            className={styles.submitButton}
          >
            {isLoading ? 'Gönderiliyor...' : 'Mesajı Gönder'}
          </button>
          
          {status && (
            <div className={`${styles.statusMessage} ${
              status.includes('✅') ? styles.success : styles.error
            }`}>
              {status}
            </div>
          )}
        </form>
      </div>
    </div>
  );
};

export default ContactForm;
