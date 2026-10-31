// TEMPORARY MOCK. Delete at engine integration. Frontend must not contain eligibility rules.

/**
 * Mock Schemes Data for YojanaMitra
 * Structure conforms to contracts/scheme.schema.json
 * Official source portals and criteria sourced from verified government domains (.gov.in)
 */

export const INDIAN_STATES = [
  { code: 'ALL', name: { en: 'All States & Union Territories', hi: 'सभी राज्य एवं केंद्र शासित प्रदेश' } },
  { code: 'AN', name: { en: 'Andaman and Nicobar Islands', hi: 'अंडमान और निकोबार द्वीप समूह' } },
  { code: 'AP', name: { en: 'Andhra Pradesh', hi: 'आंध्र प्रदेश' } },
  { code: 'AR', name: { en: 'Arunachal Pradesh', hi: 'अरुणाचल प्रदेश' } },
  { code: 'AS', name: { en: 'Assam', hi: 'असम' } },
  { code: 'BR', name: { en: 'Bihar', hi: 'बिहार' } },
  { code: 'CH', name: { en: 'Chandigarh', hi: 'चंडीगढ़' } },
  { code: 'CT', name: { en: 'Chhattisgarh', hi: 'छत्तीसगढ़' } },
  { code: 'DN', name: { en: 'Dadra and Nagar Haveli and Daman and Diu', hi: 'दादरा और नगर हवेली एवं दमन और दीव' } },
  { code: 'DL', name: { en: 'Delhi (NCT)', hi: 'दिल्ली (राष्ट्रीय राजधानी क्षेत्र)' } },
  { code: 'GA', name: { en: 'Goa', hi: 'गोवा' } },
  { code: 'GJ', name: { en: 'Gujarat', hi: 'गुजरात' } },
  { code: 'HR', name: { en: 'Haryana', hi: 'हरियाणा' } },
  { code: 'HP', name: { en: 'Himachal Pradesh', hi: 'हिमाचल प्रदेश' } },
  { code: 'JK', name: { en: 'Jammu and Kashmir', hi: 'जम्मू और कश्मीर' } },
  { code: 'JH', name: { en: 'Jharkhand', hi: 'झारखंड' } },
  { code: 'KA', name: { en: 'Karnataka', hi: 'कर्नाटक' } },
  { code: 'KL', name: { en: 'Kerala', hi: 'केरल' } },
  { code: 'LA', name: { en: 'Ladakh', hi: 'लद्दाख' } },
  { code: 'LD', name: { en: 'Lakshadweep', hi: 'लक्षद्वीप' } },
  { code: 'MP', name: { en: 'Madhya Pradesh', hi: 'मध्य प्रदेश' } },
  { code: 'MH', name: { en: 'Maharashtra', hi: 'महाराष्ट्र' } },
  { code: 'MN', name: { en: 'Manipur', hi: 'मणिपुर' } },
  { code: 'ML', name: { en: 'Meghalaya', hi: 'मेघालय' } },
  { code: 'MZ', name: { en: 'Mizoram', hi: 'मिजोरम' } },
  { code: 'NL', name: { en: 'Nagaland', hi: 'नागालैंड' } },
  { code: 'OD', name: { en: 'Odisha', hi: 'ओडिशा' } },
  { code: 'PY', name: { en: 'Puducherry', hi: 'पुदुच्चेरी' } },
  { code: 'PB', name: { en: 'Punjab', hi: 'पंजाब' } },
  { code: 'RJ', name: { en: 'Rajasthan', hi: 'राजस्थान' } },
  { code: 'SK', name: { en: 'Sikkim', hi: 'सिक्किम' } },
  { code: 'TN', name: { en: 'Tamil Nadu', hi: 'तमिलनाडु' } },
  { code: 'TS', name: { en: 'Telangana', hi: 'तेलंगाना' } },
  { code: 'TR', name: { en: 'Tripura', hi: 'त्रिपुरा' } },
  { code: 'UP', name: { en: 'Uttar Pradesh', hi: 'उत्तर प्रदेश' } },
  { code: 'UK', name: { en: 'Uttarakhand', hi: 'उत्तराखंड' } },
  { code: 'WB', name: { en: 'West Bengal', hi: 'पश्चिम बंगाल' } },
];

export const SCHEME_CATEGORIES = [
  { id: 'all', key: 'catAll', icon: 'Grid' },
  { id: 'agriculture', key: 'catAgriculture', icon: 'Sprout' },
  { id: 'women-child', key: 'catWomenChild', icon: 'Users' },
  { id: 'education', key: 'catEducation', icon: 'GraduationCap' },
  { id: 'health', key: 'catHealth', icon: 'HeartPulse' },
  { id: 'housing', key: 'catHousing', icon: 'Home' },
  { id: 'employment', key: 'catEmployment', icon: 'Briefcase' },
  { id: 'business', key: 'catBusiness', icon: 'TrendingUp' },
  { id: 'social-welfare', key: 'catSocialWelfare', icon: 'ShieldCheck' },
];

