import React from 'react';
import { HeroSection } from '../components/home/HeroSection';
import { FeaturedSpotlight } from '../components/home/FeaturedSpotlight';
import { CategoryCard } from '../components/home/CategoryCard';
import { HowItWorks } from '../components/home/HowItWorks';
import { FeaturedSchemes } from '../components/home/FeaturedSchemes';
import { TrustPrivacy } from '../components/home/TrustPrivacy';
import { useLanguage } from '../i18n/LanguageContext';

export const HomePage = () => {
  const { t } = useLanguage();

  const categories = [
    { id: 'agriculture', titleKey: 'catAgriculture', descKey: 'catAgricultureDesc' },
    { id: 'women-child', titleKey: 'catWomenChild', descKey: 'catWomenChildDesc' },
    { id: 'education', titleKey: 'catEducation', descKey: 'catEducationDesc' },
    { id: 'health', titleKey: 'catHealth', descKey: 'catHealthDesc' },
    { id: 'housing', titleKey: 'catHousing', descKey: 'catHousingDesc' },
    { id: 'employment', titleKey: 'catEmployment', descKey: 'catEmploymentDesc' },
    { id: 'business', titleKey: 'catBusiness', descKey: 'catBusinessDesc' },
    { id: 'social-welfare', titleKey: 'catSocialWelfare', descKey: 'catSocialWelfareDesc' },
  ];

  return (
    <div className="flex-1 relative">
      {/* 1. Hero Section */}
      <HeroSection />

      {/* 2. Featured scheme spotlight */}
      <FeaturedSpotlight />

      {/* 3. Popular Categories */}
      <section className="py-24 md:py-32 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-12">
          <div>
          <p className="eyebrow mb-4">Targeted welfare</p>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-950 tracking-tight mb-3">
            {t('categoriesHeading', 'Browse by Category')}
          </h2>
          <p className="text-base text-stone-500 max-w-xl">
            {t(
              'categoriesSubheading',
              'Find schemes tailored to your occupation, family needs, and life stage'
            )}
          </p>
          </div>
          <span className="text-sm text-stone-500 md:pb-1">8 areas of support</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 border-t border-stone-300">
          {categories.map((cat) => (
            <CategoryCard
              key={cat.id}
              categoryId={cat.id}
              titleKey={cat.titleKey}
              descKey={cat.descKey}
            />
          ))}
        </div>
      </section>

      {/* 4. How It Works */}
      <HowItWorks />

      {/* 5. Featured Schemes */}
      <FeaturedSchemes />

      {/* 6. Trust & Privacy */}
      <TrustPrivacy />
    </div>
  );
};
