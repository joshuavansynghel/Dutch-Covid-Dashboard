from datetime import datetime, timedelta
from pathlib import Path

import socket
import pandas as pd
import numpy as np


class DataManager:
	"""
	DataManager handles loading, cleaning, merging and saving COVID data from the Netherlands,
	including retrieving fresh data from the web when outdated.
	"""

	LOCAL_FOLDER = 'Data'
	DATA_URLS = {
        'covid_cases': [
            'https://data.rivm.nl/covid-19/COVID-19_aantallen_gemeente_per_dag.csv',
            'https://data.rivm.nl/covid-19/COVID-19_aantallen_gemeente_per_dag_tm_03102021.csv'
        ],
        'covid_hospitalizations': [
            'https://data.rivm.nl/covid-19/COVID-19_ziekenhuisopnames.csv',
            'https://data.rivm.nl/data/covid-19/COVID-19_ziekenhuisopnames_tm_03102021.csv'
        ]
    }
	MAX_DAYS_DATA_OUTDATED = 7

	def __init__(self):
		"""
		Initiliazes the DataManager by refreshing COVID data if necessary and
		setting unique values for provinces and years.
		"""
		self.unique_year_values = []
		self.unique_province_values = []

		self._refresh_covid_data()
		self._set_unique_values()

	
	def _refresh_covid_data(self):
		"""
		Checks if local COVID data is outdated or missing, and refrehed the data
		by downloading from the web if necessary.
		"""
		data_file = Path(self.LOCAL_FOLDER) / 'covid_alltime.csv'

		# Check if file exists and if it's been updated within the allowed time frame
		if data_file.exists():
			file_age = datetime.now() - datetime.fromtimestamp(data_file.stat().st_mtime)

			if file_age < timedelta(days=self.MAX_DAYS_DATA_OUTDATED):
				return # Data is up to date
		
		# Download fresh data if internet is available, otherwise raise error
		if self._check_internet_connection():
			self._read_and_save_data_from_web()
		else:
			raise ConnectionError("No internet connection and data is outdated or missing")


	def _check_internet_connection(self):
		"""Checks internet connectivity by attempting to connect to a DNS server."""
		try:
			socket.create_connection(('8.8.8.8', 53), timeout=3)
			return True
		except OSError:
			return False


	def _read_and_save_data_from_web(self):
		"""Reads data from web sources, cleans and merges it, and then saves it locally."""
		raw_case_data = self._read_and_concat_data('covid_cases')
		clean_case_data = self._clean_case_data(raw_case_data)

		raw_hospital_data = self._read_and_concat_data('covid_hospitalizations')
		clean_hospital_data = self._clean_hospital_data(raw_hospital_data)

		full_dataset = self._merge_data(clean_case_data, clean_hospital_data)
		clean_full_dataset = self._clean_merged_data(full_dataset)

		self._save_clean_data(clean_full_dataset)


	def _read_and_concat_data(self, data_type):
		"""Reads and concatenates CSV files for specified data type."""
		dfs = [pd.read_csv(url, sep=';') for url in self.DATA_URLS[data_type]]

		return pd.concat(dfs, axis=0)


	def _clean_case_data(self, case_df):
		"""Cleans covid case data by aggregating municipalities that have merged."""
		old_municipalities = ['Brielle', 'Hellevoetsluis', 'Westvoorne']
		old_municipality_df = case_df[case_df['Municipality_name'].isin(old_municipalities)]

		# Aggregate data for the old municipalities and sum up relevant columns
		grouped_df = old_municipality_df.groupby([
            'Version', 'Date_of_report', 'Date_of_publication', 'Province',
            'Security_region_code', 'Security_region_name', 'Municipal_health_service',
            'ROAZ_region'
        ]).agg({'Total_reported': 'sum', 'Deceased': 'sum'}).reset_index()

		# Add municipality information to reflect merged municipality
		grouped_df['Municipality_code'] = 'GM1992'
		grouped_df['Municipality_name'] = 'Voorne aan zee'

		# Combine aggregated data with other municipalities and reset outliers in Deceased column
		full_case_df = pd.concat([case_df[~case_df['Municipality_name'].isin(old_municipalities)], grouped_df],axis=0)
		full_case_df['Deceased'] = np.where(full_case_df['Deceased'] == 9999, 0, full_case_df['Deceased'])

		return full_case_df
	

	def _clean_hospital_data(self, hospital_df):
		"""Placeholder for cleaning hospital data if required."""
		return hospital_df
	
	
	def _merge_data(self, case_df, hospital_df):
		"""Merges case and hospitalization data on relevant columns."""
		case_df.rename(columns={'Date_of_publication':'Date_of_statistics'}, inplace=True)

		full_dataset_df = pd.merge(
                case_df, 
				hospital_df[['Date_of_statistics', 'Municipality_code', 'Hospital_admission']],
                on=['Date_of_statistics', 'Municipality_code'], 
				how='left'
            )
		
		return full_dataset_df


	def _clean_merged_data(self, merged_df):
		"""Performs final cleaning on the merged dataset, including date column creation."""
		merged_df[['Province', 'Security_region_name']] = merged_df[['Province', 'Security_region_name']].replace({'Fryslân':'Friesland'})
		merged_df.drop(columns=['Version', 'Date_of_report'], inplace=True)
		merged_df['Date_of_statistics'] = pd.to_datetime(merged_df['Date_of_statistics'])

		# Add additional date-related colmuns for enhanced time-series analysis
		merged_df['Year_of_statistics'] = merged_df['Date_of_statistics'].dt.year
		merged_df['Month_of_statistics'] = merged_df['Date_of_statistics'].dt.month
		merged_df['Week_of_statistics'] = merged_df['Date_of_statistics'].dt.isocalendar().week

		# Create columns for year-month and year-week in ISO FORMAT
		merged_df['Isomonth_of_statistics'] = (
			merged_df['Year_of_statistics'].astype(str) +
			merged_df['Month_of_statistics'].astype(str).str.zfill(2) # Zero pad months for consistent format
		)
		merged_df['Isoweek_of_statistics'] = (
			merged_df['Year_of_statistics'].astype(str) +
			merged_df['Week_of_statistics'].astype(str).str.zfill(2) # Zero pad weeks for consistent format
		)
		
		merged_df['Country'] = 'Netherlands' # Add country for national data analysis

		return merged_df
	

	def _save_clean_data(self, merged_dataframe):
		"""Saves the cleaned dataset both as yearly segments and as a full dataset."""
		data_dir = Path(self.LOCAL_FOLDER)
		data_dir.mkdir(exist_ok=True)

		# Save yearly data for individual CSV files
		for year, segmented_data in merged_dataframe.groupby('Year_of_statistics'):

			segment_path = data_dir / f'covid_{year}.csv'

			segmented_data.to_csv(
				segment_path, 
				index=False,
				encoding='utf-8-sig'
			)
		
		# Save full dataset
		full_dataframe_path = data_dir / f'covid_alltime.csv'
		
		merged_dataframe.to_csv(
			full_dataframe_path,
			index=False,
			encoding='utf-8-sig'
		)
		

	def _set_unique_values(self):
		"""Sets unique values for provinces and years from the all-time data."""
		data = self.pull_data('Alltime')

		self.unique_province_values = self._get_unique_province_values(data)
		self.unique_year_values = self._get_unique_year_values(data)
	

	def _get_unique_year_values(self, data):
		"""Returns a sorted list of unique years for data selection."""
		year_list = sorted(data['Year_of_statistics'].dropna().astype(str).unique())
		year_list.insert(0, 'Alltime')

		return year_list
	

	def _get_unique_province_values(self, data):
		"""Returns a sorted list of unique provinces, including special options."""
		province_list = ['Netherlands', 'All provinces'] + sorted(data['Province'].dropna().unique().tolist())

		return province_list


	def pull_data(self, year):
		"""Loads data for specific year from saved csv file."""
		file_path = Path(self.LOCAL_FOLDER) / f'covid_{year.lower()}.csv'

		try:
			return pd.read_csv(file_path, encoding='utf-8-sig')
		except FileNotFoundError:
			print(f'No data found for year {year}')
			return pd.Dataframe()	
	

	def filter_data(self, year, province):
		"""Filters data by specified year and province."""
		df = self.pull_data(year.lower())

		if province not in ['Netherlands', 'All provinces']:
			df = df[df['Province'] == province]

		return df
	

	def aggregate_data(self, filtered_df, columns_to_aggregate, column_to_aggregate_on):
		"""Aggregates data by specified columns and calculates sum for a given column."""
		return filtered_df.groupby(column_to_aggregate_on)[columns_to_aggregate].sum().reset_index()


	def sort_data(self, aggregated_df, sort_by, sort_order):
		"""Sorts data by a specified column in ascending or descending order."""
		if sort_order == 'Ascending':
			aggregated_df.sort_values(by=sort_by, ascending=True, inplace=True)
		else:
			aggregated_df.sort_values(by=sort_by, ascending=False, inplace=True)