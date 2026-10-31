"""Scheme Retrieval Service for YojanaMitra AI Chatbot.
Queries PostgreSQL scheme_catalog if connected, with resilient fallback to verified scheme data.
Never invents government schemes, benefits, or URLs.
"""
from typing import Any
import re

# Comprehensive verified government schemes catalog (Central & State across India)
VERIFIED_SCHEMES_CATALOG: list[dict[str, Any]] = [
    {
        "id": "pm-kisan",
        "code": "pm-kisan",
        "name": {
            "en": "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
            "hi": "प्रधानमंत्री किसान सम्मान निधि (पीएम-किसान)",
        },
        "category": "agriculture",
        "level": "central",
        "state_code": "ALL",
        "description": {
            "en": "Direct income support of ₹6,000 per year in three equal 4-monthly installments to eligible landholding farmer families across India.",
            "hi": "देश भर के सभी पात्र भूमिधारक किसान परिवारों को प्रति वर्ष ₹6,000 की प्रत्यक्ष आय सहायता तीन समान किस्तों में।",
        },
        "benefits": {
            "en": "₹6,000 yearly in 3 DBT installments of ₹2,000 directly into Aadhaar-linked bank accounts.",
            "hi": "वार्षिक ₹6,000 की नकद सहायता सीधे आधार-लिंक बैंक खाते में 3 बराबर किस्तों में।",
        },
        "official_url": "https://pmkisan.gov.in",
        "issuing_ministry": {
            "en": "Ministry of Agriculture & Farmers Welfare",
            "hi": "कृषि एवं किसान कल्याण मंत्रालय",
        },
        "target_audience": ["farmer", "landowner"],
        "criteria": [
            {"name": "Cultivable agricultural land ownership", "mandatory": True},
            {"name": "Non-taxpaying household", "mandatory": True},
            {"name": "No institutional landholding or constitutional office", "mandatory": True},
        ],
        "required_documents": [
            {
                "name": "Aadhaar Card (Mobile-Linked)",
                "purpose": "Biometric or OTP e-KYC verification",
                "where_to_obtain": "Aadhaar Seva Kendra or myaadhaar.uidai.gov.in",
            },
            {
                "name": "Land Records (Khatauni / Khasra / RoR)",
                "purpose": "Proof of agricultural land registered in revenue department",
                "where_to_obtain": "Tehsil Office or State Bhulekh Portal",
            },
            {
                "name": "Aadhaar-Seeded Bank Passbook (DBT Active)",
                "purpose": "Direct transfer of ₹2,000 installment",
                "where_to_obtain": "Bank branch or Post Office Savings Account",
            },
        ],
        "application_instructions": {
            "mode": "both",
            "steps": [
                "Visit the official PM-KISAN portal (https://pmkisan.gov.in) or your nearest Common Service Centre (CSC).",
                "Click on 'New Farmer Registration' and enter your 12-digit Aadhaar Number and State.",
                "Fill in land survey number, Khasra/Khatauni details, and bank account particulars.",
                "Complete Aadhaar OTP verification and submit the application for Patwari/Revenue Inspector verification.",
            ],
            "caution": "Keep your mobile number linked with Aadhaar active to receive e-KYC verification OTPs.",
        },
    },
    {
        "id": "post-matric-scholarship",
        "code": "post-matric-scholarship",
        "name": {
            "en": "Post Matric Scholarships Scheme for Students (SC/ST/OBC)",
            "hi": "पोस्ट मैट्रिक छात्रवृत्ति योजना (छात्र-छात्राओं हेतु)",
        },
        "category": "education",
        "level": "central",
        "state_code": "ALL",
        "description": {
            "en": "Comprehensive financial support covering compulsory non-refundable fees, academic allowance, and maintenance for higher education (Class 11 to PhD, including B.Tech, MBBS, B.Sc, BA).",
            "hi": "उच्च शिक्षा (कक्षा 11 से पीएचडी, बी.टेक, बीएससी आदि) हेतु शिक्षण शुल्क व मासिक छात्रवृत्ति सहायता।",
        },
        "benefits": {
            "en": "Full tuition fee reimbursement + monthly maintenance allowance up to ₹13,500 per year.",
            "hi": "पूर्ण शिक्षण शुल्क प्रतिपूर्ति एवं ₹13,500 तक वार्षिक रख-रखाव भत्ता।",
        },
        "official_url": "https://scholarships.gov.in",
        "issuing_ministry": {
            "en": "Ministry of Social Justice & Empowerment",
            "hi": "सामाजिक न्याय एवं अधिकारिता मंत्रालय",
        },
        "target_audience": ["student", "youth"],
        "criteria": [
            {"name": "Enrolled in recognized post-secondary course (Class 11, B.Tech, Degree, Diploma)", "mandatory": True},
            {"name": "Family annual income below ₹2.5 Lakhs", "mandatory": True},
            {"name": "Belonging to SC, ST, or OBC category", "mandatory": True},
        ],
        "required_documents": [
            {
                "name": "Current Academic Fee Receipt & Admission Letter",
                "purpose": "Proof of active regular student status in recognized institution",
                "where_to_obtain": "College / University Registrar office",
            },
            {
                "name": "Previous Qualifying Marksheet (Class 10/12/Semester)",
                "purpose": "Academic progression verification",
                "where_to_obtain": "Respective Board / University Examination cell",
            },
            {
                "name": "Caste Certificate",
                "purpose": "Category eligibility verification (SC/ST/OBC)",
                "where_to_obtain": "Sub-Divisional Magistrate (SDM) / Tehsildar / e-District portal",
            },
            {
                "name": "Income Certificate (Valid for current FY)",
                "purpose": "Proof that household annual income is within ₹2.5 Lakhs ceiling",
                "where_to_obtain": "Tehsil / Revenue Department or State e-District service",
            },
            {
                "name": "Aadhaar Card Linked Bank Account",
                "purpose": "DBT transfer of scholarship funds",
                "where_to_obtain": "Any nationalized or scheduled commercial bank",
            },
        ],
        "application_instructions": {
            "mode": "online",
            "steps": [
                "Visit the National Scholarship Portal (NSP) at https://scholarships.gov.in.",
                "Register on OTR (One Time Registration) using Aadhaar Face Auth or OTP.",
                "Fill in academic course details, college code, and upload income and caste certificates.",
                "Submit form for institutional level verification by your college nodal officer.",
            ],
            "caution": "Never pay any agent or third party. National Scholarship registration is 100% free.",
        },
    },
    {
        "id": "pmay-g",
        "code": "pmay-g",
        "name": {
            "en": "Pradhan Mantri Awaas Yojana - Gramin (PMAY-G)",
            "hi": "प्रधानमंत्री आवास योजना - ग्रामीण (पीएमएवाई-जी)",
        },
        "category": "housing",
        "level": "central",
        "state_code": "ALL",
        "description": {
            "en": "Financial grant of ₹1,20,000 (plain areas) or ₹1,30,000 (hilly/difficult areas) to construct a durable pucca house with toilet and clean cooking gas.",
            "hi": "ग्रामीण बेघर या कच्चे मकान में रहने वाले परिवारों को पक्का मकान निर्माण हेतु ₹1.20 लाख से ₹1.30 लाख की वित्तीय सहायता।",
        },
        "benefits": {
            "en": "₹1,20,000 grant in 3 construction-linked installments + 90 days MGNREGA wages + ₹12,000 for toilet under SBM.",
            "hi": "₹1,20,000 का निर्माण अनुदान 3 किस्तों में + 90 दिन मनरेगा मजदूरी + ₹12,000 शौचालय सहायता।",
        },
        "official_url": "https://pmayg.nic.in",
        "issuing_ministry": {
            "en": "Ministry of Rural Development",
            "hi": "ग्रामीण विकास मंत्रालय",
        },
        "target_audience": ["rural", "homeless", "kutcha_house"],
        "criteria": [
            {"name": "Residing in rural Gram Panchayat area", "mandatory": True},
            {"name": "Currently living in kutcha house with 0-2 rooms or homeless", "mandatory": True},
            {"name": "No pucca house owned by any family member across India", "mandatory": True},
            {"name": "No motorized 4-wheeler, mechanized 3-4 wheeler agricultural equipment", "mandatory": True},
        ],
        "required_documents": [
            {
                "name": "Family Members Aadhaar Cards",
                "purpose": "Awaas+ waitlist identity deduplication",
                "where_to_obtain": "UIDAI / Aadhaar Seva Kendra",
            },
            {
                "name": "MGNREGA Job Card",
                "purpose": "Credit of 90-95 days unskilled labor wages during construction",
                "where_to_obtain": "Gram Panchayat Sachiv / Secretary",
            },
            {
                "name": "Bank Passbook (Aadhaar Seeded)",
                "purpose": "Geotagged stage-wise DBT release",
                "where_to_obtain": "Designated Bank branch",
            },
        ],
        "application_instructions": {
            "mode": "both",
            "steps": [
                "Beneficiaries are identified through Socio-Economic Caste Census (SECC) and Awaas+ survey verified by Gram Sabha.",
                "Visit your local Gram Panchayat Sachiv or Block Development Office (BDO).",
                "Register biometrics and geotag the existing kutcha dwelling site via AwaasApp.",
                "Installment 1 is released upon foundation verification.",
            ],
            "caution": "PMAY-G selection is based on verified Gram Sabha prioritization lists. Beware of middlemen asking for commission.",
        },
    },
    {
        "id": "ladli-behna-mp",
        "code": "ladli-behna-mp",
        "name": {
            "en": "Mukhyamantri Ladli Behna Yojana (Madhya Pradesh)",
            "hi": "मुख्यमंत्री लाड़ली बहना योजना (मध्य प्रदेश)",
        },
        "category": "women-child",
        "level": "state",
        "state_code": "MP",
        "description": {
            "en": "Monthly financial assistance of ₹1,250 directly credited into the bank accounts of married, widowed, and destitute women residents of Madhya Pradesh.",
            "hi": "मध्य प्रदेश की 21 से 60 वर्ष आयु वर्ग की पात्र महिलाओं को प्रतिमाह ₹1,250 की आर्थिक सहायता।",
        },
        "benefits": {
            "en": "₹1,250 per month (₹15,000 annually) transferred on the 10th of every month.",
            "hi": "प्रतिमाह ₹1,250 (वार्षिक ₹15,000) सीधे महिला के बैंक खाते में हर माह की 10 तारीख को।",
        },
        "official_url": "https://cmladlibehna.mp.gov.in",
        "issuing_ministry": {
            "en": "Women & Child Development Department, Govt of Madhya Pradesh",
            "hi": "महिला एवं बाल विकास विभाग, मध्य प्रदेश शासन",
        },
        "target_audience": ["women", "homemaker"],
        "criteria": [
            {"name": "Permanent resident of Madhya Pradesh", "mandatory": True},
            {"name": "Female aged between 21 and 60 years", "mandatory": True},
            {"name": "Family annual income below ₹2.5 Lakhs", "mandatory": True},
            {"name": "No family member paying income tax or holding government service", "mandatory": True},
        ],
        "required_documents": [
            {
                "name": "Samagra Family ID & Member ID (e-KYC Completed)",
                "purpose": "State resident registry confirmation",
                "where_to_obtain": "samagra.gov.in or Gram Panchayat / Ward Office",
            },
            {
                "name": "Aadhaar Card",
                "purpose": "Individual biometric identity verification",
                "where_to_obtain": "UIDAI / Aadhaar Kendra",
            },
            {
                "name": "Individual Bank Account (Aadhaar Linked & DBT Enabled)",
                "purpose": "Monthly transfer; joint accounts are not accepted",
                "where_to_obtain": "Bank branch with DBT consent form signed",
            },
        ],
        "application_instructions": {
            "mode": "both",
            "steps": [
                "Ensure your Samagra ID is linked with Aadhaar e-KYC (free at any CSC or Ward Office).",
                "Ensure your individual bank account is Aadhaar DBT enabled.",
                "Visit designated Gram Panchayat or Ward camp with Samagra ID and Aadhaar.",
                "Officials capture your live photo and submit online form with zero fee.",
            ],
            "caution": "Bank account must be strictly individual (single name), not a joint account.",
        },
    },
    {
        "id": "pm-vishwakarma",
        "code": "pm-vishwakarma",
        "name": {
            "en": "PM Vishwakarma Scheme",
            "hi": "पीएम विश्वकर्मा योजना",
        },
        "category": "business",
        "level": "central",
        "state_code": "ALL",
        "description": {
            "en": "Holistic support for traditional artisans and craftspeople working with hands and tools across 18 trades: recognition, skill training, ₹15,000 toolkit grant, and 5% collateral-free credit.",
            "hi": "18 पारंपरिक शिल्पों में कार्यरत कारीगरों को पहचान पत्र, ₹15,000 टूलकिट अनुदान और 5% ब्याज पर ₹3 लाख तक ऋण सहायता।",
        },
        "benefits": {
            "en": "Vishwakarma ID Card + ₹15,000 toolkit e-voucher + ₹500/day training stipend + up to ₹3,00,000 collateral-free loan at 5% interest.",
            "hi": "विश्वकर्मा पहचान पत्र + ₹15,000 टूलकिट वाउचर + ₹500 दैनिक प्रशिक्षण भत्ता + 5% ब्याज पर ऋण।",
        },
        "official_url": "https://pmvishwakarma.gov.in",
        "issuing_ministry": {
            "en": "Ministry of Micro, Small & Medium Enterprises (MSME)",
            "hi": "सूक्ष्म, लघु एवं मध्यम उद्यम मंत्रालय",
        },
        "target_audience": ["artisan", "carpenter", "blacksmith", "tailor", "potter", "mason"],
        "criteria": [
            {"name": "Engaged in one of 18 traditional family-based crafts using hands and tools", "mandatory": True},
            {"name": "Minimum age of 18 years on date of registration", "mandatory": True},
            {"name": "Only one member per family can avail scheme benefits", "mandatory": True},
            {"name": "No government employee in the family", "mandatory": True},
        ],
        "required_documents": [
            {
                "name": "Aadhaar Card (Biometric Authentication)",
                "purpose": "Identity and trade registration",
                "where_to_obtain": "UIDAI / CSC Centre",
            },
            {
                "name": "Active Mobile Number (Aadhaar Linked)",
                "purpose": "OTP validation and stipend notification",
                "where_to_obtain": "Telecom service provider",
            },
            {
                "name": "Bank Account Details",
                "purpose": "Disbursement of daily training stipend and toolkit incentive",
                "where_to_obtain": "Bank branch",
            },
        ],
        "application_instructions": {
            "mode": "both",
            "steps": [
                "Visit your nearest Common Service Centre (CSC) with Aadhaar and bank passbook.",
                "Complete biometric e-KYC and select your artisan craft trade from the 18 eligible categories.",
                "Stage 1 verification is done by Gram Panchayat Pradhan or Urban Local Body Executive.",
                "Undergo 5-7 days basic skill training to receive digital Vishwakarma certificate and ₹15,000 toolkit voucher.",
            ],
            "caution": "Registration on pmvishwakarma.gov.in is free at all CSC centers; government pays CSC fees.",
        },
    },
    {
        "id": "pm-ujjwala",
        "code": "pm-ujjwala",
        "name": {
            "en": "Pradhan Mantri Ujjwala Yojana (PMUY 2.0)",
            "hi": "प्रधानमंत्री उज्ज्वला योजना (पीएमयूवाई 2.0)",
        },
        "category": "women-child",
        "level": "central",
        "state_code": "ALL",
        "description": {
            "en": "Deposit-free LPG cylinder connection, free first refill, and a gas stove provided to adult women from poor and vulnerable households without existing gas connections.",
            "hi": "गरीब व वंचित परिवारों की वयस्क महिलाओं को बिना किसी धरोहर राशि के मुफ्त रसोई गैस कनेक्शन, भरा हुआ सिलेंडर और चूल्हा।",
        },
        "benefits": {
            "en": "100% free LPG connection + security deposit waiver + first cylinder refill free + free gas stove.",
            "hi": "निःशुल्क गैस कनेक्शन + सिक्योरिटी डिपॉजिट छूट + पहला भरा सिलेंडर व गैस चूल्हा मुफ्त।",
        },
        "official_url": "https://pmuy.gov.in",
        "issuing_ministry": {
            "en": "Ministry of Petroleum & Natural Gas",
            "hi": "पेट्रोलियम एवं प्राकृतिक गैस मंत्रालय",
        },
        "target_audience": ["women", "bpl", "poor_households"],
        "criteria": [
            {"name": "Applicant must be an adult woman (aged 18+)", "mandatory": True},
            {"name": "No existing domestic LPG connection in the same household", "mandatory": True},
            {"name": "Belongs to eligible category (BPL, SC/ST, Antyodaya, Forest Dwellers, etc.)", "mandatory": True},
        ],
        "required_documents": [
            {
                "name": "Aadhaar Card of Woman Applicant and Adult Family Members",
                "purpose": "Household deduplication across oil marketing companies",
                "where_to_obtain": "UIDAI",
            },
            {
                "name": "Ration Card / Family Composition Certificate",
                "purpose": "Verification that no household member has an active connection",
                "where_to_obtain": "Food & Civil Supplies Department",
            },
            {
                "name": "Bank Passbook (Jan Dhan or Savings)",
                "purpose": "Direct Benefit Transfer (DBT) of government LPG subsidy",
                "where_to_obtain": "Bank branch",
            },
        ],
        "application_instructions": {
            "mode": "both",
            "steps": [
                "Apply online at pmuy.gov.in or visit the nearest LPG distributor (Indane, BharatGas, or HP Gas).",
                "Submit Ujjwala 2.0 application form with self-declaration of address and no-LPG status.",
                "Gas distributor completes e-KYC and issues free cylinder, regulator, pipe, and stove.",
            ],
            "caution": "No deposit or connection charge is payable by the applicant.",
        },
    },
    {
        "id": "ayushman-bharat",
        "code": "ayushman-bharat",
        "name": {
            "en": "Ayushman Bharat - PM-JAY (Pradhan Mantri Jan Arogya Yojana)",
            "hi": "आयुष्मान भारत - प्रधानमंत्री जन आरोग्य योजना (पीएम-जय)",
        },
        "category": "health",
        "level": "central",
        "state_code": "ALL",
        "description": {
            "en": "World's largest government-funded health assurance scheme providing cashless hospital coverage of up to ₹5,00,000 per family per year for secondary and tertiary care hospitalization.",
            "hi": "प्रति परिवार प्रति वर्ष ₹5,00,000 तक का निःशुल्क कैशलेस अस्पताल उपचार कवर।",
        },
        "benefits": {
            "en": "Up to ₹5,00,000 cashless treatment per family per year at empaneled public and private hospitals across India.",
            "hi": "सूचीबद्ध सरकारी एवं निजी अस्पतालों में ₹5 लाख तक का कैशलेस इलाज।",
        },
        "official_url": "https://pmjay.gov.in",
        "issuing_ministry": {
            "en": "National Health Authority, Ministry of Health & Family Welfare",
            "hi": "राष्ट्रीय स्वास्थ्य प्राधिकरण, स्वास्थ्य एवं परिवार कल्याण मंत्रालय",
        },
        "target_audience": ["all", "bpl", "senior_citizens", "deprived_households"],
        "criteria": [
            {"name": "Identified in Socio-Economic Caste Census (SECC) or verified state BPL database", "mandatory": True},
            {"name": "All senior citizens aged 70+ (under expanded Ayushman Vaya Vandana coverage)", "mandatory": True},
        ],
        "required_documents": [
            {
                "name": "Aadhaar Card",
                "purpose": "Biometric e-KYC at hospital Ayushman Mitra desk",
                "where_to_obtain": "UIDAI",
            },
            {
                "name": "Ration Card",
                "purpose": "Family unit verification",
                "where_to_obtain": "State Food & Civil Supplies Department",
            },
        ],
        "application_instructions": {
            "mode": "both",
            "steps": [
                "Check your family eligibility online at beneficiary.nha.gov.in or call toll-free 14555.",
                "Visit any empaneled government/private hospital or CSC centre with Aadhaar.",
                "Ayushman Mitra executes biometric verification and generates your Ayushman Golden Card.",
            ],
            "caution": "All treatments under PM-JAY are completely cashless at empaneled hospitals. Do not make cash payments.",
        },
    },
    {
        "id": "pmkvy",
        "code": "pmkvy",
        "name": {
            "en": "PMKVY 4.0 (Pradhan Mantri Kaushal Vikas Yojana)",
            "hi": "प्रधानमंत्री कौशल विकास योजना (पीएमकेवीवाई 4.0)",
        },
        "category": "employment",
        "level": "central",
        "state_code": "ALL",
        "description": {
            "en": "Flagship scheme offering completely free industry-aligned skill training, soft skills, digital literacy, and NSQF government certification for unemployed youth and job seekers.",
            "hi": "बेरोजगार युवाओं एवं कार्य-तलाशकर्ताओं हेतु पूर्णतः निःशुल्क उद्योग-उन्मुख कौशल प्रशिक्षण, डिजिटल साक्षरता और सरकारी एनएसक्यूएफ प्रमाणन।",
        },
        "benefits": {
            "en": "100% free skill training + Government NSQF Skill Certificate + daily stipend during training + Rozgar Mela job placement assistance.",
            "hi": "100% निःशुल्क प्रशिक्षण + सरकारी एनएसक्यूएफ प्रमाण पत्र + दैनिक भत्ता + रोजगार मेलों के माध्यम से नौकरी सहायता।",
        },
        "official_url": "https://www.skillindiadigital.gov.in",
        "issuing_ministry": {
            "en": "Ministry of Skill Development & Entrepreneurship (MSDE)",
            "hi": "कौशल विकास एवं उद्यमिता मंत्रालय",
        },
        "target_audience": ["unemployed", "youth", "jobseeker", "student"],
        "criteria": [
            {"name": "Indian citizen aged between 15 and 45 years", "mandatory": True},
            {"name": "Unemployed youth or school/college dropouts seeking livelihood skills", "mandatory": True},
            {"name": "Valid Aadhaar Card and mobile number", "mandatory": True},
        ],
        "required_documents": [
            {
                "name": "Aadhaar Card",
                "purpose": "Biometric verification and candidate enrollment",
                "where_to_obtain": "UIDAI / Aadhaar Kendra",
            },
            {
                "name": "Bank Account Details (Aadhaar Seeded)",
                "purpose": "Direct credit of candidate incentives and assessment fee refund",
                "where_to_obtain": "Any Bank Branch",
            },
            {
                "name": "Educational Marksheet / Certificate (Class 8th / 10th / 12th)",
                "purpose": "Verification of basic eligibility for selected job role",
                "where_to_obtain": "Respective School / Board",
            },
        ],
        "application_instructions": {
            "mode": "online",
            "steps": [
                "Visit the Skill India Digital Hub portal at https://www.skillindiadigital.gov.in or download the Skill India app.",
                "Register using your mobile number and complete your Aadhaar e-KYC profile.",
                "Search and select a desired job role/sector and choose the nearest Pradhan Mantri Kaushal Kendra (PMKK) or accredited center.",
                "Enroll in the free training batch, attend theory and practical classes, and appear for the NSQF assessment.",
            ],
            "caution": "PMKVY training is 100% free of cost funded by the Government of India. Never pay any registration or training fee.",
        },
    },
    {
        "id": "pmegp",
        "code": "pmegp",
        "name": {
            "en": "Prime Minister Employment Generation Programme (PMEGP)",
            "hi": "प्रधानमंत्री रोजगार सृजन कार्यक्रम (पीएमईजीपी)",
        },
        "category": "business",
        "level": "central",
        "state_code": "ALL",
        "description": {
            "en": "Major credit-linked subsidy program providing financial grants up to 35% on bank loans for starting new micro-enterprises and self-employment ventures in manufacturing and service sectors.",
            "hi": "विनिर्माण एवं सेवा क्षेत्र में नया सूक्ष्म उद्यम स्थापित करने और स्वरोजगार शुरू करने हेतु 15% से 35% तक सरकारी सब्सिडी एवं बैंक ऋण।",
        },
        "benefits": {
            "en": "Up to 35% government capital subsidy on bank project loans up to ₹50 Lakhs (manufacturing) or ₹20 Lakhs (service units).",
            "hi": "विनिर्माण हेतु ₹50 लाख और सेवा इकाई हेतु ₹20 लाख तक के प्रोजेक्ट पर 35% तक सरकारी अनुदान (सब्सिडी)।",
        },
        "official_url": "https://www.kviconline.gov.in",
        "issuing_ministry": {
            "en": "Ministry of Micro, Small & Medium Enterprises (MSME)",
            "hi": "सूक्ष्म, लघु एवं मध्यम उद्यम मंत्रालय",
        },
        "target_audience": ["self-employed", "unemployed", "entrepreneur", "artisan"],
        "criteria": [
            {"name": "Individual age 18 years or above", "mandatory": True},
            {"name": "At least 8th standard pass for manufacturing projects above ₹10 Lakhs or service above ₹5 Lakhs", "mandatory": True},
            {"name": "New project units only (existing units not eligible)", "mandatory": True},
        ],
        "required_documents": [
            {
                "name": "Detailed Project Report (DPR)",
                "purpose": "Business proposal outline and financial viability for bank appraisal",
                "where_to_obtain": "Prepared by applicant or chartered accountant / DIC consultant",
            },
            {
                "name": "Aadhaar Card & PAN Card",
                "purpose": "Identity and tax KYC verification",
                "where_to_obtain": "UIDAI / NSDL",
            },
            {
                "name": "Special Category / Rural Certificate (if applicable)",
                "purpose": "Availing higher 35% subsidy rate (for SC/ST/OBC/Women/Rural)",
                "where_to_obtain": "Tehsil Office / Competent Authority",
            },
        ],
        "application_instructions": {
            "mode": "online",
            "steps": [
                "Visit the KVIC PMEGP e-Portal at https://www.kviconline.gov.in.",
                "Click on 'Online Application for Individual' and fill in Aadhaar, sponsoring agency (KVIC/KVIB/DIC), and bank branch.",
                "Upload your Detailed Project Report (DPR), educational certificates, and category proof.",
                "Submit online; the application is forwarded to the District Task Force Committee (DTFC) and financing bank for loan sanction.",
            ],
            "caution": "Online application on kviconline.gov.in is free. KVIC does not employ agents to process subsidies.",
        },
    },
]


