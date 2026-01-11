// Özel form alanları (Sera, Silo ve Su Tahsis Belgesi) yönetimi
const SpecialFormFields = {
  /**
   * Su tahsis belgesi sorusunun görünürlüğünü kontrol et
   */
  updateSuTahsisBelgesiVisibility() {
    const yapiTuruSelect = Utils.getElement(CONFIG.selectors.form.yapiTuru);
    const suTahsisBelgesiGroup = Utils.getElement(
      CONFIG.selectors.suTahsisBelgesi,
    );

    if (!yapiTuruSelect || !suTahsisBelgesiGroup) return;

    const selectedIndex = yapiTuruSelect.selectedIndex;
    let selectedYapiTuruText =
      selectedIndex > -1 ? yapiTuruSelect.options[selectedIndex].text : null;

    if (selectedYapiTuruText) {
      const parts = selectedYapiTuruText.split(" - ");
      selectedYapiTuruText =
        parts.length > 1 ? parts.slice(1).join(" - ") : parts[0];
    }

    // --- YENİ: Hiçbir uyarı/soru gösterilmeyecek türler ---
    const noWarningTypes = [
      "Açıkta meyve/sebze kurutma alanı",
      "Hububat, çeltik, ayçiçeği kurutma tesisi",
      "Mantar Üretim Tesisi",
      "Arıcılık tesisleri",
      "Zeytinyağı Fabrikası", // Zeytinyağı Fabrikası eklendi
      "Bağ evi" // Bağ evi için su tahsis belgesi sorulmamalı
    ];
    if (selectedYapiTuruText && noWarningTypes.includes(selectedYapiTuruText)) {
      // Uyarı/soru DOM'dan kaldır
      this.hideSuTahsisBelgesiQuestion(suTahsisBelgesiGroup);
      // Eski uyarı mesajlarını da kaldır
      const existingInfo = suTahsisBelgesiGroup.querySelector(
        ".hayvancilik-su-tahsis-info",
      );
      if (existingInfo) existingInfo.remove();
      return;
    }

    // İpek böcekçiliği tesisi için özel kontrol - her durumda dut bahçesi sor, YAS kontrolü yapma
    if (
      selectedYapiTuruText &&
      selectedYapiTuruText.includes("İpek böcekçiliği tesisi")
    ) {
      // Soru işareti infoLink'i sadece dut bahçesi sorusunda gizle
      const infoLink = suTahsisBelgesiGroup.querySelector(
        "#su-tahsis-info-link",
      );
      if (infoLink) infoLink.style.display = "none";
      this.updateDutBahcesiSorusu(suTahsisBelgesiGroup, selectedYapiTuruText);
      // Diğer uyarı mesajlarını kaldır
      const existingInfo = suTahsisBelgesiGroup.querySelector(
        ".hayvancilik-su-tahsis-info",
      );
      if (existingInfo) existingInfo.remove();
      return;
    }

    // "Tarımsal ürün yıkama tesisi" her durumda su tahsis belgesi sormalı
    // "Besi Sığırcılığı Tesisi" ve "Süt Sığırcılığı Tesisi" için SADECE YAS KAPALI ALAN İÇİNDEYSE su tahsis belgesi sor
    const isYikamaTesisi =
      selectedYapiTuruText === "Tarımsal ürün yıkama tesisi";
    const isBesiSigirciligi =
      selectedYapiTuruText === "Besi Sığırcılığı Tesisi";
    const isSutSigirciligi = selectedYapiTuruText === "Süt Sığırcılığı Tesisi";
    let shouldShowSuTahsis = false;

    if (isYikamaTesisi) {
      // Yıkama tesisi her durumda su tahsis belgesi sorgusu gerektirir
      shouldShowSuTahsis = true;
    } else if (
      isInsideYasKapaliAlan &&
      (isBesiSigirciligi || isSutSigirciligi)
    ) {
      // Besi ve süt tesisleri SADECE YAS kapalı alan içindeyse su tahsis belgesi sorgusu gerektirir
      shouldShowSuTahsis = true;
    } else if (
      isInsideYasKapaliAlan &&
      yapiTuruSelect.value &&
      selectedYapiTuruText &&
      BAKICI_EVI_UYGUN_YAPI_TIPLERI.includes(selectedYapiTuruText) &&
      selectedYapiTuruText !== "İpek böcekçiliği tesisi"
    ) {
      // Diğer yapı türleri için YAS içindeyse ve belirli koşulları sağlıyorsa göster
      shouldShowSuTahsis = true;
    }

    if (shouldShowSuTahsis) {
      this.showSuTahsisBelgesiQuestion(
        suTahsisBelgesiGroup,
        selectedYapiTuruText,
      );

      // Uyarı mesajı oluşturma
      // Önce eski bilgilendirmeyi temizle
      const existingInfo = suTahsisBelgesiGroup.querySelector(
        ".hayvancilik-su-tahsis-info",
      );
      if (existingInfo) {
        existingInfo.remove();
      }

      // YENİ DEĞİŞİKLİK: Aşağıdaki uyarı mesajı blokları kaldırıldı/yorum satırı yapıldı.
      // Artık "Su Tahsis Belgesi Var Mı?" sorusu gösterilse bile bu özel uyarılar gösterilmeyecek.

      // YAS içinde besi ve süt tesisleri için özel uyarı
      /*
      if (isInsideYasKapaliAlan && (isBesiSigirciligi || isSutSigirciligi)) {
        const infoDiv = document.createElement("div");
        infoDiv.className =
          "alert alert-warning mt-2 hayvancilik-su-tahsis-info";
        infoDiv.innerHTML = `<i class="fas fa-exclamation-triangle"></i> <strong>${selectedYapiTuruText}</strong> için YAS kapalı alan içinde su tahsis belgesi zorunludur. Su tahsis belgesi olmadan izin verilmez.`;
        suTahsisBelgesiGroup.appendChild(infoDiv);
      } else if (isYikamaTesisi) {
        // Yıkama tesisi için özel uyarı
        const infoDiv = document.createElement("div");
        infoDiv.className =
          "alert alert-warning mt-2 hayvancilik-su-tahsis-info";
        infoDiv.innerHTML = `<i class="fas fa-exclamation-triangle"></i> <strong>${selectedYapiTuruText}</strong> için su tahsis belgesi zorunludur. Su tahsis belgesi olmadan izin verilmez.`;
        suTahsisBelgesiGroup.appendChild(infoDiv);
      }
      */
    } else {
      this.hideSuTahsisBelgesiQuestion(suTahsisBelgesiGroup);
    }
    // Su tahsis radio event listener'larını her güncellemede ekle
    if (typeof window.attachSuTahsisRadioListeners === 'function') {
      window.attachSuTahsisRadioListeners();
    }
  },

  /**
   * Sera ve silo formu görünürlüğünü kontrol eden fonksiyon
   */
  updateSeraFormuVisibility() {
    const yapiTuruSelect = Utils.getElement(CONFIG.selectors.form.yapiTuru);
    const seraFormuGroup = Utils.getElement("#sera-form-group");
    const siloFormuGroup = Utils.getElement("#silo-form-group");

    if (!yapiTuruSelect) return;

    const selectedIndex = yapiTuruSelect.selectedIndex;
    let selectedYapiTuruText =
      selectedIndex > -1 ? yapiTuruSelect.options[selectedIndex].text : null;

    if (selectedYapiTuruText) {
      const parts = selectedYapiTuruText.split(" - ");
      selectedYapiTuruText =
        parts.length > 1 ? parts.slice(1).join(" - ") : parts[0];
    }

    // Önce eski özel formları kaldır
    if (seraFormuGroup) seraFormuGroup.remove();
    if (siloFormuGroup) siloFormuGroup.remove();

    // Sadece sera seçildiyse form oluştur
    if (selectedYapiTuruText === "Sera") {
      this.createSeraFormFields();
    }
    // Silo seçildiyse silo formunu oluştur
    else if (selectedYapiTuruText === "Hububat ve yem depolama silosu") {
      this.createSiloFormFields();
    }
  },

  /**
   * Sera ile ilgili form alanlarını oluştur
   */
  createSeraFormFields() {
    const suTahsisBelgesiGroup = Utils.getElement(
      CONFIG.selectors.suTahsisBelgesi,
    );
    const formContainer = suTahsisBelgesiGroup
      ? suTahsisBelgesiGroup.parentNode
      : null;

    if (!formContainer) return;

    // Grup container oluştur
    const seraFormGroup = document.createElement("div");
    seraFormGroup.id = "sera-form-group";
    seraFormGroup.className = "form-group mt-3 form-fade-in";
    seraFormGroup.style.animation = "highlight 2s";

    // Animasyon bittikten sonra form-fade-in sınıfını kaldır
    setTimeout(() => {
      seraFormGroup.classList.remove("form-fade-in");
    }, 600);

    // Arazi büyüklüğü değerini al
    const araziBuyukluguInput = Utils.getElement(
      CONFIG.selectors.form.araziBuyuklugu,
    );
    const araziBuyuklugu = parseFloat(araziBuyukluguInput?.value || 0);

    // Varsayılan sera alanı (arazi büyüklüğünün %80'i)
    const oran =
      typeof window.SERA_VARSAYILAN_ALAN_ORANI === "number"
        ? window.SERA_VARSAYILAN_ALAN_ORANI
        : 0.8;
    const varsayilanSeraAlani = Math.round(araziBuyuklugu * oran);

    // Sera Alanı Kısmı
    const seraAlaniDiv = document.createElement("div");
    seraAlaniDiv.className = "mb-3";

    const seraAlaniLabel = document.createElement("label");
    seraAlaniLabel.htmlFor = "id_sera_alani_m2";
    seraAlaniLabel.className = "form-label";
    seraAlaniLabel.textContent = "Planlanan Sera Alanı (m²)";

    const seraAlaniInput = document.createElement("input");
    seraAlaniInput.type = "number";
    seraAlaniInput.name = "sera_alani_m2";
    seraAlaniInput.id = "id_sera_alani_m2";
    seraAlaniInput.className = "form-control";
    seraAlaniInput.value = varsayilanSeraAlani;
    seraAlaniInput.min = "10";
    seraAlaniInput.required = true;

    const seraAlaniHelpText = document.createElement("small");
    seraAlaniHelpText.className = "form-text text-muted";
    seraAlaniHelpText.textContent = "Sera için planlanan kapalı alan büyüklüğü";

    seraAlaniDiv.appendChild(seraAlaniLabel);
    seraAlaniDiv.appendChild(seraAlaniInput);
    seraAlaniDiv.appendChild(seraAlaniHelpText);

    // Bilgi mesajı
    const infoDiv = document.createElement("div");
    infoDiv.className = "alert alert-info mt-2";
    infoDiv.innerHTML =
      '<i class="fas fa-info-circle"></i> Sera projesinde idari bina yapılabilecek maksimum alan hesaplanacak ve sonuçlarda gösterilecektir.';

    // Tüm elemanları ana gruba ekle
    seraFormGroup.appendChild(seraAlaniDiv);
    seraFormGroup.appendChild(infoDiv);

    // Form grubunu sayfaya ekle - Su tahsis belgesi grubundan önce
    if (suTahsisBelgesiGroup) {
      formContainer.insertBefore(seraFormGroup, suTahsisBelgesiGroup);
    } else {
      // Submit butonundan önce ekle
      const submitButton = Utils.getElement(CONFIG.selectors.form.submitButton);
      if (submitButton && submitButton.parentNode) {
        formContainer.insertBefore(seraFormGroup, submitButton.parentNode);
      } else {
        // Son çare - container'ın sonuna ekle
        formContainer.appendChild(seraFormGroup);
      }
    }
  },

  /**
   * Silo ile ilgili form alanlarını oluştur
   */
  createSiloFormFields() {
    const suTahsisBelgesiGroup = Utils.getElement(
      CONFIG.selectors.suTahsisBelgesi,
    );
    const formContainer = suTahsisBelgesiGroup
      ? suTahsisBelgesiGroup.parentNode
      : null;

    if (!formContainer) return;

    // Grup container oluştur
    const siloFormGroup = document.createElement("div");
    siloFormGroup.id = "silo-form-group";
    siloFormGroup.className = "form-group mt-3 form-fade-in";
    siloFormGroup.style.animation = "highlight 2s";

    // Animasyon bittikten sonra form-fade-in sınıfını kaldır
    setTimeout(() => {
      siloFormGroup.classList.remove("form-fade-in");
    }, 600);

    // Arazi büyüklüğü değerini al
    const araziBuyukluguInput = Utils.getElement(
      CONFIG.selectors.form.araziBuyuklugu,
    );
    const araziBuyuklugu = parseFloat(araziBuyukluguInput?.value || 0);

    // Silo Alanı Kısmı
    const siloAlaniDiv = document.createElement("div");
    siloAlaniDiv.className = "mb-3";

    const siloAlaniLabel = document.createElement("label");
    siloAlaniLabel.htmlFor = "id_silo_alani_m2";
    siloAlaniLabel.className = "form-label";
    siloAlaniLabel.textContent = "Planlanan Silo Taban Alanı (m²)";

    const siloAlaniInput = document.createElement("input");
    siloAlaniInput.type = "number";
    siloAlaniInput.name = "planlanan_silo_taban_alani_m2";
    siloAlaniInput.id = "id_silo_alani_m2";
    siloAlaniInput.className = "form-control";
    siloAlaniInput.min = "10";
    siloAlaniInput.step = "0.01"; // Ondalık sayılara izin ver
    siloAlaniInput.required = true;
    siloAlaniInput.setAttribute("data-error", "Silo taban alanı gereklidir");
    siloAlaniInput.placeholder = "Lütfen silo taban alanını girin (m²)";

    // Varsayılan değer olarak maksimum emsal değerinin %80'ini ayarla
    if (araziBuyuklugu > 0) {
      const maxEmsal = araziBuyuklugu * 0.2; // %20 maksimum emsal
      const defaultSiloAlani = Math.floor(maxEmsal * 0.8); // Maksimum değerin %80'i
      if (defaultSiloAlani > 10) {
        siloAlaniInput.value = defaultSiloAlani;
      }
    }

    // Focus olduğunda tüm metni seç
    siloAlaniInput.addEventListener("focus", function (e) {
      e.target.select();
    });

    // Zorunlu alan göstergesi ekle
    siloAlaniLabel.innerHTML =
      'Planlanan Silo Taban Alanı (m²) <span class="text-danger">*</span>';

    // Input değeri değiştiğinde doğrulama yapılmasını sağla
    siloAlaniInput.addEventListener("input", function (e) {
      const value = e.target.value.trim();
      // Girdi rengini sıfırla
      e.target.classList.remove("is-invalid", "is-valid");

      // Eğer boşsa
      if (value === "") {
        e.target.setCustomValidity("Silo taban alanı boş olamaz");
        e.target.classList.add("is-invalid");
      }
      // Sayısal değer kontrolü
      else if (!/^[0-9.,]+$/.test(value)) {
        e.target.setCustomValidity("Lütfen sadece sayısal değer girin");
        e.target.classList.add("is-invalid");
      }
      // Değer kontrolü
      else {
        const numValue = parseFloat(value.replace(",", "."));
        if (isNaN(numValue) || numValue <= 0) {
          e.target.setCustomValidity("Geçerli bir pozitif sayı girin");
          e.target.classList.add("is-invalid");
        } else {
          e.target.setCustomValidity("");
          e.target.classList.add("is-valid");

          // Arazi büyüklüğünü alıp kıyasla
          const araziBuyukluguInput = Utils.getElement(
            CONFIG.selectors.form.araziBuyuklugu,
          );
          if (araziBuyukluguInput && araziBuyukluguInput.value) {
            const araziBuyuklugu = parseFloat(araziBuyukluguInput.value);
            if (!isNaN(araziBuyuklugu) && araziBuyuklugu > 0) {
              const maxEmsal = araziBuyuklugu * 0.2; // %20 maksimum emsal
              if (numValue > maxEmsal) {
                e.target.setCustomValidity(
                  "Silo alanı maksimum emsal değerini aşıyor",
                );
                e.target.classList.remove("is-valid");
                e.target.classList.add("is-warning"); // Uyarı rengi
              }
            }
          }
        }
      }

      // HTML5 doğrulama mesajını göster
      e.target.reportValidity();
    });

    // Form gönderilmeden önce son bir doğrulama daha yap
    siloAlaniInput.addEventListener("blur", function (e) {
      let value = e.target.value.trim();
      if (value) {
        // Virgülleri noktaya çevir ve sayıya dönüştür
        value = value.replace(",", ".");
        const numValue = parseFloat(value);
        if (!isNaN(numValue)) {
          // Sayısal değeri göster
          e.target.value = numValue.toString();
          console.log("Silo alanı doğrulandı:", numValue);

          // Arazi büyüklüğünü alıp kıyasla
          const araziBuyukluguInput = Utils.getElement(
            CONFIG.selectors.form.araziBuyuklugu,
          );
          if (araziBuyukluguInput && araziBuyukluguInput.value) {
            const araziBuyuklugu = parseFloat(araziBuyukluguInput.value);
            if (!isNaN(araziBuyuklugu) && araziBuyuklugu > 0) {
              const maxEmsal = araziBuyuklugu * 0.2; // %20 maksimum emsal

              // Kullanıcıya bilgi mesajı göster
              const infoDiv =
                e.target.parentNode.querySelector(".silo-info-message") ||
                document.createElement("div");
              infoDiv.className = "form-text mt-2 silo-info-message";

              if (numValue > maxEmsal) {
                infoDiv.classList.add("text-danger");
                infoDiv.innerHTML = `<i class="fas fa-exclamation-triangle"></i> Dikkat: Silo alanı (${numValue} m²), maksimum yapılaşma hakkını (${maxEmsal.toFixed(2)} m²) aşıyor!`;
              } else {
                infoDiv.classList.add("text-success");
                infoDiv.innerHTML = `<i class="fas fa-check-circle"></i> Silo alanı (${numValue} m²), maksimum yapılaşma hakkı (${maxEmsal.toFixed(2)} m²) içinde kalıyor.`;
              }

              // Mesaj kutusunu ekle veya güncelle
              if (!e.target.parentNode.querySelector(".silo-info-message")) {
                e.target.parentNode.appendChild(infoDiv);
              }
            }
          }
        }
      }
    });

    const siloAlaniHelpText = document.createElement("small");
    siloAlaniHelpText.className = "form-text text-muted";
    siloAlaniHelpText.innerHTML =
      '<span class="text-danger">*</span> Bu alan zorunludur - Silo için planlanan taban alanını m² cinsinden girmelisiniz';

    siloAlaniDiv.appendChild(siloAlaniLabel);
    siloAlaniDiv.appendChild(siloAlaniInput);
    siloAlaniDiv.appendChild(siloAlaniHelpText);

    // Bilgi mesajları (Sadece genel bilgi mesajı kalacak)
    // const infoDiv = document.createElement('div');
    // infoDiv.className = 'alert alert-info mt-2';
    // infoDiv.innerHTML = '<i class="fas fa-info-circle"></i> Silo projesinde idari bina ve müştemilat alanı kuralları otomatik hesaplanacak ve sonuçlarda gösterilecektir.';

    // Tüm elemanları ana gruba ekle
    siloFormGroup.appendChild(siloAlaniDiv);
    // siloFormGroup.appendChild(infoDiv); // Bu satırı kaldırın veya yoruma alın

    // Form grubunu sayfaya ekle - Su tahsis belgesi grubundan önce
    if (suTahsisBelgesiGroup) {
      formContainer.insertBefore(siloFormGroup, suTahsisBelgesiGroup);
    } else {
      // Submit butonundan önce ekle
      const submitButton = Utils.getElement(CONFIG.selectors.form.submitButton);
      if (submitButton && submitButton.parentNode) {
        formContainer.insertBefore(siloFormGroup, submitButton.parentNode);
      } else {
        // Son çare - container'ın sonuna ekle
        formContainer.appendChild(siloFormGroup);
      }
    }
  },

  /**
   * Dut bahçesi sorusunu göster ve form elemanlarını güncelle
   */
  updateDutBahcesiSorusu(group, yapiTuru) {
    // Mevcut input ve label elemanlarını bul
    const infoLink = group.querySelector("#su-tahsis-info-link");
    const evetRadio = Utils.getElement(CONFIG.selectors.form.suTahsisVarRadio);
    const hayirRadio = Utils.getElement(CONFIG.selectors.form.suTahsisYokRadio);
    const label = group.querySelector("label.option-label");

    // Bilgi linkini (soru işareti) tamamen gizle
    if (infoLink) {
      infoLink.style.display = "none";
      infoLink.onclick = null;
    }

    // İkon ve soru metnini güncelle
    if (label) {
      const iconElement = label.querySelector("i");
      if (iconElement) {
        iconElement.className = "fas fa-tree"; // Su damlası yerine ağaç ikonu
      }

      // Mevcut metin düğümünü bul ve değiştir
      for (let node of label.childNodes) {
        if (node.nodeType === Node.TEXT_NODE && node.textContent.trim()) {
          node.textContent = " Dut Bahçesi Var Mı?";
          break;
        }
      }
    }

    // Bilgi linkinin başlığını güncelle
    if (infoLink) {
      infoLink.title = "İpek böcekçiliği için dut bahçesi gereklidir";
    }

    // Radio butonların name ve ID'lerini geçici olarak değiştir
    if (evetRadio) {
      evetRadio.name = "dut_bahcesi_var_mi";
      evetRadio.id = "dut_bahcesi_var";
    }

    if (hayirRadio) {
      hayirRadio.name = "dut_bahcesi_var_mi";
      hayirRadio.id = "dut_bahcesi_yok";
    }

    // Labelları güncelle
    const evetLabel = group.querySelector('label[for="su_tahsis_var"]');
    const hayirLabel = group.querySelector('label[for="su_tahsis_yok"]');

    if (evetLabel) evetLabel.setAttribute("for", "dut_bahcesi_var");
    if (hayirLabel) hayirLabel.setAttribute("for", "dut_bahcesi_yok");

    // Grubu göster
    Utils.setVisibility(group, true);
    group.style.animation = "highlight 2s";
    console.log("Dut bahçesi sorusu gösterildi:", yapiTuru);
  },

  /**
   * Su tahsis belgesi sorusunu göster ve form elemanlarını orijinal haline getir
   */
  showSuTahsisBelgesiQuestion(group, yapiTuru) {
    // Mevcut input ve label elemanlarını bul
    const infoLink = group.querySelector("#su-tahsis-info-link");
    const evetRadio =
      group.querySelector("#dut_bahcesi_var") ||
      Utils.getElement(CONFIG.selectors.form.suTahsisVarRadio);
    const hayirRadio =
      group.querySelector("#dut_bahcesi_yok") ||
      Utils.getElement(CONFIG.selectors.form.suTahsisYokRadio);
    const label = group.querySelector("label.option-label");

    // İkon ve soru metnini orijinal haline getir
    if (label) {
      const iconElement = label.querySelector("i");
      if (iconElement) {
        iconElement.className = "fas fa-tint"; // Su damlası ikonu
      }

      // Mevcut metin düğümünü bul ve değiştir
      for (let node of label.childNodes) {
        if (node.nodeType === Node.TEXT_NODE && node.textContent.trim()) {
          node.textContent = " Su Tahsis Belgesi Var Mı?";
          break;
        }
      }
    }

    // Bilgi linkinin başlığını orijinal haline getir
    if (infoLink) {
      infoLink.title = "Kapalı Su Havzalarında Su Tahsisi Hakkında Bilgi";
      // Soru işareti ikonunu görünür ve tıklanabilir yap
      infoLink.style.display = "inline-flex";
      infoLink.onclick = function (e) {
        e.preventDefault();
        const modal = document.getElementById("su-tahsis-info-modal");
        const modalBody = document.getElementById("su-tahsis-info-modal-body");
        if (modal && modalBody) {
          modal.style.display = "block";
          modalBody.innerHTML = "Yükleniyor..."; // Önceki içeriği temizle ve yükleniyor mesajı göster
          fetch("/static/genelge.md")
            .then(response => {
              if (!response.ok) {
                throw new Error("Dosya yüklenemedi: " + response.statusText);
              }
              return response.text();
            })
            .then(md => {
              const targetTitle = "**Kapalı Su Havzalarında Su Tahsisi ile İlgili Özel Hüküm:**";
              const start = md.indexOf(targetTitle);

              if (start === -1) {
                  modalBody.innerHTML = "İlgili bölüm (\"Kapalı Su Havzalarında Su Tahsisi ile İlgili Özel Hüküm:\") genelge.md dosyasında bulunamadı.";
                  return;
              }

              // Bir sonraki bölüm başlığını veya dosya sonunu bul
              let end = md.length;
              const nextSectionMarkers = ["\n##", "\n###", "\n####", "\n--- "]; // Olası sonraki bölüm işaretçileri
              let searchStartPos = start + targetTitle.length;

              for (const marker of nextSectionMarkers) {
                  const markerPos = md.indexOf(marker, searchStartPos);
                  if (markerPos !== -1) {
                      if (end === md.length || markerPos < end) {
                          end = markerPos;
                      }
                  }
              }

              let section = md.substring(start, end).trim();
              
              if (window.markdownit) {
                const mdParser = window.markdownit();
                section = mdParser.render(section);
              } else {
                section = section.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>');
              }
              modalBody.innerHTML = section;
            })
            .catch(error => {
              console.error("Genelge yüklenirken hata:", error);
              modalBody.innerHTML = "Bilgi yüklenirken bir hata oluştu. Lütfen konsolu kontrol edin.";
            });
        }
      };
    }

    // Radio butonların name ve ID'lerini orijinal haline getir
    if (evetRadio) {
      evetRadio.name = "su_tahsis_belgesi_var_mi";
      evetRadio.id = "su_tahsis_var";
    }

    if (hayirRadio) {
      hayirRadio.name = "su_tahsis_belgesi_var_mi";
      hayirRadio.id = "su_tahsis_yok";
    }

    // Labelları güncelle
    const evetLabel = group.querySelector('label[for="dut_bahcesi_var"]');
    const hayirLabel = group.querySelector('label[for="dut_bahcesi_yok"]');

    if (evetLabel) evetLabel.setAttribute("for", "su_tahsis_var");
    if (hayirLabel) hayirLabel.setAttribute("for", "su_tahsis_yok");

    group.style.display = "block";
    group.classList.add("form-fade-in");
    group.style.animation = "highlight 2s";

    // Animasyon bittikten sonra form-fade-in sınıfını kaldır
    setTimeout(() => {
      group.classList.remove("form-fade-in");
    }, 600);

    console.log("Su tahsis belgesi sorusu gösterildi:", yapiTuru);
  },

  /**
   * Su tahsis belgesi sorusunu gizle
   */
  hideSuTahsisBelgesiQuestion(group) {
    Utils.setVisibility(group, false);

    // İpek böcekçiliği ve normal su tahsis belgesi için radio butonları sıfırla
    const suTahsisVarRadio =
      Utils.getElement("#su_tahsis_var") ||
      Utils.getElement("#dut_bahcesi_var");
    const suTahsisYokRadio =
      Utils.getElement("#su_tahsis_yok") ||
      Utils.getElement("#dut_bahcesi_yok");

    if (suTahsisVarRadio) suTahsisVarRadio.checked = false;
    if (suTahsisYokRadio) suTahsisYokRadio.checked = false;
  },
};

