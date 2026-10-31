const valueOf = (answers, key) => answers?.[key]?.value ?? answers?.[key];

export const ageFromDob = (dob, today = new Date()) => {
  if (!dob) return null;
  const birth = new Date(`${dob}T00:00:00`);
  if (Number.isNaN(birth.getTime()) || birth > today) return null;
  let age = today.getFullYear() - birth.getFullYear();
  const beforeBirthday = today.getMonth() < birth.getMonth() || (today.getMonth() === birth.getMonth() && today.getDate() < birth.getDate());
  if (beforeBirthday) age -= 1;
  return age >= 0 ? age : null;
};

export const profileToAnswers = (answers, today) => {
  const mapped = {};
  const set = (key, value) => { if (value !== undefined && value !== null && value !== '' && value !== 'prefer_not_to_say' && value !== 'dont_know') mapped[key] = value; };
  set('state', valueOf(answers, 'domicile'));
  set('age', ageFromDob(valueOf(answers, 'date_of_birth'), today));
  set('gender', valueOf(answers, 'gender'));
  set('area_type', valueOf(answers, 'rural_urban'));
  set('income_taxpayer', valueOf(answers, 'income_taxpayer'));
  set('owns_land', valueOf(answers, 'agricultural_land') === 'none' ? false : valueOf(answers, 'agricultural_land') ? true : undefined);
  set('housing_type', valueOf(answers, 'house_type'));
  set('occupation', valueOf(answers, 'occupation')?.[0]);
  if (valueOf(answers, 'ration_card_type') === 'bpl' || valueOf(answers, 'ration_card_type') === 'antyodaya') mapped.household_attributes = ['has_bpl_card'];
  if (valueOf(answers, 'lpg_connection') === 'yes') mapped.household_attributes = [...(mapped.household_attributes || []), 'has_existing_lpg'];
  if (valueOf(answers, 'disability') === 'yes') mapped.household_attributes = [...(mapped.household_attributes || []), 'has_disability'];
  if (valueOf(answers, 'income_taxpayer') === 'yes') mapped.household_attributes = [...(mapped.household_attributes || []), 'pays_income_tax'];
  if (valueOf(answers, 'motor_vehicle') === 'yes') mapped.household_attributes = [...(mapped.household_attributes || []), 'owns_car_tractor'];
  return mapped;
};

export const profileAnswerSources = (answers) => Object.fromEntries(Object.entries(answers || {}).map(([key, item]) => [key, item?.source || 'self']));