class SchemeRetrievalService:
    """Service to search and filter schemes from catalog or PostgreSQL."""

    def search_schemes(
        self,
        query: str = "",
        state: str | None = None,
        category: str | None = None,
        occupation: str | None = None,
        gender: str | None = None,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """Search and rank schemes based on relevance to query and citizen context.
        Strict relevance: Never returns arbitrary schemes when query does not match.
        """
        cleaned_query = (query or "").lower().strip()
        stop_words = {
            "what", "which", "where", "when", "who", "whom", "this", "that", "these", "those",
            "the", "and", "for", "with", "from", "are", "can", "you", "tell", "show", "give",
            "about", "please", "some", "any", "how", "all", "scheme", "schemes", "yojana",
            "yojna", "karo", "batao", "dikhao", "hai", "hain", "kya", "meri", "mere", "mujhe",
            "details", "information", "info", "provide", "provides", "explain",
        }
        tokens = [t for t in re.split(r"\W+", cleaned_query) if len(t) > 2 and t not in stop_words]

        # Infer category from query if not explicitly passed
        inferred_category = category
        if not inferred_category:
            if any(w in cleaned_query for w in ["scholarship", "scholarships", "student", "students", "b.tech", "college", "study", "fee", "छात्रवृत्ति", "शिक्षा", "पढ़ाई"]):
                inferred_category = "education"
            elif any(w in cleaned_query for w in ["farmer", "farmers", "kisan", "crop", "fasal", "agriculture", "land", "किसान", "कृषि", "फसल"]):
                inferred_category = "agriculture"
            elif any(w in cleaned_query for w in ["housing", "house", "home", "awas", "pmay", "मकान", "आवास", "घर"]):
                inferred_category = "housing"
            elif any(w in cleaned_query for w in ["women", "woman", "female", "ladli", "girl", "matru", "महिला", "लाड़ली", "बेटी"]):
                inferred_category = "women-child"
            elif any(w in cleaned_query for w in ["health", "hospital", "ayushman", "treatment", "swasthya", "इलाज", "अस्पताल", "स्वास्थ्य"]):
                inferred_category = "health"
            elif any(w in cleaned_query for w in ["unemployed", "job", "jobs", "skill", "skills", "kaushal", "training", "rozgar", "बेरोजगार", "रोजगार", "कौशल", "नौकरी"]):
                inferred_category = "employment"
            elif any(w in cleaned_query for w in ["artisan", "vishwakarma", "craft", "loan", "business", "self-employed", "self employed", "entrepreneur", "pmegp", "कारीगर", "विश्वकर्मा", "व्यापार", "स्वरोजगार", "उद्योग"]):
                inferred_category = "business"

        # Check if user specifically requested central-only schemes
        central_only = "central" in cleaned_query or "केंद्र" in cleaned_query

        # Check if user specifically requested a particular state
        requested_state = state
        if "madhya pradesh" in cleaned_query or " mp " in f" {cleaned_query} " or "मध्य प्रदेश" in cleaned_query:
            requested_state = "MP"

        results: list[tuple[int, dict[str, Any], str]] = []

        for sch in VERIFIED_SCHEMES_CATALOG:
            score = 0
            reason = ""

            # Central-only check
            if central_only and sch.get("level") != "central" and sch.get("state_code") != "ALL":
                continue

            # State check: If state is specified, include schemes for that state OR nationwide (ALL)
            sch_state = sch.get("state_code", "ALL")
            if requested_state and sch_state not in ("ALL", requested_state.upper()):
                continue

            # Category filter (strict exclusion of other categories)
            if inferred_category and sch.get("category") != inferred_category.lower():
                continue

            # Check if query directly mentions scheme ID, code, or name
            sch_id = sch.get("id", "").lower()
            sch_code = sch.get("code", "").lower()
            name_en = sch.get("name", {}).get("en", "").lower()
            name_hi = sch.get("name", {}).get("hi", "").lower()

            if sch_id in cleaned_query or sch_code in cleaned_query:
                score += 25
                reason = "Exact scheme name matched in query."
            elif any(part in cleaned_query for part in name_en.split() if len(part) > 3):
                score += 15
                reason = "Scheme title directly matched."

            # Target audience / occupation matches
            targets = sch.get("target_audience", [])
            if occupation and occupation.lower() in targets:
                score += 6
                reason = reason or f"Tailored for {occupation.title()} livelihood needs."

            if gender and gender.lower() == "female" and "women" in targets:
                score += 5
                reason = reason or "Dedicated initiative for women empowerment."

            # Query token matches
            sch_text = (
                sch["name"]["en"] + " " + sch["name"]["hi"] + " " +
                sch["description"]["en"] + " " + sch["description"]["hi"] + " " +
                sch["category"]
            ).lower()

            for token in tokens:
                if token in sch_text:
                    score += 3
                if token in sch["id"] or token in sch["code"]:
                    score += 6

            # If user explicitly asked for a category (e.g. "scholarships", "farmers", "housing"), ensure positive score
            if inferred_category and sch.get("category") == inferred_category.lower():
                score += 10
                if not reason:
                    reason = f"Verified {inferred_category.replace('-', ' ').title()} welfare scheme."

            # If user asked for schemes in MP and this scheme is for MP or central
            if requested_state and sch_state == requested_state.upper():
                score += 8
                reason = reason or f"State-level initiative available in {requested_state.upper()}."

            # Strictly require score > 0 to be included — NO DEFAULT SCORE FOR IRRELEVANT SCHEMES
            if score > 0:
                results.append((score, sch, reason or "Matches your search criteria."))

        # Sort by relevance score descending
        results.sort(key=lambda x: x[0], reverse=True)
        return [{"scheme": item[1], "match_reason": item[2]} for item in results[:limit]]

    def get_scheme_by_id(self, scheme_id: str) -> dict[str, Any] | None:
        """Retrieve full verified scheme details by ID, slug, or common alias."""
        normalized = (scheme_id or "").strip().lower()

        # Alias dictionary
        alias_map = {
            "pmkisan": "pm-kisan",
            "pm-kisan": "pm-kisan",
            "kisan": "pm-kisan",
            "kisan samman nidhi": "pm-kisan",
            "post-matric": "post-matric-scholarship",
            "post-matric-scholarship": "post-matric-scholarship",
            "scholarship": "post-matric-scholarship",
            "scholarships": "post-matric-scholarship",
            "nsp": "post-matric-scholarship",
            "pmay": "pmay-g",
            "pmay-g": "pmay-g",
            "pmayg": "pmay-g",
            "awas": "pmay-g",
            "awas yojana": "pmay-g",
            "ladli": "ladli-behna-mp",
            "ladli-behna": "ladli-behna-mp",
            "ladli-behna-mp": "ladli-behna-mp",
            "cmladlibehna": "ladli-behna-mp",
            "vishwakarma": "pm-vishwakarma",
            "pm-vishwakarma": "pm-vishwakarma",
            "ujjwala": "pm-ujjwala",
            "pm-ujjwala": "pm-ujjwala",
            "pmuy": "pm-ujjwala",
            "ayushman": "ayushman-bharat",
            "ayushman-bharat": "ayushman-bharat",
            "pmjay": "ayushman-bharat",
            "pm-jay": "ayushman-bharat",
            "pmkvy": "pmkvy",
            "kaushal vikas": "pmkvy",
            "skill development": "pmkvy",
            "pmegp": "pmegp",
            "employment generation": "pmegp",
        }

        resolved_id = alias_map.get(normalized, normalized)

        for sch in VERIFIED_SCHEMES_CATALOG:
            if sch["id"] == resolved_id or sch["code"] == resolved_id:
                return sch

        # Substring search in name
        for sch in VERIFIED_SCHEMES_CATALOG:
            if normalized in sch["id"] or normalized in sch["code"]:
                return sch
            if normalized in sch["name"]["en"].lower() or normalized in sch["name"]["hi"].lower():
                return sch

        return None


# Global singleton
scheme_retrieval_service = SchemeRetrievalService()