// Eğer bu bilgi mesajı DOM'a ekleniyorsa, eklenmesini engelleyin veya eklenmişse kaldırın.
// Örneğin, aşağıdaki gibi bir kod varsa kaldırın veya yoruma alın:
// infoDiv.innerHTML = `<div class="alert alert-info mt-2"><i class="fas fa-info-circle"></i> Silo projesinde idari bina ve müştemilat alanı kuralları otomatik hesaplanacak ve sonuçlarda gösterilecektir.</div>`;

// Ayrıca, sayfa yüklendiğinde bu mesajı DOM'dan kaldırmak için aşağıdaki kodu ekleyin:
document.addEventListener("DOMContentLoaded", () => {
  // Silo bilgi mesajını kaldır
  document
    .querySelectorAll(".alert.alert-info.mt-2")
    .forEach((el) => el.remove());

  const yapiTuruSelect = Utils.getElement(CONFIG.selectors.form.yapiTuru);
  const infoDiv = document.getElementById("yapi-turu-info");

  if (infoDiv) {
    const yapiTuru = yapiTuruSelect.value;
    if (yapiTuru === "4") {
      // Sera
      infoDiv.innerHTML =
        '<i class="fas fa-info-circle"></i> Sera projesinde idari bina yapılabilecek maksimum alan hesaplanacak ve sonuçlarda gösterilecektir.';
      infoDiv.className = "form-text mt-2 text-info";
      infoDiv.style.display = "block";
    } else if (yapiTuru === "5") {
      // Silo
      // Aşağıdaki satırı kaldırın veya yoruma alın
      // infoDiv.innerHTML = '<i class="fas fa-info-circle"></i> Silo projesinde idari bina ve müştemilat alanı otomatik hesaplanacak ve sonuçlarda gösterilecektir.';
      // infoDiv.className = "form-text mt-2 text-info";
      // infoDiv.style.display = 'block';

      // Bunun yerine mesajı gizleyin veya boşaltın
      infoDiv.innerHTML = "";
      infoDiv.style.display = "none";
    } else {
      infoDiv.innerHTML = "";
      infoDiv.style.display = "none";
    }
  }

  // Modal kapatma fonksiyonu (güvenli olması için tekrar ekleniyor)
  const closeBtn = document.getElementById("su-tahsis-info-modal-close");
  const modal = document.getElementById("su-tahsis-info-modal");
  if (closeBtn && modal) {
    closeBtn.onclick = function () {
      modal.style.display = "none";
    };
  }
});
