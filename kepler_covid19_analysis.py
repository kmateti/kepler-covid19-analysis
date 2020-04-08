# This script will prepare the JHU COVID-10 data for importing into kepler-gl


import pandas as pd
import math
import numpy as np
import glob
import os
import difflib
#from keplergl import KeplerGl


# Clone https://github.com/CSSEGISandData/COVID-19 in same parent folder
jhu_data_dir = '../COVID-19/csse_covid_19_data/csse_covid_19_daily_reports/'

# County population density data from https://randstatestats.org/
pop_density_data = 'US-Census-Population-Density-2019.csv'
    
sqmi_to_sqkm = 2.5899752356 #1.60934*1.60934

def get_us_covid19_data():
    # Read the latest COVID-19 data, where 'Admin2' is County data    
    all_data = glob.glob(os.path.join(jhu_data_dir, '*.csv'))
    latest_data = all_data[-1]
    df = pd.read_csv(latest_data);
    
    # Focus on US right now
    # Drop any data where Admin2 is nanpoints like the Diamond Princess
    covid_df = df.loc[df['Country_Region'] == 'US', :].dropna()

    return covid_df
    

def append_pop_density(covid_df):
    # Read the population density (no FIPS index, and in persons per sq mile)
    df = pd.read_csv(pop_density_data, skiprows=3)
    
    pop_density_array = np.zeros(covid_df.shape[0], dtype=float)
    
    for ii in range(covid_df.shape[0]):
        
        # if ii == 618:
        #     km = 1
        county = covid_df.iloc[ii]['Admin2']
        state_bool_idx = \
            df['State'].str.find(covid_df.iloc[ii]['Province_State']) != -1
        
        if isinstance(county, str):
            state_df = df.loc[state_bool_idx, :]
            county_idx = state_df['Area'].str.find(county) != -1
            
            if any(county_idx):
                pop_density_sq_miles = state_df.loc[county_idx, 'Density_persons_per_square_mile']\
                    .astype(float).values[0]
                pop_density_array[ii] = pop_density_sq_miles / sqmi_to_sqkm
            else:
                pop_density_array[ii] = np.nan                

        else:
            pop_density_array[ii] = np.nan
            print('Did not find {0}'.format(covid_df.iloc[ii]['Admin2']))
        
    covid_df['Density_persons_per_square_km'] = pd.Series(pop_density_array.transpose(), name='Density_persons_per_square_km')
    return covid_df
    

if __name__ == "__main__": 

    # Read the COVID-19 data    
    covid_usa_df = get_us_covid19_data();
    
    # Append US county population density data
    covid_w_popdensity = append_pop_density(covid_usa_df)
    
    # display_df = pd.DataFrame({'Province-County': df['Admin2'], 'Latitude' : df['Lat'], 'Longitude': df['Long_'],
    #                'Confirmed': df['Confirmed'], 'Deaths': df['Deaths'], 
    #                'Recovered': df['Recovered'],'Active': df['Active']
    #               })

    # Load an empty map
    # map_1 = KeplerGl()
    # map_1.add_data(data=display_df)
    # map_1.save_to_html()