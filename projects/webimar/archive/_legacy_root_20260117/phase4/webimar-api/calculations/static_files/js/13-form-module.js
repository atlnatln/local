// Ana Form modülü - Diğer form modüllerinin birleştirildiği nokta
const FormModule = {
    init() {
        // FormCore'dan miras alınan özellikleri ayarla
        this.originalOptions = FormCore.originalOptions;
        
        // Form modüllerini başlat
        FormCore.init();
    },
    
    // FormCore'dan gelen metotlar
    setupFormControls: FormCore.setupFormControls,
    setupSelectPlaceholder: FormCore.setupSelectPlaceholder,
    setupEventListeners: FormCore.setupEventListeners,
    filterYapiTuruByTapuVasfi: FormCore.filterYapiTuruByTapuVasfi,
    
    // FormVisibility'den gelen metotlar
    handleTapuVasfiChange: FormVisibility.handleTapuVasfiChange.bind(FormVisibility),
    handleAraziBuyukluguChange: FormVisibility.handleAraziBuyukluguChange.bind(FormVisibility),
    
    // SpecialFormFields'dan gelen metotlar
    updateSuTahsisBelgesiVisibility: SpecialFormFields.updateSuTahsisBelgesiVisibility.bind(SpecialFormFields),
    updateSeraFormuVisibility: SpecialFormFields.updateSeraFormuVisibility.bind(SpecialFormFields),
    createSeraFormFields: SpecialFormFields.createSeraFormFields.bind(SpecialFormFields),
    createSiloFormFields: SpecialFormFields.createSiloFormFields.bind(SpecialFormFields),
    updateDutBahcesiSorusu: SpecialFormFields.updateDutBahcesiSorusu.bind(SpecialFormFields),
    showSuTahsisBelgesiQuestion: SpecialFormFields.showSuTahsisBelgesiQuestion.bind(SpecialFormFields),
    hideSuTahsisBelgesiQuestion: SpecialFormFields.hideSuTahsisBelgesiQuestion.bind(SpecialFormFields),
    
    // FormSubmission'dan gelen metotlar
    handleFormSubmit: FormSubmission.handleFormSubmit.bind(FormSubmission),
    validateForm: FormSubmission.validateForm.bind(FormSubmission),
    prepareFormData: FormSubmission.prepareFormData.bind(FormSubmission),
    submitForm: FormSubmission.submitForm.bind(FormSubmission)
};