export const MOCK_SCHEMES = [
  {
    id: 'pm-kisan',
    code: 'pm-kisan',
    name: {
      en: 'PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)',
      hi: 'प्रधानमंत्री किसान सम्मान निधि (पीएम-किसान)',
    },
    short_name: 'PM-KISAN',
    category: 'agriculture',
    level: 'central',
    state_code: 'ALL',
    applicable_states: ['ALL'],
    featured: true,
    description: {
      en: 'Direct income support of ₹6,000 per year in three equal 4-monthly installments of ₹2,000 to all eligible landholding farmer families across India.',
      hi: 'देश भर के सभी पात्र भूमिधारक किसान परिवारों को प्रति वर्ष ₹6,000 की प्रत्यक्ष आय सहायता तीन समान 4-मासिक किस्तों (₹2,000 प्रत्येक) में।',
    },
    benefits: {
      en: 'Direct Benefit Transfer (DBT) of ₹6,000 annually credited straight into the farmer’s Aadhaar-linked bank account in 3 installments.',
      hi: 'प्रति वर्ष ₹6,000 की नकद सहायता सीधे किसान के आधार-लिंक बैंक खाते में 3 बराबर किस्तों (प्रत्येक ₹2,000) में डीबीटी द्वारा।',
    },
    official_source: {
      url: 'https://pmkisan.gov.in',
      last_checked_date: '2026-02-15',
      issuing_ministry: {
        en: 'Ministry of Agriculture & Farmers Welfare',
        hi: 'कृषि एवं किसान कल्याण मंत्रालय',
      },
      gazette_or_order_ref: 'Operational Guidelines (Revised) 2024',
    },
    criteria: [
      {
        id: 'crit-landowner',
        field: 'owns_agricultural_land',
        operator: 'EQUALS',
        target_value: true,
        criticality: 'MANDATORY',
        explanation_if_met: {
          en: 'You own cultivable agricultural land registered in your name or family name.',
          hi: 'आपके या परिवार के नाम पर खेती योग्य कृषि भूमि दर्ज है।',
        },
        explanation_if_violated: {
          en: 'This scheme requires cultivable agricultural land ownership in land records.',
          hi: 'इस योजना के लिए राजस्व रिकॉर्ड में खेती योग्य ज़मीन का नाम होना अनिवार्य है।',
        },
      },
      {
        id: 'crit-not-taxpayer',
        field: 'is_income_taxpayer',
        operator: 'EQUALS',
        target_value: false,
        criticality: 'DISQUALIFIER',
        explanation_if_met: {
          en: 'No member of the household paid income tax in the last assessment year.',
          hi: 'परिवार के किसी भी सदस्य ने पिछले वित्तीय वर्ष में आयकर नहीं भरा है।',
        },
        explanation_if_violated: {
          en: 'Income tax-paying individuals and institutional landholders are excluded from PM-KISAN.',
          hi: 'आयकर भरने वाले किसान परिवार और संस्थागत भूमिधारक इस योजना से बाहर हैं।',
        },
      },
    ],
    required_documents: [
      {
        id: 'doc-aadhaar',
        title: {
          en: 'Aadhaar Card (linked with active mobile)',
          hi: 'आधार कार्ड (सक्रिय मोबाइल नंबर से लिंक)',
        },
        issuing_authority: {
          en: 'UIDAI',
          hi: 'भारतीय विशिष्ट पहचान प्राधिकरण',
        },
        optional: false,
        guidance: {
          en: 'Mandatory for OTP and biometric e-KYC on PM-KISAN portal.',
          hi: 'पीएम-किसान पोर्टल पर ओटीपी एवं बायोमेट्रिक ई-केवाईसी हेतु अनिवार्य।',
        },
      },
      {
        id: 'doc-land-records',
        title: {
          en: 'Land Ownership Record (Khatauni / RoR / Khasra)',
          hi: 'भू-अभिलेख (खतौनी / खसरा / नकल)',
        },
        issuing_authority: {
          en: 'State Revenue Department / Bhulekh',
          hi: 'राज्य राजस्व विभाग / भूलेख पोर्टल',
        },
        optional: false,
        guidance: {
          en: 'Must show your name as a valid landholder in the computerized state land database.',
          hi: 'सरकारी भूलेख पोर्टल पर आपका नाम भूमि स्वामी के रूप में दर्ज होना चाहिए।',
        },
      },
      {
        id: 'doc-bank-passbook',
        title: {
          en: 'Bank Account Passbook (Aadhaar & NPCI Mapped)',
          hi: 'बैंक पासबुक (आधार एवं एनपीसीआई सीडेड खाता)',
        },
        issuing_authority: {
          en: 'Commercial Bank, Regional Rural Bank or IPPB',
          hi: 'वाणिज्यिक बैंक, ग्रामीण बैंक अथवा डाकघर बैंक',
        },
        optional: false,
        guidance: {
          en: 'Direct Benefit Transfer (DBT) is credited solely to Aadhaar-seeded accounts.',
          hi: 'डीबीटी राशि केवल आधार से लिंक सक्रिय बैंक खाते में ही भेजी जाती है।',
        },
      },
    ],
    application_steps: [
      {
        step_number: 1,
        title: { en: 'Self Registration on Portal', hi: 'पोर्टल पर स्वयं पंजीकरण' },
        description: {
          en: 'Visit https://pmkisan.gov.in and click on "Farmers Corner" -> "New Farmer Registration".',
          hi: 'pmkisan.gov.in पर जाएं और "Farmers Corner" में "New Farmer Registration" पर क्लिक करें।',
        },
      },
      {
        step_number: 2,
        title: { en: 'Aadhaar Authentication & Land Details', hi: 'आधार प्रमाणीकरण एवं भूमि विवरण' },
        description: {
          en: 'Enter your Aadhaar number, state, district, sub-district, village, and upload land Khatauni.',
          hi: 'आधार संख्या दर्ज कर ओटीपी सत्यापित करें और अपनी खतौनी/जमाबंदी का विवरण भरें।',
        },
      },
      {
        step_number: 3,
        title: { en: 'Walk-in CSC Assistance (Alternative)', hi: 'जन सेवा केंद्र (CSC) के माध्यम से' },
        description: {
          en: 'Alternatively, visit any local Common Service Centre (CSC) with your Aadhaar, bank passbook, and land papers.',
          hi: 'यदि ऑनलाइन फॉर्म भरने में कठिनाई हो, तो नज़दीकी सीएससी केंद्र पर जाकर पंजीकरण कराएं।',
        },
      },
    ],
  },
  {
    id: 'pm-ujjwala',
    code: 'pm-ujjwala',
    name: {
      en: 'Pradhan Mantri Ujjwala Yojana (PMUY 2.0)',
      hi: 'प्रधानमंत्री उज्ज्वला योजना (पीएमयूवाई 2.0)',
    },
    short_name: 'PM Ujjwala',
    category: 'women-child',
    level: 'central',
    state_code: 'ALL',
    applicable_states: ['ALL'],
    featured: true,
    description: {
      en: 'Deposit-free LPG cylinder connection provided to adult women from poor and BPL households, along with first refill and stove free of cost.',
      hi: 'गरीब एवं बीपीएल परिवारों की वयस्क महिलाओं को बिना किसी डिपॉज़िट के नया एलपीजी गैस कनेक्शन, पहला भरा हुआ सिलेंडर और चूल्हा निःशुल्क।',
    },
    benefits: {
      en: 'Free LPG connection, security deposit waiver on cylinder and regulator, free first refill, and a complimentary 2-burner gas stove.',
      hi: 'निःशुल्क गैस कनेक्शन, सुरक्षा राशि की छूट, पहला भरा हुआ गैस सिलेंडर और 2 बर्नर वाला गैस चूल्हा एकदम मुफ्त।',
    },
    official_source: {
      url: 'https://pmuy.gov.in',
      last_checked_date: '2026-01-20',
      issuing_ministry: {
        en: 'Ministry of Petroleum & Natural Gas',
        hi: 'पेट्रोलियम एवं प्राकृतिक गैस मंत्रालय',
      },
      gazette_or_order_ref: 'PMUY Guidelines Phase II (2023-2025)',
    },
    criteria: [
      {
        id: 'crit-adult-female',
        field: 'is_adult_woman',
        operator: 'EQUALS',
        target_value: true,
        criticality: 'MANDATORY',
        explanation_if_met: {
          en: 'Applicant must be an adult woman aged 18 years or above.',
          hi: 'आवेदक 18 वर्ष या उससे अधिक आयु की महिला होनी चाहिए।',
        },
        explanation_if_violated: {
          en: 'Ujjwala connections are issued solely in the name of an adult female member of the household.',
          hi: 'उज्ज्वला योजना के तहत कनेक्शन केवल परिवार की वयस्क महिला के नाम पर ही दिया जाता है।',
        },
      },
      {
        id: 'crit-no-existing-lpg',
        field: 'has_existing_lpg',
        operator: 'EQUALS',
        target_value: false,
        criticality: 'DISQUALIFIER',
        explanation_if_met: {
          en: 'No existing LPG connection exists in the same household.',
          hi: 'परिवार के किसी भी सदस्य के नाम पर पहले से कोई एलपीजी गैस कनेक्शन नहीं है।',
        },
        explanation_if_violated: {
          en: 'Households with an existing active LPG connection are not eligible for a second subsidized connection.',
          hi: 'जिन परिवारों में पहले से रसोई गैस कनेक्शन है, वे इस योजना के पात्र नहीं हैं।',
        },
      },
    ],
    required_documents: [
      {
        id: 'doc-aadhaar-woman',
        title: {
          en: 'Aadhaar Card of the female applicant',
          hi: 'महिला आवेदक का आधार कार्ड',
        },
        issuing_authority: {
          en: 'UIDAI',
          hi: 'भारतीय विशिष्ट पहचान प्राधिकरण',
        },
        optional: false,
        guidance: {
          en: 'Proof of identity and address.',
          hi: 'पहचान और निवास के प्रमाण हेतु।',
        },
      },
      {
        id: 'doc-ration-card',
        title: {
          en: 'Ration Card / Family Composition Certificate',
          hi: 'राशन कार्ड (परिवार के सभी सदस्यों के नाम सहित)',
        },
        issuing_authority: {
          en: 'Department of Food & Civil Supplies',
          hi: 'खाद्य एवं नागरिक आपूर्ति विभाग',
        },
        optional: false,
        guidance: {
          en: 'Confirms family composition and eligible BPL / Antyodaya status.',
          hi: 'परिवार के सदस्यों की पुष्टि एवं बीपीएल/अंत्योदय श्रेणी हेतु।',
        },
      },
      {
        id: 'doc-bank-account',
        title: {
          en: 'Bank Account Passbook (Jan Dhan or Savings)',
          hi: 'बैंक पासबुक (जन धन या सामान्य बचत खाता)',
        },
        issuing_authority: {
          en: 'Bank / Post Office',
          hi: 'बैंक अथवा डाकघर',
        },
        optional: false,
        guidance: {
          en: 'Required for future cylinder subsidy deposits.',
          hi: 'भविष्य में मिलने वाली एलपीजी सब्सिडी सीधे खाते में पाने हेतु।',
        },
      },
    ],
    application_steps: [
      {
        step_number: 1,
        title: { en: 'Choose Fuel Distributor', hi: 'गैस एजेंसी चुनें' },
        description: {
          en: 'Choose nearest Indane, Bharat Gas, or HP Gas distributor.',
          hi: 'अपनी नज़दीकी इंडेन, भारत गैस या एचपी गैस एजेंसी का चयन करें।',
        },
      },
      {
        step_number: 2,
        title: { en: 'Submit Ujjwala Application Form', hi: 'उज्ज्वला फॉर्म जमा करें' },
        description: {
          en: 'Submit completed 14-point declaration and documents at the distributor office or online on pmuy.gov.in.',
          hi: 'आवश्यक दस्तावेज़ों के साथ आवेदन पत्र गैस एजेंसी में जमा करें या ऑनलाइन पोर्टल पर भरें।',
        },
      },
    ],
  },
  {
    id: 'pm-vishwakarma',
    code: 'pm-vishwakarma',
    name: {
      en: 'PM Vishwakarma Scheme',
      hi: 'पीएम विश्वकर्मा योजना',
    },
    short_name: 'PM Vishwakarma',
    category: 'business',
    level: 'central',
    state_code: 'ALL',
    applicable_states: ['ALL'],
    featured: true,
    description: {
      en: 'Holistic end-to-end support to traditional artisans and craftspeople working with their hands and tools across 18 designated trades.',
      hi: 'हाथ और औज़ारों से काम करने वाले 18 पारंपरिक शिल्पकर्मियों और कारीगरों को पहचान पत्र, कौशल प्रशिक्षण, टूलकिट और रियायती ऋण सहायता।',
    },
    benefits: {
      en: 'PM Vishwakarma Certificate & ID, ₹15,000 modern toolkit incentive, skill stipend of ₹500/day during training, and collateral-free enterprise credit up to ₹3 Lakh at 5% interest.',
      hi: 'विश्वकर्मा प्रमाण पत्र एवं आईडी कार्ड, ₹15,000 का टूलकिट अनुदान, प्रशिक्षण के दौरान ₹500 प्रतिदिन मानदेय, तथा 5% रियायती ब्याज पर ₹3 लाख तक बिना गारंटी लोन।',
    },
    official_source: {
      url: 'https://pmvishwakarma.gov.in',
      last_checked_date: '2026-02-01',
      issuing_ministry: {
        en: 'Ministry of Micro, Small & Medium Enterprises (MSME)',
        hi: 'सूक्ष्म, लघु एवं मध्यम उद्यम मंत्रालय (MSME)',
      },
      gazette_or_order_ref: 'Gazette of India Notification No. 433 (E)',
    },
    criteria: [
      {
        id: 'crit-traditional-artisan',
        field: 'is_traditional_artisan',
        operator: 'EQUALS',
        target_value: true,
        criticality: 'MANDATORY',
        explanation_if_met: {
          en: 'You engage in one of the 18 eligible traditional family trades (Carpenter, Blacksmith, Potter, Sculptor, Cobbler, Mason, Weaver, Tailor, Barber, etc.).',
          hi: 'आप 18 पारंपरिक व्यवसायों में से एक में संलग्न हैं (बढ़ई, लोहार, कुम्हार, मूर्तिकार, मोची, राजमिस्त्री, धोबी, नाई, दर्जी आदि)।',
        },
        explanation_if_violated: {
          en: 'Only artisans and craftspeople engaged in the 18 scheduled family crafts are covered under PM Vishwakarma.',
          hi: 'केवल निर्धारित 18 पारंपरिक व्यवसायों से जुड़े कारीगर ही इस योजना के पात्र हैं।',
        },
      },
      {
        id: 'crit-min-age-18',
        field: 'age_greater_than_18',
        operator: 'EQUALS',
        target_value: true,
        criticality: 'MANDATORY',
        explanation_if_met: {
          en: 'Applicant is 18 years of age or older at the time of registration.',
          hi: 'आवेदक की आयु पंजीकरण के समय 18 वर्ष या उससे अधिक है।',
        },
        explanation_if_violated: {
          en: 'Applicant must be minimum 18 years old.',
          hi: 'आवेदक की न्यूनतम आयु 18 वर्ष होनी आवश्यक है।',
        },
      },
    ],
    required_documents: [
      {
        id: 'doc-aadhaar-artisan',
        title: { en: 'Aadhaar Card (Biometric enabled)', hi: 'आधार कार्ड (बायोमेट्रिक प्रमाणीकरण हेतु)' },
        issuing_authority: { en: 'UIDAI', hi: 'भारतीय विशिष्ट पहचान प्राधिकरण' },
        optional: false,
        guidance: { en: 'Biometric authentication takes place at the CSC during application.', hi: 'आवेदन के समय सीएससी पर बायोमेट्रिक जांच की जाती है।' },
      },
      {
        id: 'doc-mobile-linked',
        title: { en: 'Aadhaar-Linked Active Mobile Number', hi: 'आधार से लिंक मोबाइल नंबर' },
        issuing_authority: { en: 'Telecom Operator', hi: 'मोबाइल नेटवर्क' },
        optional: false,
        guidance: { en: 'Required for OTP registration and DBT toolkit credit.', hi: 'ओटीपी सत्यापन एवं टूलकिट अनुदान राशि प्राप्ति हेतु।' },
      },
      {
        id: 'doc-bank-account-artisan',
        title: { en: 'Active Bank Account Details', hi: 'सक्रिय बैंक खाता विवरण' },
        issuing_authority: { en: 'Scheduled Commercial Bank', hi: 'अनुसूचित बैंक' },
        optional: false,
        guidance: { en: 'Account where training stipend and credit assistance will be disbursed.', hi: 'जिस खाते में स्टाइपेंड और ऋण राशि हस्तांतरित की जाएगी।' },
      },
    ],
    application_steps: [
      {
        step_number: 1,
        title: { en: 'CSC Biometric Registration', hi: 'सीएससी केंद्र पर बायोमेट्रिक पंजीकरण' },
        description: {
          en: 'Visit the nearest Common Service Centre (CSC) with your trade tools details and Aadhaar.',
          hi: 'अपने व्यवसाय की जानकारी और आधार कार्ड लेकर नज़दीकी जन सेवा केंद्र पर जाएं।',
        },
      },
      {
        step_number: 2,
        title: { en: 'Gram Panchayat / Urban Local Body Verification', hi: 'ग्राम प्रधान / नगर निकाय सत्यापन' },
        description: {
          en: 'Your application is verified by the local Gram Pradhan or Executive Officer.',
          hi: 'ग्राम पंचायत या स्थानीय निकाय द्वारा आपके पारंपरिक कार्य का भौतिक सत्यापन किया जाता है।',
        },
      },
      {
        step_number: 3,
        title: { en: 'Basic Training & Toolkit Voucher', hi: 'प्रशिक्षण एवं टूलकिट ई-वाउचर' },
        description: {
          en: 'Complete 5-7 days basic skill upgrading and receive ₹15,000 digital e-RUPI toolkit voucher.',
          hi: '5 से 7 दिनों का प्रशिक्षण पूरा करने पर ₹15,000 का टूलकिट ई-वाउचर प्राप्त होता है।',
        },
      },
    ],
  },
  {
    id: 'pmay-g',
    code: 'pmay-g',
    name: {
      en: 'Pradhan Mantri Awaas Yojana - Gramin (PMAY-G)',
      hi: 'प्रधानमंत्री आवास योजना - ग्रामीण (पीएमएवाई-जी)',
    },
    short_name: 'PMAY-G',
    category: 'housing',
    level: 'central',
    state_code: 'ALL',
    applicable_states: ['ALL'],
    featured: true,
    description: {
      en: 'Financial assistance of ₹1.20 Lakh in plains and ₹1.30 Lakh in hilly/difficult areas to homeless and kutcha-house dwelling rural families for building a permanent pucca house.',
      hi: 'ग्रामीण क्षेत्रों के बेघर और कच्चे मकानों में रहने वाले परिवारों को पक्का मकान बनाने हेतु मैदानी क्षेत्रों में ₹1.20 लाख तथा पहाड़ी क्षेत्रों में ₹1.30 लाख की वित्तीय सहायता।',
    },
    benefits: {
      en: 'Financial grant up to ₹1.20 Lakh / ₹1.30 Lakh + 90-95 days of unskilled labor wages under MGNREGA (~₹25,000) + ₹12,000 assistance for toilet construction under SBM-G.',
      hi: 'मकान निर्माण हेतु ₹1.20 लाख से ₹1.30 लाख का अनुदान + मनरेगा के तहत 90 दिनों की मजदूरी (~₹25,000) + शौचालय निर्माण हेतु ₹12,000 अतिरिक्त सहायता।',
    },
    official_source: {
      url: 'https://pmayg.nic.in',
      last_checked_date: '2026-02-10',
      issuing_ministry: {
        en: 'Ministry of Rural Development',
        hi: 'ग्रामीण विकास मंत्रालय',
      },
      gazette_or_order_ref: 'PMAY-G Framework for Implementation (Extension to 2028-29)',
    },
    criteria: [
      {
        id: 'crit-rural-kutcha',
        field: 'lives_in_kutcha_house',
        operator: 'EQUALS',
        target_value: true,
        criticality: 'MANDATORY',
        explanation_if_met: {
          en: 'You reside in rural India and your family does not own a pucca house anywhere in the country.',
          hi: 'आप ग्रामीण क्षेत्र में रहते हैं और देश भर में आपके पास कोई पक्का मकान नहीं है।',
        },
        explanation_if_violated: {
          en: 'Households that already own a pucca house are not eligible for PMAY-G assistance.',
          hi: 'जिन परिवारों के पास पहले से पक्का मकान है, वे पीएम आवास योजना के पात्र नहीं हैं।',
        },
      },
      {
        id: 'crit-no-motor-vehicle',
        field: 'owns_motorized_vehicle',
        operator: 'EQUALS',
        target_value: false,
        criticality: 'DISQUALIFIER',
        explanation_if_met: {
          en: 'No household member owns a motorized 3-wheeler or 4-wheeler vehicle.',
          hi: 'परिवार में किसी के पास तीन पहिया या चार पहिया मोटर वाहन नहीं है।',
        },
        explanation_if_violated: {
          en: 'Ownership of motorized 3/4 wheeler vehicles or mechanized agricultural equipment is an exclusion criterion.',
          hi: 'चार पहिया गाड़ी या मशीनीकृत कृषि उपकरण रखने वाले परिवार इस योजना से बहिष्कृत हैं।',
        },
      },
    ],
    required_documents: [
      {
        id: 'doc-aadhaar-family',
        title: { en: 'Aadhaar Numbers of all adult family members', hi: 'परिवार के सभी वयस्क सदस्यों के आधार कार्ड' },
        issuing_authority: { en: 'UIDAI', hi: 'भारतीय विशिष्ट पहचान प्राधिकरण' },
        optional: false,
        guidance: { en: 'Consent form required for de-duplication in SECC / Awaas+ list.', hi: 'आवास+ सूची में नाम सत्यापन हेतु सहमति पत्र आवश्यक है।' },
      },
      {
        id: 'doc-bank-account-pmay',
        title: { en: 'Bank / Post Office Passbook with IFSC', hi: 'बैंक अथवा डाकघर खाता पासबुक' },
        issuing_authority: { en: 'Bank / Post Office', hi: 'बैंक या डाकघर' },
        optional: false,
        guidance: { en: 'Must be an active single or joint DBT account of beneficiary.', hi: 'सक्रिय डीबीटी खाता जिसमें निर्माण की 3 किस्तों का पैसा सीधे आएगा।' },
      },
      {
        id: 'doc-job-card',
        title: { en: 'MGNREGA Job Card (if registered)', hi: 'मनरेगा जॉब कार्ड (यदि उपलब्ध हो)' },
        issuing_authority: { en: 'Gram Panchayat', hi: 'ग्राम पंचायत' },
        optional: true,
        guidance: { en: 'To claim additional 90-95 days unskilled labor entitlement.', hi: 'मकान निर्माण में 90 दिन की मजदूरी का अतिरिक्त लाभ पाने हेतु।' },
      },
    ],
    application_steps: [
      {
        step_number: 1,
        title: { en: 'Awaas+ Survey Verification', hi: 'आवास+ सूची में नाम की जांच' },
        description: {
          en: 'Check with your Gram Panchayat Secretary or Gram Rozgar Sahayak if your name appears on the Awaas+ permanent waitlist.',
          hi: 'ग्राम पंचायत सचिव या ग्राम रोजगार सहायक से मिलकर आवास+ प्रतीक्षा सूची में अपना नाम जांचें।',
        },
      },
      {
        step_number: 2,
        title: { en: 'Geo-tagging of Kutcha House Site', hi: 'कच्चे मकान का जियो-टैगिंग (फ़ोटो)' },
        description: {
          en: 'The Panchayat inspector clicks geo-tagged photos of your current kutcha structure using the AwaasApp.',
          hi: 'पंचायत प्रतिनिधि आवास मोबाइल ऐप से आपके वर्तमान कच्चे मकान की जियो-टैग फोटो अपलोड करते हैं।',
        },
      },
      {
        step_number: 3,
        title: { en: 'Sanction & Installment Disbursal', hi: 'स्वीकृति आदेश एवं किस्तों का भुगतान' },
        description: {
          en: 'Upon approval, funds are transferred in 3 stages: plinth level, lintel level, and completion.',
          hi: 'स्वीकृति के बाद नींव, छत और पूर्णता स्तर के आधार पर तीन किस्तों में बैंक खाते में पैसा आता है।',
        },
      },
    ],
  },
  {
    id: 'ladli-behna-mp',
    code: 'ladli-behna-mp',
    name: {
      en: 'Mukhyamantri Ladli Behna Yojana (Madhya Pradesh)',
      hi: 'मुख्यमंत्री लाड़ली बहना योजना (मध्य प्रदेश)',
    },
    short_name: 'Ladli Behna Yojana',
    category: 'women-child',
    level: 'state',
    state_code: 'MP',
    applicable_states: ['MP'],
    featured: true,
    description: {
      en: 'Monthly financial assistance of ₹1,250 directly transferred to eligible resident women of Madhya Pradesh aged 21 to 60 years to ensure financial autonomy and family health.',
      hi: 'मध्य प्रदेश की 21 से 60 वर्ष आयु की पात्र बहनों को प्रतिमाह ₹1,250 की प्रत्यक्ष आर्थिक सहायता ताकि वे आर्थिक रूप से सशक्त और स्वावलंबी बन सकें।',
    },
    benefits: {
      en: 'Direct monthly DBT transfer of ₹1,250 (₹15,000 per year) directly credited to beneficiary woman’s bank account on the 10th of every month.',
      hi: 'प्रत्येक माह की 10 तारीख को ₹1,250 की राशि (सालाना ₹15,000) सीधे बहन के आधार-लिंक बैंक खाते में डीबीटी द्वारा।',
    },
    official_source: {
      url: 'https://cmladlibehna.mp.gov.in',
      last_checked_date: '2026-02-18',
      issuing_ministry: {
        en: 'Women & Child Development Department, Govt of Madhya Pradesh',
        hi: 'महिला एवं बाल विकास विभाग, मध्य प्रदेश शासन',
      },
      gazette_or_order_ref: 'MP Govt Order F-01-02/2023/50-2',
    },
    criteria: [
      {
        id: 'crit-mp-domicile',
        field: 'is_mp_resident',
        operator: 'EQUALS',
        target_value: true,
        criticality: 'MANDATORY',
        explanation_if_met: {
          en: 'Applicant is a permanent resident and domiciled in Madhya Pradesh.',
          hi: 'आवेदिका मध्य प्रदेश की स्थानीय निवासी हैं।',
        },
        explanation_if_violated: {
          en: 'Mukhyamantri Ladli Behna Yojana is strictly for permanent residents of Madhya Pradesh.',
          hi: 'यह योजना केवल मध्य प्रदेश की मूल निवासी महिलाओं के लिए है।',
        },
      },
      {
        id: 'crit-age-21-60',
        field: 'age_between_21_60',
        operator: 'EQUALS',
        target_value: true,
        criticality: 'MANDATORY',
        explanation_if_met: {
          en: 'Woman applicant is between 21 and 60 years of age.',
          hi: 'आवेदिका महिला की उम्र 21 वर्ष से 60 वर्ष के बीच है।',
        },
        explanation_if_violated: {
          en: 'Applicant must be between 21 and 60 years of age (married, widowed, divorced, or abandoned).',
          hi: 'महिला की आयु 21 से 60 वर्ष के मध्य होनी चाहिए।',
        },
      },
      {
        id: 'crit-family-income-cap',
        field: 'annual_income_under_2_5lakh',
        operator: 'EQUALS',
        target_value: true,
        criticality: 'MANDATORY',
        explanation_if_met: {
          en: 'Combined family annual income is less than ₹2.5 Lakh.',
          hi: 'परिवार की कुल वार्षिक आय ₹2.5 लाख से कम है।',
        },
        explanation_if_violated: {
          en: 'Families with annual income exceeding ₹2.5 Lakh or owning more than 5 acres of land are ineligible.',
          hi: 'जिन परिवारों की आय ₹2.5 लाख से अधिक है या 5 एकड़ से अधिक कृषि भूमि है, वे अपात्र हैं।',
        },
      },
    ],
    required_documents: [
      {
        id: 'doc-samagra-id',
        title: { en: 'Samagra Family ID & Member ID (e-KYC verified)', hi: 'समग्र परिवार आईडी एवं सदस्य आईडी (ई-केवाईसी पूर्ण)' },
        issuing_authority: { en: 'Samagra Social Security Mission MP', hi: 'समग्र सामाजिक सुरक्षा मिशन, म.प्र.' },
        optional: false,
        guidance: { en: 'Must be linked and e-KYC completed with Aadhaar before applying.', hi: 'समग्र पोर्टल पर आधार ई-केवाईसी पहले से पूर्ण होना अनिवार्य है।' },
      },
      {
        id: 'doc-aadhaar-mp',
        title: { en: 'Aadhaar Card', hi: 'आधार कार्ड' },
        issuing_authority: { en: 'UIDAI', hi: 'भारतीय विशिष्ट पहचान प्राधिकरण' },
        optional: false,
        guidance: { en: 'Must be actively linked to personal DBT bank account.', hi: 'स्वयं के डीबीटी सक्रिय बैंक खाते से लिंक होना चाहिए।' },
      },
      {
        id: 'doc-dbt-bank-mp',
        title: { en: 'Personal Aadhaar-Linked Bank Account (Not joint)', hi: 'व्यक्तिगत बैंक खाता (संयुक्त खाता मान्य नहीं)' },
        issuing_authority: { en: 'Bank', hi: 'बैंक' },
        optional: false,
        guidance: { en: 'Beneficiary woman must have her own independent bank account with DBT active.', hi: 'महिला का स्वयं का एकल बैंक खाता जिसमें डीबीटी सक्षम हो।' },
      },
    ],
    application_steps: [
      {
        step_number: 1,
        title: { en: 'Complete Samagra e-KYC', hi: 'समग्र पोर्टल पर ई-केवाईसी कराएं' },
        description: {
          en: 'Ensure your Samagra ID is linked with your Aadhaar and mobile number.',
          hi: 'अपने समग्र आईडी में आधार लिंक कराएं और बायोमेट्रिक या ओटीपी सत्यापन पूरा करें।',
        },
      },
      {
        step_number: 2,
        title: { en: 'Attend Village / Ward Camp', hi: 'ग्राम पंचायत अथवा वार्ड शिविर में जाएं' },
        description: {
          en: 'Gram Panchayat and Ward offices organize special on-ground camps for form submission and live photo capture.',
          hi: 'ग्राम पंचायत या वार्ड कार्यालय द्वारा आयोजित शिविर में जाएं, जहाँ निःशुल्क ऑनलाइन फॉर्म भरा जाता है।',
        },
      },
    ],
  },
  {
    id: 'pm-jay-ayushman',
    code: 'pm-jay-ayushman',
    name: {
      en: 'Ayushman Bharat PM-JAY (Pradhan Mantri Jan Arogya Yojana)',
      hi: 'आयुष्मान भारत प्रधानमंत्री जन आरोग्य योजना (पीएम-जय)',
    },
    short_name: 'Ayushman Bharat',
    category: 'health',
    level: 'central',
    state_code: 'ALL',
    applicable_states: ['ALL'],
    featured: false,
    description: {
      en: 'Cashless health insurance coverage of up to ₹5 Lakh per family per year for secondary and tertiary care hospitalization across public and empanelled private hospitals in India.',
      hi: 'देश भर के सरकारी एवं सूचीबद्ध निजी अस्पतालों में माध्यमिक एवं तृतीयक स्तर के उपचार हेतु प्रति परिवार प्रति वर्ष ₹5 लाख तक का निःशुल्क कैशलेस स्वास्थ्य कवर।',
    },
    benefits: {
      en: 'Free cashless treatment up to ₹5,00,000 annually per family covering 1,900+ medical procedures, medicines, surgery, pre & post hospitalization.',
      hi: 'प्रति परिवार प्रति वर्ष ₹5,00,000 तक का मुफ्त इलाज। 1,900 से अधिक बीमारियों का ऑपरेशन, दवाएं और अस्पताल का खर्च पूरी तरह कैशलेस।',
    },
    official_source: {
      url: 'https://beneficiary.nha.gov.in',
      last_checked_date: '2026-02-12',
      issuing_ministry: {
        en: 'National Health Authority (NHA), Ministry of Health & Family Welfare',
        hi: 'राष्ट्रीय स्वास्थ्य प्राधिकरण (NHA), स्वास्थ्य एवं परिवार कल्याण मंत्रालय',
      },
      gazette_or_order_ref: 'Ayushman Bharat PM-JAY National Guidelines',
    },
    criteria: [
      {
        id: 'crit-secc-deprivation',
        field: 'is_secc_or_ration_eligible',
        operator: 'EQUALS',
        target_value: true,
        criticality: 'MANDATORY',
        explanation_if_met: {
          en: 'Identified under socio-economic deprivation criteria (D1-D7) or valid NFSA/State Priority Ration Card.',
          hi: 'सामाजिक-आर्थिक वंचित श्रेणी (डी1-डी7) अथवा राष्ट्रीय खाद्य सुरक्षा प्राथमिकता राशन कार्ड सूची में शामिल हैं।',
        },
        explanation_if_violated: {
          en: 'Households must be identified under designated deprivation criteria or state-approved beneficiary databases.',
          hi: 'पात्रता हेतु परिवार का नाम सामाजिक-आर्थिक सूची या अधिकृत राशन कार्ड में होना आवश्यक है।',
        },
      },
    ],
    required_documents: [
      {
        id: 'doc-aadhaar-pmjay',
        title: { en: 'Aadhaar Card', hi: 'आधार कार्ड' },
        issuing_authority: { en: 'UIDAI', hi: 'भारतीय विशिष्ट पहचान प्राधिकरण' },
        optional: false,
        guidance: { en: 'Mandatory for instant e-KYC and Ayushman Card creation.', hi: 'तत्काल ई-केवाईसी और आयुष्मान कार्ड जारी करने हेतु अनिवार्य।' },
      },
      {
        id: 'doc-ration-card-pmjay',
        title: { en: 'Ration Card / Family ID', hi: 'राशन कार्ड अथवा परिवार आईडी' },
        issuing_authority: { en: 'Food Department', hi: 'खाद्य एवं रसद विभाग' },
        optional: false,
        guidance: { en: 'To confirm household linkage and family members.', hi: 'परिवार के सदस्यों के सत्यापन हेतु।' },
      },
    ],
    application_steps: [
      {
        step_number: 1,
        title: { en: 'Check Beneficiary Status Online', hi: 'ऑनलाइन पात्रता की जांच करें' },
        description: {
          en: 'Visit beneficiary.nha.gov.in and search by Aadhaar number, Ration card number, or PMJAY ID.',
          hi: 'beneficiary.nha.gov.in पर जाएं और आधार या राशन कार्ड नंबर दर्ज करके जांच करें।',
        },
      },
      {
        step_number: 2,
        title: { en: 'Ayushman Mitra / Hospital Desk', hi: 'अस्पताल में आयुष्मान मित्र से संपर्क' },
        description: {
          en: 'Approach the Ayushman Mitra helpdesk at any empanelled hospital or CSC to print your PVC card.',
          hi: 'किसी भी सूचीबद्ध अस्पताल या जन सेवा केंद्र पर आयुष्मान मित्र से अपना कार्ड बनवाएं।',
        },
      },
    ],
  },
  {
    id: 'pm-svanidhi',
    code: 'pm-svanidhi',
    name: {
      en: "PM SVANidhi (PM Street Vendor's AtmaNirbhar Nidhi)",
      hi: 'पीएम स्वनिधि (प्रधानमंत्री स्ट्रीट वेंडर आत्मनिर्भर निधि)',
    },
    short_name: 'PM SVANidhi',
    category: 'business',
    level: 'central',
    state_code: 'ALL',
    applicable_states: ['ALL'],
    featured: false,
    description: {
      en: 'Affordable working capital collateral-free micro-credit loans up to ₹50,000 to urban and peri-urban street vendors, with 7% interest subsidy on prompt repayment and digital cashback.',
      hi: 'शहरी एवं उप-शहरी क्षेत्रों के रेहड़ी-पटरी एवं ठेला विक्रेताओं को बिना गारंटी ₹50,000 तक का सस्ता कार्यशील पूंजी ऋण, समय पर भुगतान पर 7% ब्याज सब्सिडी और डिजिटल कैशबैक।',
    },
    benefits: {
      en: 'Initial loan of ₹10,000 (1st tranche), upon timely repayment eligible for ₹20,000 (2nd tranche) and up to ₹50,000 (3rd tranche). 7% interest subsidy directly credited to bank account.',
      hi: 'प्रथम चरण में ₹10,000, समय पर चुकाने पर ₹20,000 और फिर ₹50,000 तक का ऋण। समय पर किश्त भरने पर 7% वार्षिक ब्याज सब्सिडी और प्रति वर्ष ₹1,200 तक कैशबैक।',
    },
    official_source: {
      url: 'https://pmsvanidhi.mohua.gov.in',
      last_checked_date: '2026-02-05',
      issuing_ministry: {
        en: 'Ministry of Housing & Urban Affairs (MoHUA)',
        hi: 'आवासन एवं शहरी कार्य मंत्रालय (MoHUA)',
      },
      gazette_or_order_ref: 'PM SVANidhi Scheme Guidelines (Extension)',
    },
    criteria: [
      {
        id: 'crit-street-vendor',
        field: 'is_street_vendor',
        operator: 'EQUALS',
        target_value: true,
        criticality: 'MANDATORY',
        explanation_if_met: {
          en: 'You are engaged in street vending of goods, articles, food, or daily services in urban/peri-urban areas.',
          hi: 'आप शहरी अथवा कस्बाई क्षेत्रों में रेहड़ी, ठेला या सड़क किनारे सामान या सेवाएं बेचने का कार्य करते हैं।',
        },
        explanation_if_violated: {
          en: 'This micro-credit facility is specifically designed for street vendors and hawkers.',
          hi: 'यह योजना विशेष रूप से रेहड़ी-पटरी एवं ठेला विक्रेताओं के लिए ही है।',
        },
      },
    ],
    required_documents: [
      {
        id: 'doc-vendor-id',
        title: { en: 'Vending Certificate / Identity Card / Letter of Recommendation (LoR)', hi: 'वेंडिंग प्रमाण पत्र / परिचय पत्र / सिफारिश पत्र (LoR)' },
        issuing_authority: { en: 'Urban Local Body (Municipality / Nagar Nigam)', hi: 'नगर निगम / नगर पालिका परिषद' },
        optional: false,
        guidance: { en: 'Issued by Town Vending Committee (TVC) or municipal officer.', hi: 'टाउन वेंडिंग कमेटी या नगर निगम द्वारा जारी किया गया पत्र।' },
      },
      {
        id: 'doc-aadhaar-svanidhi',
        title: { en: 'Aadhaar Card', hi: 'आधार कार्ड' },
        issuing_authority: { en: 'UIDAI', hi: 'भारतीय विशिष्ट पहचान प्राधिकरण' },
        optional: false,
        guidance: { en: 'Identity verification for loan disbursement.', hi: 'पहचान और सत्यापन हेतु।' },
      },
      {
        id: 'doc-bank-account-svanidhi',
        title: { en: 'Bank Savings Account Passbook', hi: 'बैंक बचत खाता पासबुक' },
        issuing_authority: { en: 'Bank', hi: 'बैंक' },
        optional: false,
        guidance: { en: 'Loan amount is disbursed directly into this account.', hi: 'ऋण राशि सीधे इसी बैंक खाते में आएगी।' },
      },
    ],
    application_steps: [
      {
        step_number: 1,
        title: { en: 'Check Vending Status / Apply for LoR', hi: 'वेंडिंग स्थिति जांचें / LoR के लिए आवेदन करें' },
        description: {
          en: 'Check if your name is in the municipal vendor survey, or apply for Letter of Recommendation (LoR) via the portal.',
          hi: 'नगर निगम के विक्रेता सर्वेक्षण में अपना नाम जांचें या पोर्टल पर सिफारिश पत्र (LoR) हेतु आवेदन करें।',
        },
      },
      {
        step_number: 2,
        title: { en: 'Apply for Loan on PM SVANidhi Portal', hi: 'पोर्टल पर ऋण आवेदन करें' },
        description: {
          en: 'Visit pmsvanidhi.mohua.gov.in or any CSC, select preferred lending institution (Lending Bank), and submit.',
          hi: 'pmsvanidhi.mohua.gov.in पर जाएं या सीएससी पर जाकर पसंदीदा बैंक चुनकर फॉर्म सबमिट करें।',
        },
      },
    ],
  },
  {
    id: 'nmmss-scholarship',
    code: 'nmmss-scholarship',
    name: {
      en: 'National Means-cum-Merit Scholarship Scheme (NMMSS)',
      hi: 'राष्ट्रीय साधन-सह-योग्यता छात्रवृत्ति योजना (एनएमएमएसएस)',
    },
    short_name: 'NMMSS Scholarship',
    category: 'education',
    level: 'central',
    state_code: 'ALL',
    applicable_states: ['ALL'],
    featured: false,
    description: {
      en: 'Scholarship of ₹12,000 per annum (₹1,000 per month) awarded to meritorious students of economically weaker sections from class IX to XII to arrest dropouts.',
      hi: 'आर्थिक रूप से कमज़ोर वर्गों के मेधावी छात्र-छात्राओं को कक्षा 9वीं से 12वीं तक पढ़ाई जारी रखने हेतु प्रति वर्ष ₹12,000 (₹1,000 प्रतिमाह) की छात्रवृत्ति।',
    },
    benefits: {
      en: 'Direct scholarship grant of ₹12,000 per academic year credited via DBT through National Scholarship Portal (NSP) for 4 consecutive years (Class 9 to 12).',
      hi: 'कक्षा 9 से 12वीं तक लगातार 4 वर्षों हेतु ₹12,000 प्रति वर्ष की छात्रवृत्ति राष्ट्रीय छात्रवृत्ति पोर्टल (NSP) द्वारा डीबीटी के माध्यम से।',
    },
    official_source: {
      url: 'https://scholarships.gov.in',
      last_checked_date: '2026-01-25',
      issuing_ministry: {
        en: 'Department of School Education & Literacy, Ministry of Education',
        hi: 'स्कूल शिक्षा एवं साक्षरता विभाग, शिक्षा मंत्रालय',
      },
      gazette_or_order_ref: 'NMMSS Revised Scheme Guidelines',
    },
    criteria: [
      {
        id: 'crit-student-income-ceiling',
        field: 'parents_income_below_3_5lakh',
        operator: 'EQUALS',
        target_value: true,
        criticality: 'MANDATORY',
        explanation_if_met: {
          en: 'Parents total annual income from all sources does not exceed ₹3,50,000.',
          hi: 'माता-पिता की सभी स्रोतों से कुल वार्षिक आय ₹3,50,000 से अधिक नहीं है।',
        },
        explanation_if_violated: {
          en: 'Household annual income must be within ₹3.5 Lakh.',
          hi: 'परिवार की वार्षिक आय ₹3.5 लाख की सीमा के अंदर होनी चाहिए।',
        },
      },
      {
        id: 'crit-govt-school-student',
        field: 'studies_in_govt_school',
        operator: 'EQUALS',
        target_value: true,
        criticality: 'MANDATORY',
        explanation_if_met: {
          en: 'Enrolled as a regular student in a Government, Local Body, or Government-aided school.',
          hi: 'सरकारी, स्थानीय निकाय या सहायता प्राप्त विद्यालय में नियमित विद्यार्थी हैं।',
        },
        explanation_if_violated: {
          en: 'Students studying in Kendriya Vidyalayas, Jawahar Navodaya Vidyalayas, Sainik Schools, and residential private schools are not eligible.',
          hi: 'केवी, जेएनवी, सैनिक स्कूल और निजी आवासीय विद्यालयों के छात्र इसके पात्र नहीं हैं।',
        },
      },
    ],
    required_documents: [
      {
        id: 'doc-income-certificate',
        title: { en: 'Parents Income Certificate', hi: 'माता-पिता का आय प्रमाण पत्र' },
        issuing_authority: { en: 'Tehsildar / Revenue Authority', hi: 'तहसीलदार / राजस्व अधिकारी' },
        optional: false,
        guidance: { en: 'Certifying annual income below ₹3.5 Lakh.', hi: 'वार्षिक आय ₹3.5 लाख से कम होने का प्रमाण।' },
      },
      {
        id: 'doc-marksheet-7th-8th',
        title: { en: 'Class VII / VIII Marksheet (minimum 55% marks, 50% for SC/ST)', hi: 'कक्षा 7वीं / 8वीं की अंकसूची (न्यूनतम 55% अंक, एससी/एसटी हेतु 50%)' },
        issuing_authority: { en: 'School Headmaster / Principal', hi: 'विद्यालय के प्रधानाध्यापक' },
        optional: false,
        guidance: { en: 'Academic merit eligibility proof.', hi: 'शैक्षणिक योग्यता प्रमाण हेतु।' },
      },
      {
        id: 'doc-bank-student',
        title: { en: "Student's Own Aadhaar-Linked Bank Account", hi: 'विद्यार्थी का स्वयं का आधार-लिंक बैंक खाता' },
        issuing_authority: { en: 'Bank', hi: 'बैंक' },
        optional: false,
        guidance: { en: 'Scholarship is credited solely to the student’s personal account.', hi: 'छात्रवृत्ति केवल छात्र के स्वयं के खाते में अंतरित होती है।' },
      },
    ],
    application_steps: [
      {
        step_number: 1,
        title: { en: 'Clear State Selection Test', hi: 'राज्य स्तरीय चयन परीक्षा उत्तीर्ण करें' },
        description: {
          en: 'Appear for the Mental Ability Test (MAT) and Scholastic Aptitude Test (SAT) conducted by the state education department in Class VIII.',
          hi: 'कक्षा 8वीं में राज्य द्वारा आयोजित मानसिक योग्यता (MAT) एवं शैक्षिक योग्यता (SAT) परीक्षा उत्तीर्ण करें।',
        },
      },
      {
        step_number: 2,
        title: { en: 'Register on National Scholarship Portal (NSP)', hi: 'राष्ट्रीय छात्रवृत्ति पोर्टल (NSP) पर आवेदन करें' },
        description: {
          en: 'Register on scholarships.gov.in, select NMMSS, and enter details along with school U-DISE code.',
          hi: 'scholarships.gov.in पर जाकर एनएमएमएसएस योजना चुनकर स्कूल कोड और बैंक विवरण भरें।',
        },
      },
    ],
  },
  {
    id: 'ignaps-pension',
    code: 'ignaps-pension',
    name: {
      en: 'Indira Gandhi National Old Age Pension Scheme (IGNOAPS)',
      hi: 'इंदिरा गांधी राष्ट्रीय वृद्धावस्था पेंशन योजना',
    },
    short_name: 'Old Age Pension',
    category: 'social-welfare',
    level: 'central',
    state_code: 'ALL',
    applicable_states: ['ALL'],
    featured: false,
    description: {
      en: 'Monthly social security pension for senior citizens aged 60 and above living below the poverty line (BPL), with supplementary top-up by respective State Governments.',
      hi: 'गरीबी रेखा से नीचे (बीपीएल) जीवन यापन करने वाले 60 वर्ष या उससे अधिक आयु के वृद्धजनों हेतु मासिक सामाजिक सुरक्षा पेंशन।',
    },
    benefits: {
      en: 'Monthly pension of ₹400-₹1,500 (Central contribution + State top-up) credited regularly via DBT into bank or post office savings account.',
      hi: '₹400 से ₹1,500 प्रतिमाह (केंद्र का अंशदान + राज्य सरकार का अतिरिक्त अंश) सीधे बैंक या डाकघर खाते में डीबीटी द्वारा।',
    },
    official_source: {
      url: 'https://nsap.nic.in',
      last_checked_date: '2026-02-14',
      issuing_ministry: {
        en: 'Ministry of Rural Development (National Social Assistance Programme)',
        hi: 'ग्रामीण विकास मंत्रालय (राष्ट्रीय सामाजिक सहायता कार्यक्रम)',
      },
      gazette_or_order_ref: 'NSAP Guidelines Revised 2024',
    },
    criteria: [
      {
        id: 'crit-senior-age-60',
        field: 'age_greater_equal_60',
        operator: 'EQUALS',
        target_value: true,
        criticality: 'MANDATORY',
        explanation_if_met: {
          en: 'You are aged 60 years or above.',
          hi: 'आपकी आयु 60 वर्ष या उससे अधिक है।',
        },
        explanation_if_violated: {
          en: 'Old age pension eligibility commences at 60 years of age.',
          hi: 'वृद्धावस्था पेंशन हेतु न्यूनतम आयु 60 वर्ष अनिवार्य है।',
        },
      },
      {
        id: 'crit-bpl-category',
        field: 'is_bpl_household',
        operator: 'EQUALS',
        target_value: true,
        criticality: 'MANDATORY',
        explanation_if_met: {
          en: 'Household belongs to Below Poverty Line (BPL) category.',
          hi: 'परिवार गरीबी रेखा से नीचे (बीपीएल) श्रेणी में आता है।',
        },
        explanation_if_violated: {
          en: 'Beneficiary must be living below the poverty line as per government criteria.',
          hi: 'लाभार्थी का गरीबी रेखा से नीचे होना अनिवार्य शर्त है।',
        },
      },
    ],
    required_documents: [
      {
        id: 'doc-age-proof',
        title: { en: 'Age Proof (Aadhaar / Voter ID / Birth Certificate)', hi: 'आयु प्रमाण (आधार / मतदाता पहचान पत्र / जन्म प्रमाण पत्र)' },
        issuing_authority: { en: 'Government Authority', hi: 'सक्षम सरकारी प्राधिकारी' },
        optional: false,
        guidance: { en: 'To verify 60+ years age milestone.', hi: '60 वर्ष से अधिक आयु प्रमाणित करने हेतु।' },
      },
      {
        id: 'doc-bpl-card',
        title: { en: 'BPL Ration Card / BPL Certificate', hi: 'बीपीएल राशन कार्ड अथवा बीपीएल प्रमाण पत्र' },
        issuing_authority: { en: 'Block Development Officer / Gram Panchayat', hi: 'खंड विकास अधिकारी / ग्राम पंचायत' },
        optional: false,
        guidance: { en: 'Proof of economic deprivation.', hi: 'आर्थिक स्थिति के सत्यापन हेतु।' },
      },
      {
        id: 'doc-bank-pension',
        title: { en: 'Bank / Post Office Passbook with Aadhaar Seeding', hi: 'बैंक अथवा डाकघर खाता पासबुक (आधार सीडेड)' },
        issuing_authority: { en: 'Bank or Post Office', hi: 'बैंक या डाकघर' },
        optional: false,
        guidance: { en: 'Monthly pension is directly credited here.', hi: 'मासिक पेंशन इसी खाते में प्राप्त होगी।' },
      },
    ],
    application_steps: [
      {
        step_number: 1,
        title: { en: 'Submit Application to Gram Panchayat / Municipality', hi: 'ग्राम पंचायत अथवा नगर पालिका में आवेदन' },
        description: {
          en: 'Obtain NSAP form from Gram Panchayat or Block Development Officer (BDO) in rural areas, or Sub-Divisional Officer (SDO) in urban areas.',
          hi: 'ग्रामीण क्षेत्रों में ग्राम पंचायत/ब्लॉक कार्यालय तथा शहरी क्षेत्रों में नगर पालिका कार्यालय में फॉर्म जमा करें।',
        },
      },
      {
        step_number: 2,
        title: { en: 'Verification by Social Welfare Inspector', hi: 'समाज कल्याण अधिकारी द्वारा जांच' },
        description: {
          en: 'Local administration verifies age and BPL eligibility on records.',
          hi: 'प्रशासनिक अधिकारी द्वारा उम्र और बीपीएल पात्रता का सत्यापन किया जाता है।',
        },
      },
    ],
  },
  {
    id: 'mp-shaikshanik-chatravriti',
    code: 'mp-shaikshanik-chatravriti',
    name: {
      en: 'Shaikshanik Chatravriti Yojana (MP Labour Welfare Board)',
      hi: 'शैक्षणिक छात्रवृत्ति योजना (मध्य प्रदेश श्रम कल्याण मंडल)',
    },
    short_name: 'MP Labour Board Scholarship',
    category: 'education',
    level: 'state',
    state_code: 'MP',
    applicable_states: ['MP'],
    featured: false,
    description: {
      en: 'Scholarship from the Madhya Pradesh Labour Welfare Board for children of workers in establishments covered by the Labour Welfare Fund Act, 1982, studying in Class 5 to 12 or in the listed college and technical courses.',
      hi: 'मध्य प्रदेश श्रम कल्याण मंडल की छात्रवृत्ति, उन श्रमिकों/कर्मचारियों के बच्चों के लिए जो श्रम कल्याण निधि अधिनियम 1982 के दायरे में आने वाले संस्थान में काम करते हैं और कक्षा 5 से 12 या सूचीबद्ध कॉलेज व तकनीकी पाठ्यक्रमों में पढ़ रहे हैं।',
    },
    benefits: {
      en: 'Scholarship at the amount fixed for each class, paid by e-payment to the student’s bank account after the Welfare Commissioner approves it.',
      hi: 'हर कक्षा के लिए तय राशि की छात्रवृत्ति, कल्याण आयुक्त की मंज़ूरी के बाद ई-पेमेंट से छात्र के बैंक खाते में।',
    },
    official_source: {
      url: 'https://scholarshipportal.mp.nic.in/ShramKalyan/Default.aspx',
      // TODO: set this to the day a teammate actually verifies the rules on the official portal / guidelines page.
      last_checked_date: '2026-10-31',
      issuing_ministry: {
        en: 'Madhya Pradesh Labour Welfare Board (Labour Department, Govt of Madhya Pradesh)',
        hi: 'मध्य प्रदेश श्रम कल्याण मंडल (श्रम विभाग, मध्य प्रदेश शासन)',
      },
      gazette_or_order_ref: 'Labour Welfare Fund Act, 1982 (as named on the myScheme page; confirm exact title)',
    },
    criteria: [
      {
        // Source: "Applicant must be a permanent resident of Madhya Pradesh."
        id: 'crit-mp-resident',
        field: 'is_mp_resident',
        operator: 'EQUALS',
        target_value: true,
        criticality: 'MANDATORY',
        explanation_if_met: {
          en: 'You are a permanent resident of Madhya Pradesh.',
          hi: 'आप मध्य प्रदेश के स्थायी निवासी हैं।',
        },
        explanation_if_violated: {
          en: 'Only permanent residents of Madhya Pradesh can apply.',
          hi: 'केवल मध्य प्रदेश के स्थायी निवासी ही आवेदन कर सकते हैं।',
        },
      },
      {
        // Source: "The parents of the applicant must be working in a factory or institution established in
        // Madhya Pradesh under the Labor Welfare Fund Act 1982."
        id: 'crit-parent-lwf-establishment',
        field: 'parent_works_in_lwf_establishment',
        operator: 'EQUALS',
        target_value: true,
        criticality: 'MANDATORY',
        explanation_if_met: {
          en: 'Your parent works in a factory or institution in Madhya Pradesh that is covered by the Labour Welfare Fund Act, 1982.',
          hi: 'आपके माता/पिता मध्य प्रदेश के ऐसे कारखाने या संस्थान में काम करते हैं जो श्रम कल्याण निधि अधिनियम 1982 के दायरे में आता है।',
        },
        explanation_if_violated: {
          en: 'The scheme is only for children of workers in establishments covered by the Labour Welfare Fund Act, 1982.',
          hi: 'यह योजना केवल श्रम कल्याण निधि अधिनियम 1982 के दायरे वाले संस्थानों में काम करने वालों के बच्चों के लिए है।',
        },
      },
      {
        // Source: "Children of officers and employees in managerial capacities working in institutions
        // cannot be benefited from this regime."
        id: 'crit-parent-not-managerial',
        field: 'parent_is_managerial_employee',
        operator: 'EQUALS',
        target_value: false,
        criticality: 'DISQUALIFIER',
        explanation_if_met: {
          en: 'Your parent does not work as an officer or in a managerial role.',
          hi: 'आपके माता/पिता अधिकारी या प्रबंधकीय पद पर काम नहीं करते।',
        },
        explanation_if_violated: {
          en: 'Children of officers and employees in managerial roles are not eligible.',
          hi: 'अधिकारियों और प्रबंधकीय पद पर काम करने वाले कर्मचारियों के बच्चे इस योजना के पात्र नहीं हैं।',
        },
      },
      {
        // Source: "Only 2 children in a family are eligible to get the benefit of this scheme."
        // NOTE: wording is ambiguous; confirm on the official guidelines. Uses a numeric operator:
        // confirm the contract supports LESS_THAN before merging.
        id: 'crit-max-two-children',
        field: 'other_children_already_benefiting',
        operator: 'LESS_THAN',
        target_value: 2,
        criticality: 'MANDATORY',
        explanation_if_met: {
          en: 'Fewer than 2 other children in your family are already receiving this scholarship.',
          hi: 'आपके परिवार के 2 से कम अन्य बच्चे इस छात्रवृत्ति का लाभ ले रहे हैं।',
        },
        explanation_if_violated: {
          en: 'Only 2 children in a family can receive this scholarship.',
          hi: 'एक परिवार के केवल 2 बच्चों को ही यह छात्रवृत्ति मिल सकती है।',
        },
      },
      {
        // Source (Benefits): Class 5th to 12th, Graduation, Post Graduation, ITI, Polytechnic,
        // PGDCA, DCA, B.E., M.B.B.S., M.Sc.
        id: 'crit-covered-course',
        field: 'studies_in_covered_course',
        operator: 'EQUALS',
        target_value: true,
        criticality: 'MANDATORY',
        explanation_if_met: {
          en: 'You study in Class 5 to 12 or in a listed course (graduation, post graduation, ITI, polytechnic, PGDCA, DCA, B.E., M.B.B.S., M.Sc.).',
          hi: 'आप कक्षा 5 से 12 में या सूचीबद्ध पाठ्यक्रम (स्नातक, स्नातकोत्तर, आईटीआई, पॉलिटेक्निक, पीजीडीसीए, डीसीए, बी.ई., एम.बी.बी.एस., एम.एससी.) में पढ़ रहे हैं।',
        },
        explanation_if_violated: {
          en: 'The scholarship covers only Class 5 to 12 and the listed courses.',
          hi: 'छात्रवृत्ति केवल कक्षा 5 से 12 और सूचीबद्ध पाठ्यक्रमों के लिए है।',
        },
      },
    ],
    required_documents: [
      {
        id: 'doc-mplwb-photo',
        title: { en: 'Latest passport-size photograph (JPEG)', hi: 'हाल की पासपोर्ट साइज़ फ़ोटो (JPEG)' },
        issuing_authority: { en: 'Self', hi: 'स्वयं' },
        optional: false,
        guidance: { en: 'Photograph of the student applying.', hi: 'आवेदन करने वाले छात्र की फ़ोटो।' },
      },
      {
        id: 'doc-mplwb-marksheet',
        title: { en: 'Previous year’s mark sheet (JPEG)', hi: 'पिछले वर्ष की अंकसूची (JPEG)' },
        issuing_authority: { en: 'School / College / Institute', hi: 'स्कूल / कॉलेज / संस्थान' },
        optional: false,
        guidance: { en: 'Of the class or course the student has passed.', hi: 'उस कक्षा या पाठ्यक्रम की जो छात्र ने उत्तीर्ण किया है।' },
      },
      {
        id: 'doc-mplwb-bank',
        title: { en: 'First page of the student’s bank passbook', hi: 'छात्र की बैंक पासबुक का पहला पृष्ठ' },
        issuing_authority: { en: 'Bank', hi: 'बैंक' },
        optional: false,
        guidance: {
          en: 'Must clearly show the student’s name, account number and IFSC code.',
          hi: 'इसमें छात्र का नाम, खाता संख्या और आईएफ़एससी कोड साफ़ दिखना चाहिए।',
        },
      },
      {
        id: 'doc-mplwb-aadhaar-numbers',
        title: { en: 'Aadhaar numbers of the student and a parent', hi: 'छात्र और माता/पिता के आधार नंबर' },
        issuing_authority: { en: 'UIDAI', hi: 'भारतीय विशिष्ट पहचान प्राधिकरण' },
        optional: false,
        // Source lists Aadhaar numbers for authentication, not under "Documents Required". Confirm.
        guidance: {
          en: 'Needed to confirm identity while applying online.',
          hi: 'ऑनलाइन आवेदन के समय पहचान की पुष्टि के लिए ज़रूरी।',
        },
      },
    ],
    application_steps: [
      {
        step_number: 1,
        title: { en: 'Register on the scholarship portal', hi: 'छात्रवृत्ति पोर्टल पर पंजीकरण करें' },
        description: {
          en: 'Go to the Shram Kalyan scholarship portal (scholarshipportal.mp.nic.in/ShramKalyan) and choose "Do Registration".',
          hi: 'श्रम कल्याण छात्रवृत्ति पोर्टल (scholarshipportal.mp.nic.in/ShramKalyan) पर जाएं और "पंजीकरण करें" चुनें।',
        },
      },
      {
        step_number: 2,
        title: { en: 'Fill the form and verify with Aadhaar', hi: 'फ़ॉर्म भरें और आधार से पहचान सत्यापित करें' },
        description: {
          en: 'Fill in the scholarship application and confirm identity using your own and your mother’s or father’s Aadhaar number.',
          hi: 'छात्रवृत्ति आवेदन भरें और अपने तथा माता या पिता के आधार नंबर से पहचान की पुष्टि करें।',
        },
      },
      {
        step_number: 3,
        title: { en: 'Upload documents before the last date', hi: 'अंतिम तिथि से पहले दस्तावेज़ जमा करें' },
        description: {
          en: 'Attach the required documents and apply within the time set by the board. Late applications are not considered.',
          hi: 'ज़रूरी दस्तावेज़ लगाएं और मंडल द्वारा तय समय-सीमा में आवेदन करें। देर से आए आवेदनों पर विचार नहीं किया जाता।',
        },
      },
    ],
  },
  {
    id: 'mp-st-girl-literacy-class11',
    code: 'mp-st-girl-literacy-class11',
    name: {
      en: 'ST Girl Child Literacy Incentive Amount - Class 11th',
      hi: 'अनुसूचित जनजाति बालिका साक्षरता प्रोत्साहन राशि - कक्षा 11वीं',
    },
    short_name: 'ST Girl Literacy Incentive (Class 11)',
    category: 'education',
    level: 'state',
    state_code: 'MP',
    applicable_states: ['MP'],
    featured: false,
    description: {
      en: 'Financial support from the Government of Madhya Pradesh for Scheduled Tribe girl students studying in Class 11, so they can continue their education without financial barriers.',
      hi: 'मध्य प्रदेश शासन की ओर से कक्षा 11 में पढ़ रही अनुसूचित जनजाति की छात्राओं को आर्थिक सहायता, ताकि पैसों की कमी से उनकी पढ़ाई न रुके।',
    },
    benefits: {
      en: 'Annual incentive of ₹3,000, credited directly to the student’s bank account after verification.',
      hi: 'सत्यापन के बाद ₹3,000 की वार्षिक प्रोत्साहन राशि सीधे छात्रा के बैंक खाते में।',
    },
    official_source: {
      url: 'https://shikshaportal.mp.gov.in/',
      last_checked_date: null, // TODO: set when a teammate verifies on the portal
      issuing_ministry: {
        en: 'School Education Department, Government of Madhya Pradesh',
        hi: 'स्कूल शिक्षा विभाग, मध्य प्रदेश शासन',
      },
      gazette_or_order_ref: null,
    },
    criteria: [
      {
        // CONFIRM (important): the source contradicts itself. Title, first sentence of Details,
        // Documents ("Caste Certificate (ST)") and the FAQ say ST. The rest of Details, Benefits
        // and Eligibility point 1 say SC / "Scheduled Caste". We used ST (title + documents +
        // FAQ agree). Check the official guideline before this goes live: wrong category here
        // tells an SC student she qualifies, or an ST student she does not.
        id: 'crit-st-category',
        field: 'social_category',
        operator: 'EQUALS',
        target_value: 'ST',
        criticality: 'MANDATORY',
        explanation_if_met: {
          en: 'You belong to the Scheduled Tribe category.',
          hi: 'आप अनुसूचित जनजाति वर्ग से हैं।',
        },
        explanation_if_violated: {
          en: 'This scheme is only for girl students of the Scheduled Tribe category (our source also mentions Scheduled Caste, so please confirm with your school).',
          hi: 'यह योजना केवल अनुसूचित जनजाति वर्ग की छात्राओं के लिए है (हमारे स्रोत में अनुसूचित जाति का भी ज़िक्र है, इसलिए अपने स्कूल से पुष्टि कर लें)।',
        },
      },
      {
        id: 'crit-girl-student',
        field: 'is_female',
        operator: 'EQUALS',
        target_value: true,
        criticality: 'MANDATORY',
        explanation_if_met: {
          en: 'The applicant is a girl student.',
          hi: 'आवेदक एक छात्रा है।',
        },
        explanation_if_violated: {
          en: 'This incentive is only for girl students.',
          hi: 'यह प्रोत्साहन राशि केवल छात्राओं के लिए है।',
        },
      },
      {
        id: 'crit-mp-resident-st-girl',
        field: 'is_mp_resident',
        operator: 'EQUALS',
        target_value: true,
        criticality: 'MANDATORY',
        explanation_if_met: {
          en: 'You belong to Madhya Pradesh.',
          hi: 'आप मध्य प्रदेश के निवासी हैं।',
        },
        explanation_if_violated: {
          en: 'The scheme is for students of Madhya Pradesh.',
          hi: 'यह योजना मध्य प्रदेश की छात्राओं के लिए है।',
        },
      },
      {
        // CONFIRM: "continuously studying" is not defined (no attendance rule given).
        // We only ask which class she is in now.
        id: 'crit-class-11',
        field: 'current_class',
        operator: 'EQUALS',
        target_value: 11,
        criticality: 'MANDATORY',
        explanation_if_met: {
          en: 'You are studying in Class 11.',
          hi: 'आप कक्षा 11 में पढ़ रही हैं।',
        },
        explanation_if_violated: {
          en: 'This version of the scheme is only for Class 11 students.',
          hi: 'यह योजना केवल कक्षा 11 की छात्राओं के लिए है।',
        },
      },
      {
        // CONFIRM: Eligibility says "recognized institution", but the application process
        // says to contact the Principal of "government schools/institutions". Unclear whether
        // private recognized schools are covered. Not turned into a rule until confirmed.
        id: 'crit-family-income-6lakh',
        field: 'annual_family_income',
        operator: 'LESS_THAN_OR_EQUAL',
        target_value: 600000,
        criticality: 'MANDATORY',
        explanation_if_met: {
          en: 'Your family’s yearly income is ₹6,00,000 or less.',
          hi: 'आपके परिवार की वार्षिक आय ₹6,00,000 या उससे कम है।',
        },
        explanation_if_violated: {
          en: 'Family yearly income must not be more than ₹6,00,000.',
          hi: 'परिवार की वार्षिक आय ₹6,00,000 से अधिक नहीं होनी चाहिए।',
        },
      },
      {
        // Source: "self-declaration that the parent/guardian is not an income tax payer".
        id: 'crit-parent-not-taxpayer',
        field: 'parent_is_income_taxpayer',
        operator: 'EQUALS',
        target_value: false,
        criticality: 'DISQUALIFIER',
        explanation_if_met: {
          en: 'Your parent or guardian does not pay income tax.',
          hi: 'आपके माता-पिता या अभिभावक आयकर नहीं भरते।',
        },
        explanation_if_violated: {
          en: 'The parent or guardian must not be an income tax payer.',
          hi: 'माता-पिता या अभिभावक आयकर दाता नहीं होने चाहिए।',
        },
      },
    ],
    required_documents: [
      {
        id: 'doc-stg-aadhaar',
        title: { en: 'Aadhaar Card', hi: 'आधार कार्ड' },
        issuing_authority: { en: 'UIDAI', hi: 'भारतीय विशिष्ट पहचान प्राधिकरण' },
        optional: false,
        guidance: { en: 'Identity proof of the student.', hi: 'छात्रा की पहचान के लिए।' },
      },
      {
        id: 'doc-stg-caste',
        title: { en: 'Permanent Caste Certificate (ST)', hi: 'स्थायी जाति प्रमाण पत्र (अनुसूचित जनजाति)' },
        issuing_authority: { en: 'Sub-Divisional Officer (Revenue)', hi: 'अनुविभागीय अधिकारी (राजस्व)' },
        optional: false,
        guidance: { en: 'A verified copy of the permanent certificate is needed.', hi: 'स्थायी प्रमाण पत्र की सत्यापित प्रति आवश्यक है।' },
      },
      {
        id: 'doc-stg-domicile',
        title: { en: 'Domicile Certificate', hi: 'मूल निवासी प्रमाण पत्र' },
        issuing_authority: { en: 'Revenue Authority', hi: 'राजस्व विभाग' },
        optional: false,
        // CONFIRM: issuing authority not stated in source; "Revenue Authority" is our assumption.
        guidance: { en: 'Proof that you live in Madhya Pradesh.', hi: 'मध्य प्रदेश के निवासी होने का प्रमाण।' },
      },
      {
        id: 'doc-stg-class10-marksheet',
        title: { en: 'Class 10 Marksheet', hi: 'कक्षा 10वीं की अंकसूची' },
        issuing_authority: { en: 'School / Board', hi: 'विद्यालय / बोर्ड' },
        optional: false,
        guidance: { en: 'Shows you passed Class 10.', hi: 'कक्षा 10 उत्तीर्ण करने का प्रमाण।' },
      },
      {
        id: 'doc-stg-bank',
        title: { en: 'Bank Passbook', hi: 'बैंक पासबुक' },
        issuing_authority: { en: 'Bank', hi: 'बैंक' },
        optional: false,
        guidance: { en: 'The ₹3,000 is credited to this account.', hi: '₹3,000 की राशि इसी खाते में आएगी।' },
      },
      {
        id: 'doc-stg-admission',
        title: { en: 'School Admission Proof', hi: 'विद्यालय में प्रवेश का प्रमाण' },
        issuing_authority: { en: 'School', hi: 'विद्यालय' },
        optional: false,
        guidance: { en: 'Shows you are enrolled in Class 11.', hi: 'कक्षा 11 में प्रवेश का प्रमाण।' },
      },
      {
        id: 'doc-stg-photo',
        title: { en: 'Recent passport-size photograph', hi: 'हाल की पासपोर्ट साइज़ फ़ोटो' },
        issuing_authority: { en: 'Self', hi: 'स्वयं' },
        optional: false,
        guidance: { en: 'Photograph of the student.', hi: 'छात्रा की फ़ोटो।' },
      },
      {
        // Listed in Eligibility points 5 and 6, but NOT in the source's "Documents Required".
        // CONFIRM and keep: without them the income and tax conditions cannot be shown.
        id: 'doc-stg-income-cert',
        title: { en: 'Income certificate or salary certificate', hi: 'आय प्रमाण पत्र या वेतन प्रमाण पत्र' },
        issuing_authority: { en: 'Competent authority', hi: 'सक्षम प्राधिकारी' },
        optional: false,
        guidance: { en: 'Shows family income is within ₹6,00,000.', hi: 'परिवार की आय ₹6,00,000 के भीतर होने का प्रमाण।' },
      },
      {
        id: 'doc-stg-selfdecl-tax',
        title: { en: 'Self-declaration: parent/guardian is not an income tax payer', hi: 'स्व-घोषणा पत्र: माता-पिता/अभिभावक आयकर दाता नहीं हैं' },
        issuing_authority: { en: 'Self (parent or guardian)', hi: 'स्वयं (माता-पिता या अभिभावक)' },
        optional: false,
        guidance: { en: 'A signed declaration.', hi: 'हस्ताक्षरित घोषणा पत्र।' },
      },
    ],
    application_steps: [
      {
        step_number: 1,
        title: { en: 'Meet the school Principal', hi: 'स्कूल के प्राचार्य से मिलें' },
        description: {
          en: 'Contact the Principal of your government school or institution with your documents.',
          hi: 'अपने दस्तावेज़ लेकर सरकारी स्कूल/संस्थान के प्राचार्य से संपर्क करें।',
        },
      },
      {
        step_number: 2,
        title: { en: 'School enters your details online', hi: 'स्कूल ऑनलाइन विवरण दर्ज करता है' },
        description: {
          en: 'A teacher enters your profile on shikshaportal.mp.gov.in from the records and certificates you give. You do not fill this online yourself.',
          hi: 'शिक्षक आपके दिए प्रमाण पत्रों के आधार पर shikshaportal.mp.gov.in पर आपकी प्रोफ़ाइल दर्ज करते हैं। आपको स्वयं ऑनलाइन फॉर्म नहीं भरना है।',
        },
      },
      {
        step_number: 3,
        title: { en: 'Track and receive the amount', hi: 'स्थिति देखें और राशि पाएं' },
        description: {
          en: 'You can track your status on shikshaportal.mp.gov.in. After verification, ₹3,000 is sent to your bank account.',
          hi: 'shikshaportal.mp.gov.in पर अपनी स्थिति देख सकते हैं। सत्यापन के बाद ₹3,000 बैंक खाते में आएंगे।',
        },
      },
    ],
  },,
  {
    id: 'ksb-home-loan-interest-subsidy',
    code: 'ksb-home-loan-interest-subsidy',
    name: {
      en: 'Financial Assistance as Interest Subsidy on Home Loan (Ex-Servicemen)',
      hi: 'गृह ऋण पर ब्याज सब्सिडी के रूप में वित्तीय सहायता (पूर्व सैनिक)',
    },
    short_name: 'Ex-Servicemen Home Loan Interest Subsidy',
    category: 'housing',
    level: 'central',
    state_code: 'ALL',
    applicable_states: ['ALL'],
    featured: false,
    description: {
      en: 'Relief from the Kendriya Sainik Board for war widows, war-bereaved families, war-disabled personnel and attributable peacetime casualties (all ranks): the Government pays back 50% of the interest on a home loan.',
      hi: 'केंद्रीय सैनिक बोर्ड की ओर से युद्ध विधवाओं, युद्ध में शहीद सैनिकों के परिवारों, युद्ध में विकलांग हुए सैनिकों और शांतिकाल में सेवा के कारण हताहत हुए (सभी रैंक) सैनिकों को गृह ऋण के ब्याज का 50% वापस।',
    },
    benefits: {
      en: '50% of the interest on your home loan is reimbursed. Only up to ₹1,00,000 of the loan is counted, even if your loan is larger. The subsidy runs for at most 5 years, or until the loan is repaid, whichever is earlier. The loan must be from a bank, a Government or public sector undertaking, LIC, GIC or HUDCO. Payment is made online after approval, when funds are available.',
      hi: 'आपके गृह ऋण के ब्याज का 50% लौटाया जाता है। ऋण चाहे अधिक हो, केवल ₹1,00,000 तक के ऋण को गिना जाता है। सब्सिडी अधिकतम 5 वर्ष, या ऋण चुकने तक, जो भी पहले हो, मिलती है। ऋण बैंक, सरकारी या सार्वजनिक क्षेत्र के उपक्रम, एलआईसी, जीआईसी या हुडको से लिया होना चाहिए। मंज़ूरी के बाद, धन उपलब्ध होने पर भुगतान ऑनलाइन होता है।',
    },
    official_source: {
      url: 'https://www.ksb.gov.in/',
      last_checked_date: null, // TODO: set when verified
      issuing_ministry: {
        en: 'Kendriya Sainik Board, Department of Ex-Servicemen Welfare, Ministry of Defence',
        hi: 'केंद्रीय सैनिक बोर्ड, पूर्व सैनिक कल्याण विभाग, रक्षा मंत्रालय',
      },
      gazette_or_order_ref: null,
    },
    criteria: [
      {
        id: 'crit-ksb-applicant-category',
        field: 'servicemen_welfare_category',
        operator: 'IN',
        target_value: ['WAR_WIDOW', 'WAR_BEREAVED_FAMILY', 'WAR_DISABLED', 'ATTRIBUTABLE_PEACETIME_CASUALTY'],
        criticality: 'MANDATORY',
        explanation_if_met: {
          en: 'You are a war widow, a member of a war-bereaved family, war-disabled personnel, or an attributable peacetime casualty (all ranks).',
          hi: 'आप युद्ध विधवा, युद्ध में शहीद सैनिक के परिवार के सदस्य, युद्ध में विकलांग हुए सैनिक, या शांतिकाल में सेवा के कारण हताहत (सभी रैंक) हैं।',
        },
        explanation_if_violated: {
          en: 'The scheme is only for war widows, war-bereaved families, war-disabled personnel and attributable peacetime casualties. Other ex-servicemen are not covered.',
          hi: 'यह योजना केवल युद्ध विधवाओं, शहीद सैनिकों के परिवारों, युद्ध में विकलांग सैनिकों और शांतिकाल में सेवा के कारण हताहत सैनिकों के लिए है। अन्य पूर्व सैनिक शामिल नहीं हैं।',
        },
      },
      {
        // CONFIRM: Eligibility says a loan from "a bank", but the FAQ says a loan from a
        // private bank does not count ("only approved banks, government/public sector
        // undertakings, LIC, GIC and HUDCO"). The source does not say which banks are
        // "approved". Check the KSB scheme page and add the correct list of lender types.
        id: 'crit-ksb-approved-lender',
        field: 'home_loan_lender_type',
        operator: 'IN',
        target_value: ['APPROVED_BANK', 'GOVT_PSU', 'LIC', 'GIC', 'HUDCO'],
        criticality: 'MANDATORY',
        explanation_if_met: {
          en: 'Your home loan is from an approved bank, a Government or public sector undertaking, LIC, GIC or HUDCO.',
          hi: 'आपका गृह ऋण किसी मान्य बैंक, सरकारी या सार्वजनिक क्षेत्र के उपक्रम, एलआईसी, जीआईसी या हुडको से है।',
        },
        explanation_if_violated: {
          en: 'The home loan must be from an approved bank, a Government or public sector undertaking, LIC, GIC or HUDCO. A loan from a private lender may not count.',
          hi: 'गृह ऋण किसी मान्य बैंक, सरकारी या सार्वजनिक क्षेत्र के उपक्रम, एलआईसी, जीआईसी या हुडको से होना चाहिए। निजी ऋणदाता से लिया ऋण मान्य नहीं हो सकता।',
        },
      },
      {
        // From the documents section: the banker must certify that repayment of the loan and
        // interest was regular and the repayment schedule has not changed. It is not in the
        // Eligibility list, but without it the claim cannot be made. CONFIRM.
        id: 'crit-ksb-regular-repayment',
        field: 'loan_repayment_regular',
        operator: 'EQUALS',
        target_value: true,
        criticality: 'MANDATORY',
        explanation_if_met: {
          en: 'You have repaid the loan and interest regularly, and the repayment schedule has not been changed.',
          hi: 'आपने ऋण और ब्याज नियमित रूप से चुकाया है और चुकौती की समय-सारणी में कोई बदलाव नहीं हुआ है।',
        },
        explanation_if_violated: {
          en: 'The bank must certify that repayment was regular and the schedule did not change. Irregular repayment can block the claim.',
          hi: 'बैंक को प्रमाणित करना होता है कि चुकौती नियमित रही और समय-सारणी नहीं बदली। अनियमित चुकौती से दावा रुक सकता है।',
        },
      },
      // Not a criterion: the ₹1,00,000 limit is a cap on the loan amount counted, not a reason
      // to refuse (the source says "regardless of the actual loan amount").
    ],
    required_documents: [
      {
        id: 'doc-ksb-ex-servicemen-id',
        title: { en: 'Ex-Servicemen Identity Card (attested copy)', hi: 'पूर्व सैनिक पहचान पत्र (सत्यापित प्रति)' },
        issuing_authority: { en: 'Armed Forces / Department of Ex-Servicemen Welfare', hi: 'सशस्त्र बल / पूर्व सैनिक कल्याण विभाग' },
        optional: false,
        guidance: { en: 'A duly attested copy.', hi: 'विधिवत सत्यापित प्रति।' },
      },
      {
        // CONFIRM: for a war widow or war-bereaved family, the Discharge Book would be the
        // soldier’s, and may not exist. Check with the District Sainik Board what they accept.
        id: 'doc-ksb-discharge-book',
        title: { en: 'Discharge Book (attested copy)', hi: 'डिस्चार्ज बुक (सत्यापित प्रति)' },
        issuing_authority: { en: 'Armed Forces', hi: 'सशस्त्र बल' },
        optional: false,
        guidance: { en: 'A duly attested copy.', hi: 'विधिवत सत्यापित प्रति।' },
      },
      {
        id: 'doc-ksb-no-change-cert',
        title: { en: 'Certificate that the repayment schedule has not changed', hi: 'प्रमाण पत्र कि चुकौती की समय-सारणी में बदलाव नहीं हुआ' },
        issuing_authority: { en: 'Your bank or lender (Government/PSU, LIC, GIC, HUDCO)', hi: 'आपका बैंक या ऋणदाता (सरकारी/पीएसयू, एलआईसी, जीआईसी, हुडको)' },
        optional: false,
        guidance: { en: 'Ask your lender for this certificate.', hi: 'यह प्रमाण पत्र अपने ऋणदाता से लें।' },
      },
      {
        id: 'doc-ksb-interest-statement',
        title: { en: 'Statement of interest actually paid for the claim period', hi: 'दावे की अवधि में वास्तव में चुकाए गए ब्याज का विवरण' },
        issuing_authority: { en: 'Your bank or lender', hi: 'आपका बैंक या ऋणदाता' },
        optional: false,
        guidance: { en: 'Shows the interest you paid.', hi: 'आपके द्वारा चुकाया गया ब्याज दर्शाता है।' },
      },
      {
        id: 'doc-ksb-regular-repayment-cert',
        title: { en: 'Certificate that loan and interest were repaid regularly', hi: 'प्रमाण पत्र कि ऋण और ब्याज नियमित रूप से चुकाए गए' },
        issuing_authority: { en: 'Your bank or lender', hi: 'आपका बैंक या ऋणदाता' },
        optional: false,
        guidance: { en: 'Ask your lender for this certificate.', hi: 'यह प्रमाण पत्र अपने ऋणदाता से लें।' },
      },
      {
        // Listed only in the online upload step, not in "Documents Required". CONFIRM.
        id: 'doc-ksb-photo',
        title: { en: 'Photograph', hi: 'फ़ोटो' },
        issuing_authority: { en: 'Self', hi: 'स्वयं' },
        optional: false,
        guidance: { en: 'To upload with the online application.', hi: 'ऑनलाइन आवेदन के साथ अपलोड करने के लिए।' },
      },
      {
        id: 'doc-ksb-bank-passbook',
        title: { en: 'Bank passbook', hi: 'बैंक पासबुक' },
        issuing_authority: { en: 'Bank', hi: 'बैंक' },
        optional: false,
        guidance: { en: 'The subsidy is paid online into your bank account.', hi: 'सब्सिडी ऑनलाइन आपके बैंक खाते में आती है।' },
      },
      {
        // CONFIRM: the upload step also mentions a caste certificate and a residential
        // certificate. These look copied from another scheme (the same page even says
        // "eligible students"). Not in the Documents Required list. Ask the District Sainik
        // Board whether they are really needed.
        id: 'doc-ksb-residential-cert',
        title: { en: 'Residential certificate and caste certificate', hi: 'निवास प्रमाण पत्र और जाति प्रमाण पत्र' },
        issuing_authority: { en: 'Competent authority', hi: 'सक्षम प्राधिकारी' },
        optional: true,
        guidance: {
          en: 'The online form mentions these, but the document list does not. Check with your District Sainik Board before arranging them.',
          hi: 'ऑनलाइन फ़ॉर्म में इनका उल्लेख है, पर दस्तावेज़ सूची में नहीं। इन्हें बनवाने से पहले अपने ज़िला सैनिक बोर्ड से पूछ लें।',
        },
      },
    ],
    application_steps: [
      {
        step_number: 1,
        title: { en: 'Register on the Kendriya Sainik Board website', hi: 'केंद्रीय सैनिक बोर्ड की वेबसाइट पर पंजीकरण करें' },
        description: {
          en: 'On ksb.gov.in choose "Register". Fill in your name, Aadhaar number, email ID, mobile number and bank details, and set a password. You then get a User ID and password.',
          hi: 'ksb.gov.in पर "Register" चुनें। अपना नाम, आधार नंबर, ईमेल, मोबाइल नंबर और बैंक विवरण भरें और पासवर्ड बनाएँ। इसके बाद आपको यूज़र आईडी और पासवर्ड मिलेगा।',
        },
      },
      {
        step_number: 2,
        title: { en: 'Fill the online application', hi: 'ऑनलाइन आवेदन भरें' },
        description: {
          en: 'Log in, click "New Application", select this scheme, fill in the form and upload the documents.',
          hi: 'लॉग इन करें, "New Application" पर क्लिक करें, यह योजना चुनें, फ़ॉर्म भरें और दस्तावेज़ अपलोड करें।',
        },
      },
      {
        step_number: 3,
        title: { en: 'Save, print and submit to the District Sainik Board', hi: 'सेव करें, प्रिंट लें और ज़िला सैनिक बोर्ड में जमा करें' },
        description: {
          en: 'Click "Save & Forward", take a printout, and submit it with all the required documents to your District Sainik Board. The Kendriya Sainik Board then checks and approves it, and payment is made online when funds are available.',
          hi: '"Save & Forward" पर क्लिक करें, प्रिंट निकालें और सभी ज़रूरी दस्तावेज़ों के साथ अपने ज़िला सैनिक बोर्ड में जमा करें। इसके बाद केंद्रीय सैनिक बोर्ड जाँच कर मंज़ूरी देता है और धन उपलब्ध होने पर भुगतान ऑनलाइन होता है।',
        },
      },
    ],
  },
  {
    id: 'pmksy-per-drop-more-crop',
    code: 'pmksy-per-drop-more-crop',
    name: {
      en: 'PM Krishi Sinchayee Yojana: Per Drop More Crop',
      hi: 'प्रधानमंत्री कृषि सिंचाई योजना: पर ड्रॉप मोर क्रॉप',
    },
    short_name: 'PMKSY Per Drop More Crop',
    category: 'agriculture',
    level: 'central',
    state_code: 'ALL',
    applicable_states: ['ALL'],
    featured: false,
    description: {
      en: 'Subsidy for farmers to install drip and sprinkler irrigation so that every drop of water gives more crop. It also supports farm ponds and other water-saving work.',
      hi: 'किसानों को ड्रिप और स्प्रिंकलर सिंचाई लगाने के लिए सब्सिडी, ताकि हर बूंद से अधिक फसल मिले। खेत तालाब जैसे जल-संरक्षण कार्यों में भी सहायता।',
    },
    benefits: {
      en: 'Subsidy of 55% of the cost for small and marginal farmers and 45% for other farmers, limited to 5 hectares per farmer, paid by Direct Benefit Transfer. The cost is shared between Centre and State 60:40 (90:10 for North Eastern and Himalayan states; 100% Centre for Union Territories).',
      hi: 'लघु और सीमांत किसानों को लागत का 55% और अन्य किसानों को 45% सब्सिडी, प्रति किसान अधिकतम 5 हेक्टेयर तक, डीबीटी से। लागत केंद्र और राज्य में 60:40 बंटती है (पूर्वोत्तर और हिमालयी राज्यों में 90:10; केंद्र शासित प्रदेशों में 100% केंद्र)।',
    },
    official_source: {
      // Site found and opened on 2026-10-31 (it is the portal for all of PMKSY). Rules NOT yet checked against it.
      url: 'https://pmksy.gov.in/',
      last_checked_date: null, // TODO: set to the day a teammate verifies the rules on the official site
      issuing_ministry: {
        en: 'Department of Agriculture & Farmers Welfare, Ministry of Agriculture & Farmers Welfare',
        hi: 'कृषि एवं किसान कल्याण विभाग, कृषि एवं किसान कल्याण मंत्रालय',
      },
      gazette_or_order_ref: 'Launched 1 July 2015 (as stated on the myScheme page)',
    },
    criteria: [
      {
        id: 'crit-pdmc-citizen',
        field: 'is_indian_citizen',
        operator: 'EQUALS',
        target_value: true,
        criticality: 'MANDATORY',
        explanation_if_met: {
          en: 'You are a citizen of India.',
          hi: 'आप भारत के नागरिक हैं।',
        },
        explanation_if_violated: {
          en: 'The applicant should be a citizen of India.',
          hi: 'आवेदक भारत का नागरिक होना चाहिए।',
        },
      },
      {
        id: 'crit-pdmc-farmer',
        field: 'is_farmer',
        operator: 'EQUALS',
        target_value: true,
        criticality: 'MANDATORY',
        explanation_if_met: {
          en: 'You are a farmer. The scheme is open to all farmers.',
          hi: 'आप किसान हैं। यह योजना सभी किसानों के लिए है।',
        },
        explanation_if_violated: {
          en: 'The scheme is for farmers.',
          hi: 'यह योजना किसानों के लिए है।',
        },
      },
    ],
    required_documents: [
      {
        id: 'doc-pdmc-aadhaar',
        title: { en: 'Aadhaar Card', hi: 'आधार कार्ड' },
        issuing_authority: { en: 'UIDAI', hi: 'भारतीय विशिष्ट पहचान प्राधिकरण' },
        optional: false,
        guidance: {
          en: 'Aadhaar details are needed because the subsidy is paid by Direct Benefit Transfer.',
          hi: 'सब्सिडी डीबीटी से मिलती है, इसलिए आधार विवरण ज़रूरी है।',
        },
      },
      {
        id: 'doc-pdmc-bank',
        title: { en: 'Bank account details', hi: 'बैंक खाते का विवरण' },
        issuing_authority: { en: 'Bank', hi: 'बैंक' },
        optional: false,
      },
      {
        id: 'doc-pdmc-address',
        title: { en: 'Address proof', hi: 'पते का प्रमाण' },
        issuing_authority: { en: 'Government authority', hi: 'सरकारी प्राधिकारी' },
        optional: false,
      },
      {
        id: 'doc-pdmc-photo',
        title: { en: 'Passport-size photograph', hi: 'पासपोर्ट साइज़ फ़ोटो' },
        issuing_authority: { en: 'Self', hi: 'स्वयं' },
        optional: false,
        guidance: {
          en: 'Paste it on the form and sign across it.',
          hi: 'फ़ॉर्म पर चिपकाएं और उस पर हस्ताक्षर करें।',
        },
      },
      {
        id: 'doc-pdmc-caste',
        title: { en: 'Caste certificate (if applicable)', hi: 'जाति प्रमाण पत्र (यदि लागू हो)' },
        issuing_authority: { en: 'Competent authority', hi: 'सक्षम अधिकारी' },
        optional: true,
      },
      {
        id: 'doc-pdmc-land',
        title: { en: 'Proof of agricultural land', hi: 'कृषि भूमि के दस्तावेज़' },
        issuing_authority: { en: 'State Revenue Department', hi: 'राज्य राजस्व विभाग' },
        optional: false,
      },
      {
        id: 'doc-pdmc-domicile',
        title: { en: 'Domicile certificate of the State / UT', hi: 'राज्य / केंद्र शासित प्रदेश का मूल निवासी प्रमाण पत्र' },
        issuing_authority: { en: 'Revenue Department', hi: 'राजस्व विभाग' },
        optional: false,
      },
    ],
    application_steps: [
      {
        step_number: 1,
        title: { en: 'Contact the agriculture office', hi: 'कृषि कार्यालय से संपर्क करें' },
        description: {
          en: 'Contact your Block or District Agriculture Office through your Gram Panchayat, or call the Kisan Call Centre on 1800-180-1551 (toll free), and ask for the application form.',
          hi: 'अपनी ग्राम पंचायत के माध्यम से ब्लॉक या जिला कृषि कार्यालय से संपर्क करें, या किसान कॉल सेंटर 1800-180-1551 (टोल फ्री) पर कॉल करें और आवेदन फ़ॉर्म लें।',
        },
      },
      {
        step_number: 2,
        title: { en: 'Fill the form with documents', hi: 'दस्तावेज़ों के साथ फ़ॉर्म भरें' },
        description: {
          en: 'Fill all mandatory fields, paste a signed passport-size photograph and attach self-attested copies of the documents.',
          hi: 'सभी ज़रूरी जानकारी भरें, हस्ताक्षर किया हुआ पासपोर्ट फ़ोटो चिपकाएं और दस्तावेज़ों की स्व-सत्यापित प्रतियां लगाएं।',
        },
      },
      {
        step_number: 3,
        title: { en: 'Submit and keep the receipt', hi: 'जमा करें और पावती रखें' },
        description: {
          en: 'Submit the signed form to the designated authority and collect the receipt. Buy only BIS-marked irrigation systems and components.',
          hi: 'हस्ताक्षरित फ़ॉर्म निर्धारित अधिकारी को जमा करें और पावती लें। केवल बीआईएस-चिह्नित सिंचाई उपकरण ही खरीदें।',
        },
      },
    ],
  },
  // NOTE: this scheme's rules are closed (2016-18 sales). Kept in the list as requested; its description says so.
  {
    id: 'mp-krishak-samriddhi',
    code: 'mp-krishak-samriddhi',
    name: {
      en: 'Mukhya Mantri Krishak Samriddhi Yojana (Madhya Pradesh)',
      hi: 'मुख्यमंत्री कृषक समृद्धि योजना (मध्य प्रदेश)',
    },
    short_name: 'Krishak Samriddhi',
    category: 'agriculture',
    level: 'state',
    state_code: 'MP',
    applicable_states: ['MP'],
    featured: false,
    rules_status: 'CLOSED_HISTORICAL', // the sale windows in the rules ended in 2018
    description: {
      en: 'An incentive per quintal for registered MP farmers who sold paddy, wheat, gram, lentil or mustard in the 2016-17 and 2017-18 seasons. The sale windows on the page ended in 2018.',
      hi: 'पंजीकृत मध्य प्रदेश के किसानों को 2016-17 और 2017-18 के सीज़न में धान, गेहूं, चना, मसूर या सरसों बेचने पर प्रति क्विंटल प्रोत्साहन राशि। पेज पर दी गई बिक्री अवधि 2018 में समाप्त हो चुकी है।',
    },
    benefits: {
      en: '₹200 per quintal for paddy (Kharif 2016) and wheat (Rabi 2016-17); ₹265 per quintal for wheat and ₹100 per quintal for gram, lentil and mustard (Rabi 2017-18). Paid by RTGS/NEFT after the District Level Implementation Committee verifies.',
      hi: 'धान (खरीफ 2016) और गेहूं (रबी 2016-17) पर ₹200 प्रति क्विंटल; गेहूं पर ₹265 और चना, मसूर, सरसों पर ₹100 प्रति क्विंटल (रबी 2017-18)। जिला स्तरीय क्रियान्वयन समिति के सत्यापन के बाद RTGS/NEFT से भुगतान।',
    },
    official_source: {
      // No official link found (only third-party sites). Left empty on purpose; the UI hides the button.
      url: '',
      last_checked_date: null, // TODO: set when a teammate verifies whether this scheme is still open
      issuing_ministry: {
        en: 'Farmer Welfare and Agriculture Development Department, Government of Madhya Pradesh',
        hi: 'किसान कल्याण एवं कृषि विकास विभाग, मध्य प्रदेश शासन',
      },
      gazette_or_order_ref: 'Not stated on the myScheme page',
    },
    criteria: [
      {
        id: 'crit-ks-registered-farmer',
        field: 'is_registered_farmer_eupajan',
        operator: 'EQUALS',
        target_value: true,
        criticality: 'MANDATORY',
        explanation_if_met: {
          en: 'You are a farmer registered on the e-Upajan portal.',
          hi: 'आप ई-उपज पोर्टल पर पंजीकृत किसान हैं।',
        },
        explanation_if_violated: {
          en: 'The farmer must be registered on the e-Upajan portal.',
          hi: 'किसान का ई-उपज पोर्टल पर पंजीकृत होना ज़रूरी है।',
        },
      },
      {
        // The sale windows listed on the page all ended in 2018.
        id: 'crit-ks-sold-in-window',
        field: 'sold_eligible_crop_in_listed_window',
        operator: 'EQUALS',
        target_value: true,
        criticality: 'MANDATORY',
        explanation_if_met: {
          en: 'You sold an eligible crop at a mandi or procurement centre in the listed sale period.',
          hi: 'आपने सूचीबद्ध बिक्री अवधि में मंडी या खरीद केंद्र पर पात्र फसल बेची।',
        },
        explanation_if_violated: {
          en: 'Only sales in the listed seasons count, and those periods ended in 2018.',
          hi: 'केवल सूचीबद्ध सीज़न की बिक्री मान्य है, और वे अवधियां 2018 में समाप्त हो चुकी हैं।',
        },
      },
    ],
    required_documents: [
      {
        id: 'doc-ks-aadhaar',
        title: { en: 'Aadhaar Card', hi: 'आधार कार्ड' },
        issuing_authority: { en: 'UIDAI', hi: 'भारतीय विशिष्ट पहचान प्राधिकरण' },
        optional: false,
      },
      {
        id: 'doc-ks-bank',
        title: { en: 'Bank account details', hi: 'बैंक खाते का विवरण' },
        issuing_authority: { en: 'Bank', hi: 'बैंक' },
        optional: false,
      },
      {
        id: 'doc-ks-mandi-slip',
        title: {
          en: 'Mandi entry slip details (slip number, date of sale, commodity number, quantity, payment received)',
          hi: 'मंडी प्रवेश पर्ची का विवरण (पर्ची क्रमांक, बिक्री की तारीख, उपज क्रमांक, मात्रा, प्राप्त भुगतान)',
        },
        issuing_authority: { en: 'Mandi / Procurement centre', hi: 'मंडी / खरीद केंद्र' },
        optional: false,
      },
    ],
    application_steps: [
      {
        step_number: 1,
        title: { en: 'Register on e-Upajan', hi: 'ई-उपज पर पंजीकरण' },
        description: {
          en: 'Register on the e-Upajan portal with Aadhaar, mobile number and bank details before selling.',
          hi: 'बेचने से पहले आधार, मोबाइल नंबर और बैंक विवरण के साथ ई-उपज पोर्टल पर पंजीकरण करें।',
        },
      },
      {
        step_number: 2,
        title: { en: 'Sell at a mandi or procurement centre', hi: 'मंडी या खरीद केंद्र पर बिक्री' },
        description: {
          en: 'Sell the eligible crop in the listed period, then the District Level Implementation Committee verifies the data and the amount is sent to your account.',
          hi: 'सूचीबद्ध अवधि में पात्र फसल बेचें, फिर जिला स्तरीय क्रियान्वयन समिति डेटा का सत्यापन करती है और राशि आपके खाते में भेजी जाती है।',
        },
      },
    ],
  },
  // ---------------------------------------------------------------------------
  // Gujarat: Stipend Scheme for Scheduled Tribes, Poultry Training Stipend
  // Drafted only from the myScheme text. Not yet checked against the official source.
  // The page puts the steps under the wrong headings (the "Online" heading describes visiting an
  // office; the "Offline" heading describes the I-Khedut portal). Both routes are kept below.
  // No income limit is stated, only that income proof is needed, so none is coded.
  // ---------------------------------------------------------------------------
  {
    id: 'gj-st-poultry-training-stipend',
    code: 'gj-st-poultry-training-stipend',
    name: {
      en: 'Stipend Scheme for Scheduled Tribes: Poultry Training Stipend (Gujarat)',
      hi: 'अनुसूचित जनजाति के लिए स्टाइपेंड योजना: पोल्ट्री प्रशिक्षण स्टाइपेंड (गुजरात)',
    },
    short_name: 'Poultry Training Stipend (ST, Gujarat)',
    category: 'agriculture',
    level: 'state',
    state_code: 'GJ',
    applicable_states: ['GJ'],
    featured: false,
    description: {
      en: 'A stipend for adult Scheduled Tribe people of Gujarat who take six days of scientific poultry farming training. Women and people below the poverty line get priority.',
      hi: 'गुजरात के वयस्क अनुसूचित जनजाति के लोगों के लिए, जो छह दिन का वैज्ञानिक मुर्गीपालन प्रशिक्षण लेते हैं, स्टाइपेंड। महिलाओं और गरीबी रेखा से नीचे के लोगों को प्राथमिकता।',
    },
    benefits: {
      en: 'Up to ₹2,000 paid into your bank account for the 6-day training (₹300 a day for 6 days = ₹1,800, plus ₹200 for travel), and a poultry training certificate after the training.',
      hi: '6 दिन के प्रशिक्षण के लिए बैंक खाते में अधिकतम ₹2,000 (₹300 प्रतिदिन × 6 दिन = ₹1,800 और आने-जाने के ₹200), और प्रशिक्षण पूरा होने पर पोल्ट्री प्रशिक्षण प्रमाण पत्र।',
    },
    official_source: {
      // Link taken from the myScheme page (I-Khedut portal application page).
      url: 'https://ikhedut.gujarat.gov.in/iKhedutPublicScheme/Public/frm_Public_ANH2_SchemeApplicaiton.aspx',
      last_checked_date: null, // TODO: set to the day a teammate verifies the rules on the official source
      issuing_ministry: {
        en: 'Department of Agriculture, Farmers Welfare & Co-operation, Government of Gujarat',
        hi: 'कृषि, किसान कल्याण एवं सहकारिता विभाग, गुजरात सरकार',
      },
      gazette_or_order_ref: 'Not stated on the myScheme page',
    },
    criteria: [
      {
        // Source: "only be given to the adult of Schedule Tribes people of the society of Gujarat State"
        id: 'crit-gjp-gujarat-resident',
        field: 'is_gujarat_resident',
        operator: 'EQUALS',
        target_value: true,
        criticality: 'MANDATORY',
        explanation_if_met: {
          en: 'You belong to Gujarat State.',
          hi: 'आप गुजरात राज्य के निवासी हैं।',
        },
        explanation_if_violated: {
          en: 'This scheme is only for people of Gujarat State.',
          hi: 'यह योजना केवल गुजरात राज्य के लोगों के लिए है।',
        },
      },
      {
        id: 'crit-gjp-scheduled-tribe',
        field: 'is_scheduled_tribe',
        operator: 'EQUALS',
        target_value: true,
        criticality: 'MANDATORY',
        explanation_if_met: {
          en: 'You belong to a Scheduled Tribe.',
          hi: 'आप अनुसूचित जनजाति से हैं।',
        },
        explanation_if_violated: {
          en: 'This scheme is only for people of Scheduled Tribes.',
          hi: 'यह योजना केवल अनुसूचित जनजाति के लोगों के लिए है।',
        },
      },
      {
        // Source: "adult"
        id: 'crit-gjp-adult',
        field: 'age',
        operator: 'GREATER_THAN_OR_EQUAL',
        target_value: 18,
        criticality: 'MANDATORY',
        explanation_if_met: {
          en: 'You are an adult (18 or older).',
          hi: 'आप वयस्क (18 वर्ष या अधिक) हैं।',
        },
        explanation_if_violated: {
          en: 'Only adults can get this stipend.',
          hi: 'यह स्टाइपेंड केवल वयस्कों को मिलता है।',
        },
      },
    ],
    required_documents: [
      {
        id: 'doc-gjp-id',
        title: { en: 'Identity proof (Aadhaar Card or Voter ID Card)', hi: 'पहचान प्रमाण (आधार कार्ड या मतदाता पहचान पत्र)' },
        issuing_authority: { en: 'UIDAI / Election Commission', hi: 'यूआईडीएआई / चुनाव आयोग' },
        optional: false,
      },
      {
        id: 'doc-gjp-income',
        title: { en: 'Income proof certificate', hi: 'आय प्रमाण पत्र' },
        issuing_authority: { en: 'Competent authority', hi: 'सक्षम अधिकारी' },
        optional: false,
      },
      {
        id: 'doc-gjp-residence',
        title: { en: 'Residence proof', hi: 'निवास प्रमाण' },
        issuing_authority: { en: 'Government authority', hi: 'सरकारी प्राधिकारी' },
        optional: false,
      },
      {
        id: 'doc-gjp-caste',
        title: { en: 'Caste certificate (Scheduled Tribe)', hi: 'जाति प्रमाण पत्र (अनुसूचित जनजाति)' },
        issuing_authority: { en: 'Competent authority', hi: 'सक्षम अधिकारी' },
        optional: false,
      },
      {
        id: 'doc-gjp-bpl',
        title: { en: 'Below Poverty Line (BPL) card', hi: 'गरीबी रेखा से नीचे (बीपीएल) कार्ड' },
        issuing_authority: { en: 'Competent authority', hi: 'सक्षम अधिकारी' },
        optional: true,
        guidance: { en: 'If you have one. It gives you priority.', hi: 'यदि है तो। इससे प्राथमिकता मिलती है।' },
      },
      {
        id: 'doc-gjp-disability',
        title: { en: 'Disability certificate (only for persons with disabilities)', hi: 'दिव्यांगता प्रमाण पत्र (केवल दिव्यांगजनों के लिए)' },
        issuing_authority: { en: 'Competent authority', hi: 'सक्षम अधिकारी' },
        optional: true,
      },
      {
        id: 'doc-gjp-ration',
        title: { en: 'Barcoded ration card', hi: 'बारकोड वाला राशन कार्ड' },
        issuing_authority: { en: 'Food & Civil Supplies Department', hi: 'खाद्य एवं नागरिक आपूर्ति विभाग' },
        optional: true,
        guidance: { en: 'If applicable.', hi: 'यदि लागू हो।' },
      },
      {
        id: 'doc-gjp-bank',
        title: { en: 'Savings account bank passbook or cancelled cheque', hi: 'बचत खाते की बैंक पासबुक या रद्द किया हुआ चेक' },
        issuing_authority: { en: 'Bank', hi: 'बैंक' },
        optional: true,
        guidance: { en: 'If applicable. The stipend is paid into your bank account.', hi: 'यदि लागू हो। स्टाइपेंड बैंक खाते में आता है।' },
      },
    ],
    application_steps: [
      {
        step_number: 1,
        title: { en: 'Apply on the I-Khedut portal', hi: 'आई-खेडूत पोर्टल पर आवेदन करें' },
        description: {
          en: 'On the I-Khedut portal click "Apply New" and submit the application. Use "Update Application" to correct it. Confirm the application within 7 days of saving it.',
          hi: 'आई-खेडूत पोर्टल पर "Apply New" पर क्लिक करके आवेदन जमा करें। सुधार के लिए "Update Application" का उपयोग करें। आवेदन सेव करने के 7 दिन के भीतर उसे कन्फर्म करें।',
        },
      },
      {
        step_number: 2,
        title: { en: 'Print, sign and submit', hi: 'प्रिंट निकालें, हस्ताक्षर करें और जमा करें' },
        description: {
          en: 'Take a printout of the confirmed application (applying online alone does not count). Sign or put your thumbprint on it and submit it with the documents to the office on the form, or upload the signed scan (PDF, under 200 KB). If documents are wrong or missing, submit the correct ones to the office within 7 days.',
          hi: 'कन्फर्म किए आवेदन का प्रिंट निकालें (केवल ऑनलाइन आवेदन मान्य नहीं है)। उस पर हस्ताक्षर या अंगूठा लगाकर दस्तावेज़ों के साथ फ़ॉर्म पर दिए कार्यालय में जमा करें, या हस्ताक्षरित स्कैन (PDF, 200 KB से कम) अपलोड करें। दस्तावेज़ गलत या अधूरे हों तो सही दस्तावेज़ 7 दिन के भीतर कार्यालय में जमा करें।',
        },
      },
      {
        step_number: 3,
        title: { en: 'Or collect the form from the poultry office', hi: 'या पोल्ट्री कार्यालय से फ़ॉर्म लें' },
        description: {
          en: 'You can also collect the form from the nearest Intensive Poultry Development Project Office or District Poultry Extension Centre, fill it in, attach self-attested documents and submit it. After verification you can get the benefit.',
          hi: 'आप नज़दीकी गहन पोल्ट्री विकास परियोजना कार्यालय या जिला पोल्ट्री विस्तार केंद्र से फ़ॉर्म लेकर भर सकते हैं, स्व-सत्यापित दस्तावेज़ लगाकर जमा करें। सत्यापन के बाद लाभ मिलता है।',
        },
      },
    ],
  },
  // ---------------------------------------------------------------------------
  // PM VIKAS (Pradhan Mantri Virasat Ka Samvardhan), Ministry of Minority Affairs
  // Drafted from the myScheme text. When I opened the official site's "About us" page it confirmed
  // the ministry and structure, but it did NOT show the age limits, the community list or the
  // quotas, and it says the scheme is aligned with the 15th Finance Commission cycle "up to
  // 2025-26". That cycle has ended, so check whether the scheme was extended.
  // Seats are limited (quotas for women, PwD and up to 25% / 15% non-minority EWS candidates), which
  // is not modelled here. Age 18+ applies to the women leadership component only.
  // ---------------------------------------------------------------------------
  {
    id: 'pm-vikas',
    code: 'pm-vikas',
    name: {
      en: 'Pradhan Mantri Virasat Ka Samvardhan (PM VIKAS)',
      hi: 'प्रधानमंत्री विरासत का संवर्धन (पीएम विकास)',
    },
    short_name: 'PM VIKAS',
    category: 'employment',
    level: 'central',
    state_code: 'ALL',
    applicable_states: ['ALL'],
    featured: false,
    description: {
      en: 'Skill training, open-school education for dropouts, and leadership and enterprise support for women from the six notified minority communities (Muslims, Christians, Sikhs, Buddhists, Jains and Parsis).',
      hi: 'छह अधिसूचित अल्पसंख्यक समुदायों (मुस्लिम, ईसाई, सिख, बौद्ध, जैन और पारसी) के लिए कौशल प्रशिक्षण, स्कूल छोड़ चुके लोगों के लिए ओपन स्कूल से शिक्षा, और महिलाओं के लिए नेतृत्व व उद्यमिता सहायता।',
    },
    benefits: {
      en: 'Skill training (traditional and modern), education support to complete Class 8, 10 or 12 through open schooling (NIOS), leadership and entrepreneurship support for women, and a stipend for trainees.',
      hi: 'कौशल प्रशिक्षण (पारंपरिक और आधुनिक), ओपन स्कूल (एनआईओएस) से कक्षा 8, 10 या 12 पूरी करने में सहायता, महिलाओं के लिए नेतृत्व और उद्यमिता सहायता, और प्रशिक्षुओं को स्टाइपेंड।',
    },
    official_source: {
      url: 'https://pmvikas.minorityaffairs.gov.in/',
      last_checked_date: null, // TODO: set to the day a teammate verifies the rules and checks the scheme is still running
      issuing_ministry: {
        en: 'Ministry of Minority Affairs, Government of India',
        hi: 'अल्पसंख्यक कार्य मंत्रालय, भारत सरकार',
      },
      gazette_or_order_ref: 'PM VIKAS Guidelines (pmvikas.minorityaffairs.gov.in)',
    },
    criteria: [
      {
        id: 'crit-pmv-indian-national',
        field: 'is_indian_citizen',
        operator: 'EQUALS',
        target_value: true,
        criticality: 'MANDATORY',
        explanation_if_met: {
          en: 'You are an Indian national.',
          hi: 'आप भारतीय नागरिक हैं।',
        },
        explanation_if_violated: {
          en: 'The scheme is for Indian nationals.',
          hi: 'यह योजना भारतीय नागरिकों के लिए है।',
        },
      },
      {
        // Source: "Indian nationals belonging to the six notified minority communities".
        // Up to 25% (traditional skilling) / 15% (other components) seats may go to non-minority EWS candidates.
        id: 'crit-pmv-minority',
        field: 'belongs_to_notified_minority_community',
        operator: 'EQUALS',
        target_value: true,
        criticality: 'MANDATORY',
        explanation_if_met: {
          en: 'You belong to one of the six notified minority communities.',
          hi: 'आप छह अधिसूचित अल्पसंख्यक समुदायों में से एक से हैं।',
        },
        explanation_if_violated: {
          en: 'The scheme is mainly for the six notified minority communities. A small share of seats can go to non-minority candidates from economically weaker sections, so ask the training centre.',
          hi: 'यह योजना मुख्य रूप से छह अधिसूचित अल्पसंख्यक समुदायों के लिए है। कुछ सीटें आर्थिक रूप से कमज़ोर वर्ग के गैर-अल्पसंख्यक उम्मीदवारों को मिल सकती हैं, इसलिए प्रशिक्षण केंद्र से पूछें।',
        },
      },
      {
        // Source: "14 to 45 years for skilling and education; 18 to 45 for women leadership"
        id: 'crit-pmv-min-age',
        field: 'age',
        operator: 'GREATER_THAN_OR_EQUAL',
        target_value: 14,
        criticality: 'MANDATORY',
        explanation_if_met: {
          en: 'You are at least 14 years old.',
          hi: 'आपकी आयु कम से कम 14 वर्ष है।',
        },
        explanation_if_violated: {
          en: 'You must be at least 14 years old (18 for the women leadership and entrepreneurship component).',
          hi: 'आपकी आयु कम से कम 14 वर्ष होनी चाहिए (महिला नेतृत्व और उद्यमिता के लिए 18 वर्ष)।',
        },
      },
      {
        id: 'crit-pmv-max-age',
        field: 'age',
        operator: 'LESS_THAN_OR_EQUAL',
        target_value: 45,
        criticality: 'MANDATORY',
        explanation_if_met: {
          en: 'You are 45 years old or younger.',
          hi: 'आपकी आयु 45 वर्ष या उससे कम है।',
        },
        explanation_if_violated: {
          en: 'The upper age limit is 45 years.',
          hi: 'अधिकतम आयु सीमा 45 वर्ष है।',
        },
      },
    ],
    required_documents: [
      {
        id: 'doc-pmv-aadhaar-bank',
        title: { en: 'Aadhaar card and Aadhaar-linked bank account', hi: 'आधार कार्ड और आधार से जुड़ा बैंक खाता' },
        issuing_authority: { en: 'UIDAI / Bank', hi: 'यूआईडीएआई / बैंक' },
        optional: false,
      },
      {
        id: 'doc-pmv-ews',
        title: { en: 'EWS certificate (for non-minority candidates only)', hi: 'ईडब्ल्यूएस प्रमाण पत्र (केवल गैर-अल्पसंख्यक उम्मीदवारों के लिए)' },
        issuing_authority: { en: 'Competent authority', hi: 'सक्षम अधिकारी' },
        optional: true,
      },
      {
        id: 'doc-pmv-qualification',
        title: { en: 'Educational qualification for the training programme you apply to', hi: 'जिस प्रशिक्षण में आवेदन कर रहे हैं उसके अनुसार शैक्षणिक योग्यता' },
        issuing_authority: { en: 'School / Board / Institute', hi: 'स्कूल / बोर्ड / संस्थान' },
        optional: false,
      },
    ],
    application_steps: [
      {
        step_number: 1,
        title: { en: 'Register on the SIDH portal', hi: 'एसआईडीएच पोर्टल पर पंजीकरण करें' },
        description: {
          en: 'Go to the Skill India Digital Hub (skillindiadigital.gov.in), register as a learner, or log in, and complete e-KYC.',
          hi: 'स्किल इंडिया डिजिटल हब (skillindiadigital.gov.in) पर जाएं, शिक्षार्थी के रूप में पंजीकरण करें या लॉगिन करें और ई-केवाईसी पूरा करें।',
        },
      },
      {
        step_number: 2,
        title: { en: 'Set up your profile', hi: 'अपनी प्रोफ़ाइल बनाएं' },
        description: {
          en: 'Create a password or PIN, verify your mobile number with an OTP, and check that your name, date of birth and contact details are correct.',
          hi: 'पासवर्ड या पिन बनाएं, ओटीपी से मोबाइल नंबर सत्यापित करें और जांचें कि नाम, जन्म तिथि और संपर्क विवरण सही हैं।',
        },
      },
      {
        step_number: 3,
        title: { en: 'Find PM VIKAS courses', hi: 'पीएम विकास के पाठ्यक्रम खोजें' },
        description: {
          en: 'On your dashboard search for PM VIKAS and job roles, using the filters for scheme, mode and sector.',
          hi: 'डैशबोर्ड पर पीएम विकास और जॉब रोल खोजें, योजना, मोड और सेक्टर के फ़िल्टर का उपयोग करें।',
        },
      },
      {
        step_number: 4,
        title: { en: 'Apply for a batch', hi: 'बैच के लिए आवेदन करें' },
        description: {
          en: 'Choose a batch for your job role and apply. You can pick up to 5 batches, which the training partner or centre reviews.',
          hi: 'अपने जॉब रोल का बैच चुनकर आवेदन करें। आप अधिकतम 5 बैच चुन सकते हैं, जिनकी समीक्षा प्रशिक्षण भागीदार या केंद्र करता है।',
        },
      },
      {
        step_number: 5,
        title: { en: 'Confirm your enrolment', hi: 'नामांकन की पुष्टि करें' },
        description: {
          en: 'After approval, accept the invitation on the portal to confirm your enrolment and track the status under "Applications".',
          hi: 'मंज़ूरी के बाद पोर्टल पर निमंत्रण स्वीकार कर नामांकन पक्का करें और "Applications" में स्थिति देखें।',
        },
      },
    ],
  },
];