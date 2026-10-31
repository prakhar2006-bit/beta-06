// TEMPORARY MOCK. Delete at engine integration. Frontend must not contain eligibility rules.

/**
 * Mock Screening Results for UI Demonstration
 * Follows contracts/eligibility-result.schema.json
 * Outcomes:
 * 1. POTENTIALLY_ELIGIBLE
 * 2. NOT_ELIGIBLE_UNDER_SCREENED_RULES
 * 3. NEEDS_VERIFICATION
 */

export const MOCK_RESULTS = {
  timestamp: new Date().toISOString(),
  schemes_evaluated: 5,
  summary_counts: {
    potentially_eligible: 2,
    needs_verification: 2,
    not_eligible: 1,
  },
  results: [
    {
      scheme_id: 'pm-kisan',
      scheme_name: {
        en: 'PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)',
        hi: 'प्रधानमंत्री किसान सम्मान निधि (पीएम-किसान)',
      },
      category: 'agriculture',
      level: 'central',
      status: 'POTENTIALLY_ELIGIBLE',
      confidence_score: 0.95,
      explanation: {
        en: 'You stated that your family owns cultivable agricultural land and no household member filed income tax. Under standard criteria, you appear eligible for ₹6,000 yearly income support.',
        hi: 'आपने बताया कि आपके परिवार के पास कृषि भूमि दर्ज है और परिवार में कोई आयकर नहीं भरता। नियमों के अनुसार आप ₹6,000 वार्षिक सहायता हेतु संभावित पात्र प्रतीत होते हैं।',
      },
      missing_information: null,
      official_source: {
        url: 'https://pmkisan.gov.in',
        last_checked_date: '2026-02-15',
        issuing_ministry: {
          en: 'Ministry of Agriculture & Farmers Welfare',
          hi: 'कृषि एवं किसान कल्याण मंत्रालय',
        },
      },
      required_documents: [
        {
          id: 'doc-aadhaar',
          title: { en: 'Aadhaar Card (Mobile Linked)', hi: 'आधार कार्ड (मोबाइल लिंक)' },
          issuing_authority: { en: 'UIDAI', hi: 'भारतीय विशिष्ट पहचान प्राधिकरण' },
          guidance: { en: 'Required for e-KYC biometric or OTP verification.', hi: 'ई-केवाईसी बायोमेट्रिक या ओटीपी सत्यापन हेतु आवश्यक।' },
        },
        {
          id: 'doc-land',
          title: { en: 'Land Ownership Record (Khatauni / Khasra)', hi: 'भू-अभिलेख (खतौनी / खसरा)' },
          issuing_authority: { en: 'Tehsil / Bhulekh Portal', hi: 'तहसील / राज्य भूलेख पोर्टल' },
          guidance: { en: 'Must be updated in the computerized land database.', hi: 'सरकारी रिकॉर्ड में नाम दर्ज होना चाहिए।' },
        },
        {
          id: 'doc-bank',
          title: { en: 'Aadhaar-Seeded Bank Passbook', hi: 'आधार-सीडेड बैंक पासबुक' },
          issuing_authority: { en: 'Bank / Post Office', hi: 'बैंक या डाकघर बैंक' },
          guidance: { en: 'DBT enabled for installment transfer.', hi: 'किस्त पाने हेतु आधार मैपिंग अनिवार्य।' },
        },
      ],
    },
    {
      scheme_id: 'pmay-g',
      scheme_name: {
        en: 'Pradhan Mantri Awaas Yojana - Gramin (PMAY-G)',
        hi: 'प्रधानमंत्री आवास योजना - ग्रामीण (पीएमएवाई-जी)',
      },
      category: 'housing',
      level: 'central',
      status: 'POTENTIALLY_ELIGIBLE',
      confidence_score: 0.9,
      explanation: {
        en: 'You reported living in a rural kutcha house with no four-wheeler vehicle ownership. You satisfy primary socio-economic housing deprivation norms.',
        hi: 'आपने बताया कि आप ग्रामीण क्षेत्र में कच्चे मकान में रहते हैं और कोई चार पहिया वाहन नहीं है। आप आवास सहायता के प्राथमिक मानकों को पूरा करते हैं।',
      },
      missing_information: null,
      official_source: {
        url: 'https://pmayg.nic.in',
        last_checked_date: '2026-02-10',
        issuing_ministry: {
          en: 'Ministry of Rural Development',
          hi: 'ग्रामीण विकास मंत्रालय',
        },
      },
      required_documents: [
        {
          id: 'doc-aadhaar-family',
          title: { en: 'Family Members Aadhaar Cards', hi: 'परिवार के सभी सदस्यों के आधार कार्ड' },
          issuing_authority: { en: 'UIDAI', hi: 'भारतीय विशिष्ट पहचान प्राधिकरण' },
          guidance: { en: 'Required for Awaas+ waitlist confirmation.', hi: 'आवास+ प्रतीक्षा सूची में नाम मिलान हेतु।' },
        },
        {
          id: 'doc-bank-pmay',
          title: { en: 'Bank Account Passbook (DBT Active)', hi: 'बैंक पासबुक (डीबीटी सक्रिय)' },
          issuing_authority: { en: 'Bank', hi: 'बैंक' },
          guidance: { en: '3 installments transferred in stages directly.', hi: '3 किस्तों में निर्माण राशि इसी खाते में आएगी।' },
        },
      ],
    },
    {
      scheme_id: 'ladli-behna-mp',
      scheme_name: {
        en: 'Mukhyamantri Ladli Behna Yojana (Madhya Pradesh)',
        hi: 'मुख्यमंत्री लाड़ली बहना योजना (मध्य प्रदेश)',
      },
      category: 'women-child',
      level: 'state',
      status: 'NEEDS_VERIFICATION',
      confidence_score: 0.65,
      explanation: {
        en: 'You appear within the age bracket and resident profile, but family income certificate and Samagra e-KYC status must be verified by the local Gram Panchayat or Ward in MP.',
        hi: 'आप आयु सीमा एवं निवास के अनुसार पात्र हो सकती हैं, किंतु वार्षिक आय ₹2.5 लाख से कम होने का प्रमाण और समग्र ई-केवाईसी सत्यापन ग्राम पंचायत/वार्ड द्वारा आवश्यक है।',
      },
      missing_information: {
        en: 'Samagra Family ID e-KYC linkage status and MP Domicile Certificate verification required.',
        hi: 'समग्र परिवार आईडी में आधार ई-केवाईसी की स्थिति एवं मध्य प्रदेश मूल निवास प्रमाण की पुष्टि आवश्यक है।',
      },
      official_source: {
        url: 'https://cmladlibehna.mp.gov.in',
        last_checked_date: '2026-02-18',
        issuing_ministry: {
          en: 'Women & Child Development Dept, Govt of MP',
          hi: 'महिला एवं बाल विकास विभाग, म.प्र. शासन',
        },
      },
      required_documents: [
        {
          id: 'doc-samagra',
          title: { en: 'Samagra Family & Member ID (e-KYC verified)', hi: 'समग्र परिवार एवं सदस्य आईडी (ई-केवाईसी पूर्ण)' },
          issuing_authority: { en: 'Samagra Mission MP', hi: 'समग्र सामाजिक सुरक्षा मिशन, म.प्र.' },
          guidance: { en: 'Must be verified at samagra.gov.in.', hi: 'समग्र पोर्टल पर आधार लिंक होना अनिवार्य।' },
        },
        {
          id: 'doc-bank-ind',
          title: { en: 'Individual Bank Account (Aadhaar Seeded)', hi: 'महिला का व्यक्तिगत बैंक खाता (डीबीटी सक्षम)' },
          issuing_authority: { en: 'Bank', hi: 'बैंक' },
          guidance: { en: 'Joint accounts are not accepted.', hi: 'संयुक्त खाता मान्य नहीं होगा।' },
        },
      ],
    },
    {
      scheme_id: 'pm-vishwakarma',
      scheme_name: {
        en: 'PM Vishwakarma Scheme',
        hi: 'पीएम विश्वकर्मा योजना',
      },
      category: 'business',
      level: 'central',
      status: 'NEEDS_VERIFICATION',
      confidence_score: 0.6,
      explanation: {
        en: 'To qualify for ₹15,000 toolkit and 5% credit, your engagement in one of the 18 traditional crafts must be endorsed by the Gram Panchayat or Urban Local Body.',
        hi: '₹15,000 टूलकिट अनुदान एवं रियायती ऋण पाने हेतु 18 पारंपरिक शिल्पों में संलग्नता का सत्यापन ग्राम पंचायत अथवा नगर निकाय द्वारा किया जाना आवश्यक है।',
      },
      missing_information: {
        en: 'Trade verification stage 1 (Gram Panchayat or Municipal Executive confirmation).',
        hi: 'पारंपरिक व्यवसाय का प्रथम स्तरीय सत्यापन (ग्राम प्रधान या नगर निगम अधिकारी द्वारा)।',
      },
      official_source: {
        url: 'https://pmvishwakarma.gov.in',
        last_checked_date: '2026-02-01',
        issuing_ministry: {
          en: 'Ministry of MSME',
          hi: 'सूक्ष्म, लघु एवं मध्यम उद्यम मंत्रालय',
        },
      },
      required_documents: [
        {
          id: 'doc-aadhaar-vk',
          title: { en: 'Aadhaar Card (Biometric)', hi: 'आधार कार्ड (बायोमेट्रिक प्रमाणीकरण)' },
          issuing_authority: { en: 'UIDAI', hi: 'भारतीय विशिष्ट पहचान प्राधिकरण' },
          guidance: { en: 'Fingerprint / iris scan at CSC.', hi: 'सीएससी केंद्र पर बायोमेट्रिक पुष्टि हेतु।' },
        },
      ],
    },
    {
      scheme_id: 'pm-ujjwala',
      scheme_name: {
        en: 'Pradhan Mantri Ujjwala Yojana (PMUY 2.0)',
        hi: 'प्रधानमंत्री उज्ज्वला योजना (पीएमयूवाई 2.0)',
      },
      category: 'women-child',
      level: 'central',
      status: 'NOT_ELIGIBLE_UNDER_SCREENED_RULES',
      confidence_score: 1.0,
      explanation: {
        en: 'Your responses indicate that your household already possesses an active domestic LPG cylinder connection. Ujjwala 2.0 grants free connections only to households without any existing LPG connection.',
        hi: 'आपके उत्तर के अनुसार आपके परिवार में पहले से रसोई गैस (एलपीजी) कनेक्शन उपलब्ध है। उज्ज्वला योजना केवल उन गरीब परिवारों को मुफ्त कनेक्शन देती है जिनके पास पहले से गैस कनेक्शन नहीं है।',
      },
      missing_information: null,
      official_source: {
        url: 'https://pmuy.gov.in',
        last_checked_date: '2026-01-20',
        issuing_ministry: {
          en: 'Ministry of Petroleum & Natural Gas',
          hi: 'पेट्रोलियम एवं प्राकृतिक गैस मंत्रालय',
        },
      },
      required_documents: [],
    },
  ],
};

