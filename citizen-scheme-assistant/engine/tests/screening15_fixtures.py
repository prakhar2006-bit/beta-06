"""Synthetic citizen inputs for tests; not policy definitions or citizen records."""
ALL_IDS = [f'in-cen-{i:06}' for i in range(1, 16)]
ORIGINAL_IDS = ['in-cen-000001', 'in-cen-000002', 'in-cen-000003', 'in-cen-000007', 'in-cen-000008']
ADDITIONAL_IDS = [sid for sid in ALL_IDS if sid not in ORIGINAL_IDS]


def sample_answers(scheme_id):
    return dict(age={'in-cen-000005':65, 'in-cen-000008':5, 'in-cen-000010':70}.get(scheme_id,30),
        existing_account=False, savings_account=True, contributions=True, indian_citizen=True,
        unorganised_worker=True, monthly_income='10000', statutory_cover=False, income_taxpayer=False,
        other_pension=False, ever_income_taxpayer=False, girl_child=True, guardian=True,
        resident_indian=True, family_limit=False, woman_applicant=True, household_has_lpg=False,
        poor_household=True, bpl_household=True, family_has_cultivable_land=True,
        income_taxpayer_last_year=False, family_government_employment=False,
        has_pucca_roof_or_wall=False, more_than_two_rooms=False, government_employee_in_family=False,
        member_income_above_15000=False, owns_motorised_three_four_wheeler=False,
        hands_tools_traditional_trade=True, self_employed_unorganised=True,
        government_service_family=False, similar_credit_last_five_years=False,
        family_already_registered=False, is_street_vendor=True, has_cov_or_lor=True,
        income_generating_business_plan=True, requested_loan_amount=50000,
        owned_suitable_roof=True, has_valid_electricity_connection=True,
        prior_solar_subsidy=False, cultivator_or_allied_activity=True)
