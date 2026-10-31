// TEMPORARY MOCK. Delete at engine integration. Frontend must not contain eligibility rules.

/**
 * Mock Questionnaire for YojanaMitra Screening
 * Conforms to input types: TEXT, NUMBER, DATE, BOOLEAN, SINGLE_SELECT, MULTI_SELECT
 * Ready for future FastAPI backend integration (sessionApi / questions/next)
 */

export const MOCK_QUESTIONS = [
  {
    id: 'q_state',
    type: 'SINGLE_SELECT',
    required: true,
    title: {
      en: 'Which State or Union Territory do you permanently reside in?',
      hi: 'आप स्थायी रूप से किस राज्य या केंद्र शासित प्रदेश में निवास करते हैं?',
    },
    help_text: {
      en: 'This helps us find state-specific schemes alongside national Central Government programs.',
      hi: 'यह आपके राज्य की विशेष योजनाओं और राष्ट्रीय केंद्रीय योजनाओं को खोजने में मदद करता है।',
    },
    options: [
      { value: 'MP', label: { en: 'Madhya Pradesh', hi: 'मध्य प्रदेश' } },
      { value: 'UP', label: { en: 'Uttar Pradesh', hi: 'उत्तर प्रदेश' } },
      { value: 'BR', label: { en: 'Bihar', hi: 'बिहार' } },
      { value: 'RJ', label: { en: 'Rajasthan', hi: 'राजस्थान' } },
      { value: 'MH', label: { en: 'Maharashtra', hi: 'महाराष्ट्र' } },
      { value: 'DL', label: { en: 'Delhi (NCT)', hi: 'दिल्ली (राष्ट्रीय राजधानी क्षेत्र)' } },
      { value: 'OTHER', label: { en: 'Other State / Union Territory', hi: 'अन्य राज्य / केंद्र शासित प्रदेश' } },
    ],
  },
  {
    id: 'q_area_type',
    type: 'SINGLE_SELECT',
    required: true,
    title: {
      en: 'What type of area do you live in?',
      hi: 'आप किस प्रकार के क्षेत्र में रहते हैं?',
    },
    help_text: {
      en: 'Many housing and rural livelihood schemes are targeted specifically to villages.',
      hi: 'कई योजनाएं जैसे ग्रामीण आवास विशेष रूप से ग्रामीण क्षेत्रों के लिए होती हैं।',
    },
    options: [
      { value: 'rural', label: { en: 'Rural (Village / Gram Panchayat)', hi: 'ग्रामीण (गाँव / ग्राम पंचायत)' } },
      { value: 'urban', label: { en: 'Urban (City / Municipality / Town)', hi: 'शहरी (शहर / नगर पालिका / नगर निगम)' } },
    ],
  },
  {
    id: 'q_age',
    type: 'NUMBER',
    required: true,
    title: {
      en: 'What is your current age (in completed years)?',
      hi: 'आपकी वर्तमान आयु (पूर्ण वर्षों में) कितनी है?',
    },
    help_text: {
      en: 'Age determines eligibility for youth, scholarship, adult, and senior citizen pensions.',
      hi: 'आयु से युवा, छात्रवृत्ति, वयस्क एवं वृद्धावस्था योजनाओं की पात्रता निर्धारित होती है।',
    },
    min: 1,
    max: 120,
    placeholder: {
      en: 'e.g. 32',
      hi: 'उदा. 32',
    },
  },
  {
    id: 'q_gender',
    type: 'SINGLE_SELECT',
    required: true,
    title: {
      en: 'What is your gender?',
      hi: 'आपका लिंग क्या है?',
    },
    help_text: {
      en: 'Several high-impact welfare programs specifically empower women and girl children.',
      hi: 'कई विशेष योजनाएं जैसे लाड़ली बहना और उज्ज्वला विशेष रूप से महिलाओं के लिए हैं।',
    },
    options: [
      { value: 'female', label: { en: 'Female', hi: 'महिला' } },
      { value: 'male', label: { en: 'Male', hi: 'पुरुष' } },
      { value: 'transgender', label: { en: 'Transgender / Other', hi: 'तृतीय लिंग (किन्नर) / अन्य' } },
    ],
  },
  {
    id: 'q_occupation',
    type: 'SINGLE_SELECT',
    required: true,
    title: {
      en: 'What is your primary occupation or source of livelihood?',
      hi: 'आपका मुख्य व्यवसाय अथवा आजीविका का साधन क्या है?',
    },
    help_text: {
      en: 'Select the option that best represents how you or your family earn a living.',
      hi: 'वह विकल्प चुनें जो आपके परिवार की मुख्य कमाई का प्रतिनिधित्व करता हो।',
    },
    options: [
      { value: 'farmer', label: { en: 'Farmer / Cultivator (खेती/किसान)', hi: 'किसान / काश्तकार' } },
      { value: 'artisan', label: { en: 'Traditional Artisan / Craftsperson (बढ़ई, लोहार, दर्जी, कुम्हार आदि)', hi: 'पारंपरिक कारीगर / शिल्पकार' } },
      { value: 'street_vendor', label: { en: 'Street Vendor / Hawker (ठेला/रेहड़ी-पटरी)', hi: 'रेहड़ी-पटरी / ठेला विक्रेता' } },
      { value: 'daily_wage', label: { en: 'Daily Wage Laborer / Construction Worker (मजदूर)', hi: 'दिहाड़ी मजदूर / निर्माण श्रमिक' } },
      { value: 'student', label: { en: 'Student (छात्र/छात्रा)', hi: 'विद्यार्थी / छात्र-छात्रा' } },
      { value: 'homemaker', label: { en: 'Homemaker / Housewife (गृहणी)', hi: 'गृहणी' } },
      { value: 'salaried_business', label: { en: 'Private Employee / Small Shopkeeper', hi: 'निजी कर्मचारी / छोटा दुकानदार' } },
      { value: 'unemployed', label: { en: 'Unemployed / Job Seeker', hi: 'बेरोज़गार / रोज़गार की तलाश में' } },
    ],
  },
  {
    id: 'q_family_income',
    type: 'NUMBER',
    required: true,
    title: {
      en: 'What is your total estimated annual household income (in ₹ INR)?',
      hi: 'आपके पूरे परिवार की कुल अनुमानित वार्षिक आय (रुपये में) कितनी है?',
    },
    help_text: {
      en: 'Total yearly earnings of all earning family members combined. Approximate estimate is sufficient.',
      hi: 'परिवार के सभी कमाने वाले सदस्यों की साल भर की कुल आय। लगभग अनुमान भी पर्याप्त है।',
    },
    min: 0,
    max: 10000000,
    placeholder: {
      en: 'e.g. 120000 (1.2 Lakh)',
      hi: 'उदा. 120000 (1.2 लाख)',
    },
  },
  {
    id: 'q_owns_land',
    type: 'BOOLEAN',
    required: true,
    title: {
      en: 'Does your family own cultivable agricultural land registered in land records?',
      hi: 'क्या आपके परिवार के नाम पर सरकारी राजस्व रिकॉर्ड में खेती योग्य कृषि भूमि दर्ज है?',
    },
    help_text: {
      en: 'Important for PM-KISAN, crop insurance, and farmer assistance schemes.',
      hi: 'पीएम-किसान एवं फसल सहायता योजनाओं की पात्रता के लिए महत्वपूर्ण।',
    },
  },
  {
    id: 'q_housing_type',
    type: 'SINGLE_SELECT',
    required: true,
    title: {
      en: 'What type of home does your family currently live in?',
      hi: 'वर्तमान में आपका परिवार किस प्रकार के घर में रहता है?',
    },
    help_text: {
      en: 'Pucca: concrete/brick roof. Kutcha: mud, thatch, tin, or bamboo shelter.',
      hi: 'पक्का: ईंट-सीमेंट की पक्की छत। कच्चा: मिट्टी, घास-फूस, टीन या खपरैल का मकान।',
    },
    options: [
      { value: 'kutcha', label: { en: 'Kutcha House (कच्चा मकान / मिट्टी या टीन की छत)', hi: 'कच्चा मकान (मिट्टी, बांस या टीन की छत)' } },
      { value: 'pucca', label: { en: 'Pucca House (पक्का मकान / पक्की कंक्रीट छत)', hi: 'पक्का मकान (कंक्रीट या ईंट की पक्की छत)' } },
      { value: 'homeless_rented', label: { en: 'Homeless / Rented / Temporary Shanty', hi: 'बेघर / किराए का कमरा / अस्थायी झुग्गी' } },
    ],
  },
  {
    id: 'q_household_attributes',
    type: 'MULTI_SELECT',
    required: false,
    title: {
      en: 'Select all conditions that currently apply to your household:',
      hi: 'आपके परिवार पर लागू होने वाली सभी उपयुक्त स्थितियों को चुनें:',
    },
    help_text: {
      en: 'Select as many as apply to help identify targeted sub-schemes.',
      hi: 'जितने विकल्प आप पर लागू हों, उन सभी पर सही का निशान लगाएं।',
    },
    options: [
      { value: 'has_bpl_card', label: { en: 'Hold a valid BPL / Antyodaya Ration Card', hi: 'बीपीएल अथवा गुलाबी/पीला अंत्योदय राशन कार्ड है' } },
      { value: 'has_existing_lpg', label: { en: 'Already have an active LPG Gas cylinder connection at home', hi: 'घर में पहले से रसोई गैस (एलपीजी) कनेक्शन उपलब्ध है' } },
      { value: 'has_disability', label: { en: 'Any family member with 40%+ benchmark disability certificate', hi: 'परिवार में 40% या अधिक दिव्यांगता प्रमाण पत्र धारक सदस्य हैं' } },
      { value: 'pays_income_tax', label: { en: 'Any household member filed or paid income tax last year', hi: 'परिवार में किसी सदस्य ने पिछले वर्ष आयकर (Income Tax) भरा है' } },
      { value: 'owns_car_tractor', label: { en: 'Owns a 4-wheeler motor vehicle or tractor', hi: 'चार पहिया मोटर गाड़ी या ट्रैक्टर का स्वामित्व है' } },
    ],
  },
  {
    id: 'q_pincode',
    type: 'TEXT',
    required: false,
    title: {
      en: 'What is your 6-digit Area PIN Code? (Optional)',
      hi: 'आपका 6 अंकों का पिन कोड (PIN Code) क्या है? (वैकल्पिक)',
    },
    help_text: {
      en: 'Used solely to locate the nearest Common Service Centre (CSC) and Gram Panchayat office.',
      hi: 'केवल निकटतम जन सेवा केंद्र (CSC) एवं पंचायत कार्यालय की पहचान के लिए।',
    },
    placeholder: {
      en: 'e.g. 462001',
      hi: 'उदा. 462001',
    },
  },
];

