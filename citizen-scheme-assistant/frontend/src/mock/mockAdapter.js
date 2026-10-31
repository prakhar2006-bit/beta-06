// TEMPORARY MOCK. Delete at engine integration. Frontend must not contain eligibility rules.

import { MOCK_QUESTIONS } from './mockQuestions.js';
import { MOCK_RESULTS } from './mockResults.js';
import { MOCK_SCHEMES } from './mockSchemes.js';

export const mockAdapter = {
  createSession(language = 'hi') {
    const mockSessionId = 'sess_' + Math.random().toString(36).substring(2, 9);
    sessionStorage.setItem('yojanamitra_session_id', mockSessionId);
    sessionStorage.setItem('yojanamitra_answers', JSON.stringify({}));
    return Promise.resolve({ session_id: mockSessionId, is_mock: true });
  },

  getNextQuestion(sessionId, currentQuestionIndex = 0) {
    if (currentQuestionIndex < MOCK_QUESTIONS.length) {
      return Promise.resolve({
        question: MOCK_QUESTIONS[currentQuestionIndex],
        current_index: currentQuestionIndex,
        total_questions: MOCK_QUESTIONS.length,
        has_more: currentQuestionIndex < MOCK_QUESTIONS.length - 1,
      });
    }
    return Promise.resolve({ question: null, has_more: false });
  },

  submitAnswer(sessionId, questionId, answerValue) {
    return Promise.resolve({ success: true, is_mock: true });
  },

  evaluateSession(sessionId) {
    return Promise.resolve({ success: true, evaluated: true, is_mock: true });
  },

  getResults(sessionId) {
    const saved = sessionStorage.getItem('yojanamitra_answers');
    const answers = saved ? JSON.parse(saved) : {};

    const evaluatedResults = MOCK_RESULTS.results.map((baseScheme) => {
      const item = JSON.parse(JSON.stringify(baseScheme));

      if (item.scheme_id === 'pm-kisan') {
        const isTaxpayer = answers.q_household_attributes?.includes('pays_income_tax');
        const ownsLand = answers.q_owns_land === true;

        if (answers.q_owns_land === false) {
          item.status = 'NOT_ELIGIBLE_UNDER_SCREENED_RULES';
          item.confidence_score = 1.0;
          item.explanation = {
            en: 'You stated that your family does not own cultivable agricultural land. Ownership of agricultural land is mandatory for PM-KISAN.',
            hi: 'आपने बताया कि आपके परिवार के पास कृषि भूमि नहीं है। पीएम-किसान योजना के लिए कृषि भूमि का स्वामित्व अनिवार्य है.',
          };
        } else if (isTaxpayer) {
          item.status = 'NOT_ELIGIBLE_UNDER_SCREENED_RULES';
          item.confidence_score = 1.0;
          item.explanation = {
            en: 'Income tax-paying families and institutional landholders are excluded from PM-KISAN benefits.',
            hi: 'आयकर भरने वाले परिवार और संस्थागत भूमिधारक पीएम-किसान योजना के दायरे से बाहर हैं।',
          };
        } else if (ownsLand || answers.q_occupation === 'farmer') {
          item.status = 'POTENTIALLY_ELIGIBLE';
          item.confidence_score = 0.95;
        }
      }

      if (item.scheme_id === 'pmay-g') {
        const isUrban = answers.q_area_type === 'urban';
        const hasVehicle = answers.q_household_attributes?.includes('owns_car_tractor');
        const isPucca = answers.q_housing_type === 'pucca';

        if (isUrban) {
          item.status = 'NOT_ELIGIBLE_UNDER_SCREENED_RULES';
          item.confidence_score = 1.0;
          item.explanation = {
            en: 'PMAY-G is strictly targeted for rural village areas. For municipal/city zones, please check PMAY-Urban.',
            hi: 'पीएमएवाई-जी विशेष रूप से ग्रामीण क्षेत्रों के लिए है। शहरी क्षेत्रों हेतु कृपया पीएमएवाई-शहरी देखें।',
          };
        } else if (hasVehicle || isPucca) {
          item.status = 'NOT_ELIGIBLE_UNDER_SCREENED_RULES';
          item.confidence_score = 0.95;
          item.explanation = {
            en: 'Households living in pucca houses or owning a four-wheeler vehicle do not satisfy primary deprivation criteria for PMAY-G.',
            hi: 'पक्के मकान में रहने वाले अथवा चार पहिया वाहन धारक परिवार पीएमएवाई-जी के प्राथमिक पात्रता मानकों में नहीं आते।',
          };
        } else if (
          answers.q_area_type === 'rural' &&
          (answers.q_housing_type === 'kutcha' || answers.q_housing_type === 'homeless_rented')
        ) {
          item.status = 'POTENTIALLY_ELIGIBLE';
          item.confidence_score = 0.9;
        }
      }

      if (item.scheme_id === 'ladli-behna-mp') {
        const isMale = answers.q_gender === 'male';
        const isOutsideMP =
          answers.q_state && answers.q_state !== 'MP' && answers.q_state !== 'OTHER';
        const highIncome =
          answers.q_family_income && Number(answers.q_family_income) > 250000;
        const isTaxpayer = answers.q_household_attributes?.includes('pays_income_tax');

        if (isMale) {
          item.status = 'NOT_ELIGIBLE_UNDER_SCREENED_RULES';
          item.confidence_score = 1.0;
          item.explanation = {
            en: 'Mukhyamantri Ladli Behna Yojana is exclusively for women. Male applicants are not eligible.',
            hi: 'मुख्यमंत्री लाड़ली बहना योजना केवल महिला आवेदकों के लिए है। पुरुष आवेदक इसके लिए अपात्र हैं।',
          };
        } else if (isOutsideMP) {
          item.status = 'NOT_ELIGIBLE_UNDER_SCREENED_RULES';
          item.confidence_score = 1.0;
          item.explanation = {
            en: 'This scheme is strictly for permanent residents of Madhya Pradesh.',
            hi: 'यह योजना केवल मध्य प्रदेश के स्थायी निवासियों के लिए है।',
          };
        } else if (highIncome || isTaxpayer) {
          item.status = 'NOT_ELIGIBLE_UNDER_SCREENED_RULES';
          item.confidence_score = 0.95;
          item.explanation = {
            en: 'Households with annual income exceeding ₹2.5 Lakhs or paying income tax are excluded from Ladli Behna.',
            hi: '₹2.5 लाख से अधिक वार्षिक आय अथवा आयकरदाता परिवार लाड़ली बहना योजना से बाहर हैं।',
          };
        } else if (answers.q_gender === 'female') {
          item.status = 'NEEDS_VERIFICATION';
          item.confidence_score = 0.65;
        }
      }

      if (item.scheme_id === 'pm-vishwakarma') {
        if (answers.q_occupation === 'artisan') {
          item.status = 'POTENTIALLY_ELIGIBLE';
          item.confidence_score = 0.9;
          item.explanation = {
            en: 'As a traditional artisan or craftsperson, you appear eligible for ₹15,000 toolkit support and 5% collateral-free credit.',
            hi: 'पारंपरिक कारीगर / शिल्पकार होने के नाते आप ₹15,000 टूलकिट अनुदान एवं रियायती ऋण पाने हेतु पात्र प्रतीत होते हैं।',
          };
        } else {
          item.status = 'NEEDS_VERIFICATION';
          item.confidence_score = 0.55;
        }
      }

      if (item.scheme_id === 'pm-ujjwala') {
        const isMale = answers.q_gender === 'male';
        const hasLpg = answers.q_household_attributes?.includes('has_existing_lpg');

        if (isMale) {
          item.status = 'NOT_ELIGIBLE_UNDER_SCREENED_RULES';
          item.confidence_score = 1.0;
          item.explanation = {
            en: 'Ujjwala 2.0 connections are released exclusively in the name of an adult woman of the household.',
            hi: 'उज्ज्वला 2.0 गैस कनेक्शन केवल परिवार की वयस्क महिला के नाम पर जारी किया जाता है।',
          };
        } else if (hasLpg) {
          item.status = 'NOT_ELIGIBLE_UNDER_SCREENED_RULES';
          item.confidence_score = 1.0;
          item.explanation = {
            en: 'Your responses indicate an existing active LPG cylinder connection. Ujjwala 2.0 provides connections only to households without any LPG connection.',
            hi: 'आपके घर में पहले से रसोई गैस कनेक्शन उपलब्ध है। उज्ज्वला योजना केवल बिना गैस कनेक्शन वाले परिवारों के लिए है।',
          };
        } else if (
          answers.q_gender === 'female' &&
          (answers.q_household_attributes?.includes('has_bpl_card') ||
            (answers.q_family_income && Number(answers.q_family_income) <= 200000))
        ) {
          item.status = 'POTENTIALLY_ELIGIBLE';
          item.confidence_score = 0.9;
          item.explanation = {
            en: 'As an eligible female applicant from a low-income household without an active LPG connection, you qualify for a deposit-free gas connection.',
            hi: 'बिना गैस कनेक्शन वाले निम्न आय परिवार की महिला होने के नाते आप मुफ्त गैस कनेक्शन पाने हेतु पात्र हैं।',
          };
        }
      }

      if (item.explanation && !item.decisive_rule) {
        item.decisive_rule = item.explanation;
      }

      return item;
    });

    const eligible = evaluatedResults.filter((r) => r.status === 'POTENTIALLY_ELIGIBLE' || r.status === 'ELIGIBLE').length;
    const needsVerification = evaluatedResults.filter((r) => r.status === 'NEEDS_VERIFICATION' || r.status === 'UNCERTAIN' || r.status === 'MAYBE').length;
    const notEligible = evaluatedResults.filter(
      (r) => r.status === 'NOT_ELIGIBLE_UNDER_SCREENED_RULES' || r.status === 'INELIGIBLE' || r.status === 'NOT_ELIGIBLE'
    ).length;
    const noRules = evaluatedResults.filter((r) => r.status === 'NO_CURRENT_RULES').length;

    return Promise.resolve({
      timestamp: new Date().toISOString(),
      schemes_evaluated: evaluatedResults.length,
      summary_counts: {
        potentially_eligible: eligible,
        needs_verification: needsVerification,
        not_eligible: notEligible,
        no_current_rules: noRules,
      },
      results: evaluatedResults,
      is_mock: true,
    });
  },

  getSchemes(params = {}) {
    let filtered = [...MOCK_SCHEMES];

    if (params.search) {
      const s = (params.search || '').toLowerCase().trim();
      if (s.length > 0) {
        filtered = filtered.filter(
          (sch) =>
            sch.name?.en?.toLowerCase().includes(s) ||
            sch.name?.hi?.toLowerCase().includes(s) ||
            sch.description?.en?.toLowerCase().includes(s) ||
            sch.description?.hi?.toLowerCase().includes(s) ||
            sch.category?.toLowerCase().includes(s) ||
            (sch.short_name && sch.short_name.toLowerCase().includes(s)) ||
            (sch.id && sch.id.toLowerCase().includes(s)) ||
            (sch.code && sch.code.toLowerCase().includes(s))
        );
      }
    }

    if (params.category && params.category !== 'all') {
      filtered = filtered.filter((sch) => sch.category === params.category);
    }

    if (params.level && params.level !== 'all') {
      filtered = filtered.filter((sch) => sch.level === params.level);
    }

    if (params.state && params.state !== 'ALL') {
      filtered = filtered.filter(
        (sch) =>
          sch.applicable_states.includes('ALL') ||
          sch.applicable_states.includes(params.state) ||
          sch.state_code === params.state
      );
    }

    return Promise.resolve({
      total: filtered.length,
      schemes: filtered,
      is_mock: true,
    });
  },

  getSchemeByCode(code) {
    const found = MOCK_SCHEMES.find((s) => s.code === code || s.id === code);
    if (found) {
      return Promise.resolve(found);
    }
    return Promise.reject(new Error(`Scheme with code '${code}' not found.`));
  },

  getFeaturedSchemes() {
    return Promise.resolve(MOCK_SCHEMES.filter((s) => s.featured));
  },

  getMockSchemesCount() {
    return MOCK_SCHEMES.length;
  },
};

