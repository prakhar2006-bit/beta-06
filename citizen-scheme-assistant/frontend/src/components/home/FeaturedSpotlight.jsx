import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, ArrowRight, Check, ExternalLink } from 'lucide-react';

const slides = [
  { tag: 'For farmers', title: 'PM-KISAN', description: 'Direct income support for eligible farmer families across India.', highlights: ['₹6,000 annual support', 'Landholding farmers', 'Direct bank transfer'], href: '/schemes/pm-kisan' },
  { tag: 'For every family', title: 'Ayushman Bharat', description: 'Health cover that helps families access quality hospital care without financial stress.', highlights: ['Up to ₹5 lakh cover', 'Cashless treatment', '12 crore+ families'], href: '/schemes/pm-jay' },
  { tag: 'For homeowners', title: 'PM Awas Yojana', description: 'Support to help eligible families build or improve a safe, permanent home.', highlights: ['Housing assistance', 'Urban & rural coverage', 'Interest subsidy'], href: '/schemes/pmay' },
];

export const FeaturedSpotlight = () => {
  const [active, setActive] = useState(0);
  const [paused, setPaused] = useState(false);
  const slide = slides[active];

  useEffect(() => {
    if (paused) return undefined;
    const timer = window.setInterval(() => setActive((current) => (current + 1) % slides.length), 5500);
    return () => window.clearInterval(timer);
  }, [paused]);

  const goTo = (direction) => setActive((current) => (current + direction + slides.length) % slides.length);

  return (
    <section className="spotlight-section py-12 md:py-16 relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between mb-5">
          <p className="eyebrow">Featured scheme spotlight</p>
          <span className="text-xs text-stone-500">{String(active + 1).padStart(2, '0')} / {String(slides.length).padStart(2, '0')}</span>
        </div>
        <div
          className="spotlight-banner relative overflow-hidden min-h-[300px] md:min-h-[340px] bg-slate-950 text-white"
          onMouseEnter={() => setPaused(true)}
          onMouseLeave={() => setPaused(false)}
        >
          <div className="absolute inset-0 spotlight-wash" aria-hidden="true" />
          <div className="relative z-10 p-7 sm:p-10 md:p-14 max-w-2xl">
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-orange-300 mb-5">{slide.tag}</p>
            <h2 className="text-3xl sm:text-5xl font-black tracking-[-0.03em] mb-4">{slide.title}</h2>
            <p className="text-sm sm:text-base text-stone-200 max-w-lg leading-relaxed mb-6">{slide.description}</p>
            <div className="flex flex-wrap gap-x-5 gap-y-2 mb-8">
              {slide.highlights.map((highlight) => <span key={highlight} className="inline-flex items-center gap-1.5 text-xs text-stone-100"><Check className="w-3.5 h-3.5 text-emerald-300" />{highlight}</span>)}
            </div>
            <Link to={slide.href} className="spotlight-cta group inline-flex items-center gap-3 px-5 py-3 text-xs font-bold text-white active:scale-95 transition-all">
              Check Eligibility <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
            </Link>
          </div>
          <div className="absolute right-6 bottom-6 hidden md:flex items-center gap-2">
            <button type="button" aria-label="Previous scheme" onClick={() => goTo(-1)} className="spotlight-arrow"><ArrowLeft className="w-4 h-4" /></button>
            <button type="button" aria-label="Next scheme" onClick={() => goTo(1)} className="spotlight-arrow"><ArrowRight className="w-4 h-4" /></button>
          </div>
          <div className="absolute bottom-0 left-0 right-0 flex gap-1.5 px-7 sm:px-10 md:px-14 pb-4">
            {slides.map((item, index) => <button type="button" key={item.title} aria-label={`Show ${item.title}`} onClick={() => setActive(index)} className="h-1 flex-1 bg-white/25 overflow-hidden"><span className={`block h-full bg-orange-400 transition-all duration-[5500ms] ${active === index && !paused ? 'w-full' : active === index ? 'w-1/2' : 'w-0'}`} /></button>)}
          </div>
        </div>
        <Link to="/schemes" className="group mt-4 inline-flex items-center gap-1.5 text-xs font-semibold text-stone-600 hover:text-orange-700 transition-colors">View all schemes <ExternalLink className="w-3.5 h-3.5 transition-transform group-hover:translate-x-0.5" /></Link>
      </div>
    </section>
  );
};
