import pandas as pd
import numpy as np

whp_df = pd.read_excel('whp_data.xlsx', sheet_name='county_summary') #load in the files for each
hospital_df = pd.read_excel('hospital_data.xlsx', sheet_name='full_data_set_heatmap')

whp_df['GEOID_CLEAN'] = whp_df['GEOID_CLEAN'].astype(str) #change to string to make the merge easier

hospital_df['FIPS_CLEAN'] = hospital_df['FIPS'].fillna(0).astype(int).astype(str).str.zfill(5)
#very long way to pad the digits the same way as GEOID_CLEAN 
hospital_df.loc[hospital_df['FIPS_CLEAN'] == '00000', 'FIPS_CLEAN'] = np.nan #return missign values back to NaN

merged_df = pd.merge(
    whp_df,
    hospital_df,
    left_on='GEOID_CLEAN',
    right_on='FIPS_CLEAN',
    how = 'left'
) #merged!

major_trauma_adult = merged_df[
    (merged_df['ADULT_TRAUMA_L1'] == 1.0) |
    (merged_df['ADULT_TRAUMA_L2'] == 1.0)
] #filters the hospitals w/ adult trauma ability

major_trauma_peds = merged_df[
    (merged_df['PEDS_TRAUMA_L1'] == 1.0) |
    (merged_df['PEDS_TRAUMA_L2'] == 1.0)
] #filters the hospitals w/ ped trauma ability

trauma_without_burn_adult = major_trauma_adult[
    (major_trauma_adult['ABA_VERIFIED'] != 'Yes') &
    ((major_trauma_adult['BURN_ADULT'] != 1.0) | (pd.isna(major_trauma_adult['BURN_ADULT'])))
] #either not ABA verified or no burn adult capability

trauma_without_burn_peds = major_trauma_peds[
    (major_trauma_peds['ABA_VERIFIED'] != 'Yes') &
    ((major_trauma_peds['BURN_PEDS'] != 1.0) | (pd.isna(major_trauma_peds['BURN_PEDS'])))
] #either not ABA verified or no burn ped capability

if 'H + VH Pct' in merged_df.columns:
    high_risk_threshold = merged_df['H + VH Pct'].quantile(0.8) #using the percentiles from the wildfire data

    high_risk_adult = trauma_without_burn_adult[
    trauma_without_burn_adult['H + VH Pct'] >= high_risk_threshold
    ] #classifies the high-risk adult areas

    high_risk_peds = trauma_without_burn_peds[
    trauma_without_burn_peds['H + VH Pct'] >= high_risk_threshold
    ] #classifies the high-risk ped areas

    
    print(f"""
    Adult:
        Total trauma centers: {len(major_trauma_adult)}
        Without burn units: {len(trauma_without_burn_adult)}
        In high-risk areas: {len(high_risk_adult)}

    Pediatric:
        Total trauma centers: {len(major_trauma_peds)}
        Without burn units: {len(trauma_without_burn_peds)}
        In high-risk areas: {len(high_risk_peds)}
    """)
    # Show examples
    display_cols = ['HOSPITAL_NAME', 'STATE', 'County', 'H + VH Pct', 'TOTAL_BEDS']
    if len(high_risk_adult) > 0:
        print("Adult Hospitals at Risk")
        print(high_risk_adult[display_cols].sort_values('H + VH Pct', ascending=False).head(10).to_string(index=False))

    if len(high_risk_peds) > 0:
        print("Pediatric Hospitals at Risk")
        print(high_risk_peds[display_cols].sort_values('H + VH Pct', ascending=False).head(10).to_string(index=False))