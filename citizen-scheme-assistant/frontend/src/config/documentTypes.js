export const DOCUMENT_TYPES = [
  { id: 'caste_certificate', labelKey: 'docCaste', provides: ['social_category'], validity_days: null },
  { id: 'income_certificate', labelKey: 'docIncome', provides: ['annual_family_income'], validity_days: null },
  { id: 'domicile_certificate', labelKey: 'docDomicile', provides: ['domicile'], validity_days: null },
  { id: 'ration_card', labelKey: 'docRationCard', provides: ['ration_card_type'], validity_days: null },
  { id: 'land_record', labelKey: 'docLandRecord', provides: ['agricultural_land'], validity_days: null },
  { id: 'marksheet', labelKey: 'docMarksheet', provides: ['education'], validity_days: null },
  { id: 'disability_certificate', labelKey: 'docDisability', provides: ['disability'], validity_days: null },
  { id: 'worker_registration', labelKey: 'docWorkerRegistration', provides: ['occupation'], validity_days: null },
  { id: 'ex_servicemen_id', labelKey: 'docExServicemen', provides: ['special_categories'], validity_days: null },
  { id: 'school_admission_proof', labelKey: 'docSchoolProof', provides: ['currently_studying'], validity_days: null },
  // CONFIRM: Aadhaar and bank passbook are tick-only and must never be uploaded.
  { id: 'aadhaar_tick', labelKey: 'docAadhaarTick', provides: [], validity_days: null, tickOnly: true },
  { id: 'bank_passbook_tick', labelKey: 'docBankPassbookTick', provides: [], validity_days: null, tickOnly: true },
];
