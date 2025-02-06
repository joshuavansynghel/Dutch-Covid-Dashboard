import matplotlib.pyplot as plt
from IPython.display import display

import ipywidgets as widgets

class GUI:
	"""
	A class to create and manage the graphical user interface for data visualization.
	"""

	def __init__(self, data_manager):
		"""Initialize the GUI with data manager and create necessary widgets."""
		self.data_manager = data_manager

		# Initialize plot output widget with specific dimensions
		self.plot_output = widgets.Output(layout=widgets.Layout(
			width='1600px',
			height='600px'
		))

		# Initialize GUI elements by creating widget containers
		self.plot_box = self.create_plot_box()
		self.filter_box = self.create_filter_box()
		self.y_axis_box = self.create_y_axis_box()
		self.x_axis_box = self.create_x_axis_box()
		self.order_data_box = self.create_sort_data_box()

		# Initialize plot classes
		self.bar_plot = BarPlot(self.data_manager)
		self.line_plot = LinePlot(self.data_manager)
		self.active_plot = self.bar_plot # Default to bar plot

		# Set initial widget values
		self.set_plot_widget_values(self.active_plot)

		# Set up observers for widget changes
		self.active_observers = set()
		self.setup_observers()

		# Display all GUI elements in the notebook
		display(self.plot_box, self.filter_box, self.y_axis_box, 
		  		self.x_axis_box, self.order_data_box, self.plot_output)
		
		# Show the initial plot (bar plot by default)
		self.show_bar_plot()


	def create_plot_box(self):
		"""Create a widget box containing buttons for selecting plot types."""
		plot_label = widgets.Label(value='Plot', layout=widgets.Layout(width='100px'))

		# Buttons to toggle between bar and line plot
		self.bar_plot_button = widgets.Button(
			description='bar-plot',
			disabled=False,
			tooltip='bar-plot'
		)
		self.line_plot_button = widgets.Button(
			description='line-plot',
			disabled=False,
			tooltip='line-plot'
		)

		# Event handlers for plot buttons
		self.bar_plot_button.on_click(self.show_bar_plot)
		self.line_plot_button.on_click(self.show_line_plot)

		# Arrange objects in horizontal box
		plot_box = widgets.HBox([plot_label, self.bar_plot_button, self.line_plot_button])

		return plot_box
	
	def create_filter_box(self):
		"""Create a widget box containing filters for selecting years and province."""
		filter_label = widgets.Label(value='Filter', layout=widgets.Layout(width='100px'))

		# Dropdown menus for filtering by year and province
		self.year_dropdown = widgets.Dropdown(
			options=self.data_manager.unique_year_values,
			value='Alltime',
			description='Year'
		)
		self.province_dropdown = widgets.Dropdown(
			options=self.data_manager.unique_province_values,
			value='Netherlands',
			description='Province'
		)

		# Arrange objects in horizontal box
		filter_box = widgets.HBox([filter_label, self.year_dropdown, self.province_dropdown])

		return filter_box
	
	def create_y_axis_box(self):
		"""Create a widget box for selecting metrics to display on the Y-axis."""
		y_axis_label = widgets.Label(value='Y-Axis', layout=widgets.Layout(width='100px'))
		
		# Checkboxes for selecting Y-axis metrics
		self.total_reported_check = widgets.Checkbox(
			value=True,
			description='Total_reported'
		)
		self.hospital_admission_check = widgets.Checkbox(
			value=True,
			description='Hospital_admission'
		)
		self.deceased_check = widgets.Checkbox(
			value=True,
			description='Deceased'
		)

		# Arrange objects in horizontal box
		y_axis_box = widgets.HBox([y_axis_label, self.total_reported_check, 
							 		self.hospital_admission_check, self.deceased_check])
		
		return y_axis_box
	
	def create_x_axis_box(self):
		"""Create a widget box for selecting X-axis options such as municipality and date format."""
		x_axis_label = widgets.Label(value='X-axis', layout=widgets.Layout(width='100px'))

		# Checkboxes and dropdown for X-axis options
		self.municipality_check = widgets.Checkbox(
			value=False,
			description='Muncipalities'
		)
		self.month_check = widgets.Checkbox(
			value=False,
			description='Months'
		)
		self.date_format_dropdown = widgets.Dropdown(
			options=['Date_of_statistics', 'Isoweek_of_statistics', 'Isomonth_of_statistics'],
			value='Date_of_statistics',
			description='Date Format'
		)

		# Arrange objects in horizontal box
		x_axis_box = widgets.HBox([x_axis_label, self.municipality_check, self.month_check, self.date_format_dropdown])

		return x_axis_box
	
	def create_sort_data_box(self):
		"""Create a widget box for data sorting options."""
		sort_label = widgets.Label(value='Order by', layout=widgets.Layout(width='100px'))

		# Dropdown and checkbox for sort options
		self.sort_by_dropdown = widgets.Dropdown(
			options=['Total_reported', 'Hospital_admission', 'Deceased'],
			value='Total_reported',
			description='Sort by'
		)
		self.sort_order_dropdown = widgets.Dropdown(
			options=['Ascending', 'Descending'],
			value='Ascending',
			description='Sort order'
		)
		self.sort_data_check = widgets.Checkbox(
			value=False,
			description='sort'
		)

		# Arrange objects in horizontal box
		order_box = widgets.HBox([sort_label, self.sort_by_dropdown, self.sort_order_dropdown, self.sort_data_check])

		return order_box
		

	def show_bar_plot(self, *args):
		"""Display the bar plot and adjust the GUI state accordingly."""
		self.active_plot = self.bar_plot

		self.deactivate_line_plot_state_checks()
		self.activate_bar_plot_state_checks()

		self.adjust_layout_for_bar_plot()

		with self.plot_output:
			display(self.active_plot.plot())

	def show_line_plot(self, *args):
		"""Display the line plot and adjust the GUI state accordingly."""
		self.active_plot = self.line_plot

		self.deactivate_bar_plot_state_checks()
		self.activate_line_plot_state_checks()

		self.adjust_layout_for_line_plot()

		with self.plot_output:
			display(self.active_plot.plot())

	def adjust_layout_for_bar_plot(self):
		"""Configure widget display settings for bar plot."""
		# Hide widgets irrelevant for bar plot
		self.date_format_dropdown.layout.display = 'none'

		# Display widgets relevant for bar plot
		self.municipality_check.layout.display = 'block'
		self.month_check.layout.display = 'block'
		self.sort_by_dropdown.layout.display = 'block'
		self.sort_order_dropdown.layout.display = 'block'
		self.sort_data_check.layout.display = 'block'

	def adjust_layout_for_line_plot(self):
		"""Configure widget display settings for line plot."""
		# Hide widgets irrelevant for line plot
		self.municipality_check.layout.display = 'none'
		self.month_check.layout.display = 'none'
		self.sort_by_dropdown.layout.display = 'none'
		self.sort_order_dropdown.layout.display = 'none'
		self.sort_data_check.layout.display = 'none'

		# Display widgets relevant for line plot
		self.date_format_dropdown.display = 'block'

	def activate_bar_plot_state_checks(self):
		"""Enable observers for bar plot widgets."""
		# Attach observers for bar plot-specific widgets
		self.province_dropdown.observe(self.update_bar_municipality_checkbox_state, names='value')
		self.month_check.observe(self.update_bar_municipality_checkbox_state, names='value')
		self.month_check.observe(self.update_bar_municipality_month_checkbox_state, names='value')
		self.municipality_check.observe(self.update_bar_municipality_month_checkbox_state, names='value')
		self.month_check.observe(self.update_bar_sort_data_checkbox_state, names='value')

		# Track active observers
		self.active_observers.add('bar_municipality_check_province')
		self.active_observers.add('bar_municipality_check_month')
		self.active_observers.add('bar_municipality_month_check_month')
		self.active_observers.add('bar_municipality_month_check_municipality')
		self.active_observers.add('bar_sort_data_check_month')

	
	def deactivate_bar_plot_state_checks(self):
		"""Disable observers for bar plot widgets."""
		# remove observers if active
		if 'bar_municipality_check_province' in self.active_observers:
			self.province_dropdown.unobserve(self.update_bar_municipality_checkbox_state, names='value')
			self.active_observers.remove('bar_municipality_check_province')

		if 'bar_municipality_check_month' in self.active_observers:
			self.month_check.unobserve(self.update_bar_municipality_checkbox_state, names='value')
			self.active_observers.remove('bar_municipality_check_month')
		
		if 'bar_municipality_month_check_month' in self.active_observers:
			self.month_check.unobserve(self.update_bar_municipality_month_checkbox_state, names='value')
			self.active_observers.remove('bar_municipality_month_check_month')

		if 'bar_municipality_month_check_municipality' in self.active_observers:
			self.municipality_check.unobserve(self.update_bar_municipality_month_checkbox_state, names='value')
			self.active_observers.remove('bar_municipality_month_check_municipality')

		if 'bar_sort_data_check_month' in self.active_observers:
			self.month_check.unobserve(self.update_bar_sort_data_checkbox_state, names='value')
			self.active_observers.remove('bar_sort_data_check_month')
	
	def update_bar_municipality_checkbox_state(self, change):
		"""Update the municipality checkbox state based on the selected province."""
		if self.province_dropdown.value in ['Netherlands', 'All provinces']:
			self.municipality_check.value = False
			self.municipality_check.disabled = True
		else:
			self.municipality_check.disabled = False
	
	def update_bar_month_checkbox_state(self, change):
		"""Update the month checkbox state based on the selected province."""
		if self.province_dropdown.value == 'All provinces':
			self.month_check.value = False
			self.month_check.disabled = True
		else:
			self.month_check.disabled = False

	def update_bar_municipality_month_checkbox_state(self, change):
		"""Update municipality and month checkbox states based on user interactions."""
		if change['new']:
			if change['owner'] == self.municipality_check:
				self.month_check.value = False
			elif change['owner'] == self.month_check:
				self.municipality_check.value = False
	
	def update_bar_sort_data_checkbox_state(self, change):
		"""Update the sort data checkbox state based on the month checkbox state."""
		if self.month_check.value == True:
			self.sort_data_check.value = False
			self.sort_data_check.disabled = True
		else:
			self.sort_data_check.disabled = False
	

	def activate_line_plot_state_checks(self):
		"""Enable observers for line plot widgets."""
		# Attach observers for line plot-specific widgets
		self.total_reported_check.observe(self.update_line_selected_metric_checkbox_state, names='value')
		self.hospital_admission_check.observe(self.update_line_selected_metric_checkbox_state, names='value')
		self.deceased_check.observe(self.update_line_selected_metric_checkbox_state, names='value')

		# Track active observers
		self.active_observers.add('line_selected_metric_check_total_reported')
		self.active_observers.add('line_selected_metric_check_hospital_admission')
		self.active_observers.add('line_selected_metric_check_deceased')


	def deactivate_line_plot_state_checks(self):
		"""Disable observers for bar plot widgets."""
		# Remove observers if active
		if 'line_selected_metric_check_total_reported' in self.active_observers:
			self.total_reported_check.unobserve(self.update_line_selected_metric_checkbox_state, names='value')
			self.active_observers.remove('line_selected_metric_check_total_reported')

		if 'line_selected_metric_check_hospital_admission' in self.active_observers:
			self.hospital_admission_check.unobserve(self.update_line_selected_metric_checkbox_state, names='value')
			self.active_observers.remove('line_selected_metric_check_hospital_admission')

		if 'line_selected_metric_check_deceased' in self.active_observers:
			self.deceased_check.unobserve(self.update_line_selected_metric_checkbox_state, names='value')
			self.active_observers.remove('line_selected_metric_check_deceased')


	def update_line_selected_metric_checkbox_state(self, change):
		"""Update line plot metric checkbox states to ensure only one metric is selected."""
		if self.total_reported_check.value == True:
			self.hospital_admission_check.value = False
			self.deceased_check.value = False

		elif self.hospital_admission_check.value == True:
			self.total_reported_check.value = False
			self.deceased_check.value = False
		
		elif self.deceased_check.value == True:
			self.total_reported_check.value = False
			self.hospital_admission_check.value = False


	def setup_observers(self):
		"""Setup observers to refresh plots upon widget value changes."""
		self.year_dropdown.observe(lambda change: self.update_plot(change), names='value')
		self.province_dropdown.observe(lambda change: self.update_plot(change), names='value')
		self.total_reported_check.observe(lambda change: self.update_plot(change), names='value')
		self.hospital_admission_check.observe(lambda change: self.update_plot(change), names='value')
		self.deceased_check.observe(lambda change: self.update_plot(change), names='value')
		self.municipality_check.observe(lambda change: self.update_plot(change), names='value')
		self.month_check.observe(lambda change: self.update_plot(change), names='value')
		self.sort_by_dropdown.observe(lambda change: self.update_plot(change), names='value')
		self.sort_order_dropdown.observe(lambda change: self.update_plot(change), names='value')
		self.sort_data_check.observe(lambda change: self.update_plot(change), names='value')


	def update_plot(self, change):
		"""Refresh the active plot based on the widget values."""
		self.set_plot_widget_values(self.active_plot)
		with self.plot_output:
			self.plot_output.clear_output(wait=True)
			display(self.active_plot.plot())


	def set_plot_widget_values(self, active_plot):
		"""Set widget values for the active plot based on current GUI selections."""
		active_plot.widget_values = {
            "year": self.year_dropdown.value,
            "province": self.province_dropdown.value,
            "total_reported": self.total_reported_check.value,
            "hospital_admission": self.hospital_admission_check.value,
            "deceased": self.deceased_check.value,
            "municipality": self.municipality_check.value,
            "month": self.month_check.value,
            "sort_by": self.sort_by_dropdown.value,
            "sort_order": self.sort_order_dropdown.value,
            "sort_data": self.sort_data_check.value,
			"date_format": self.date_format_dropdown.value,
        }

	
class PlotTemplate:
	"""
	Abstract class for creating plots based on data from the DataManager.
	Handles data retrieval, filtering, aggregation and sorting.
	"""
	
	def __init__(self, data_manager):
		"""Initialize the PlotTemplate with a DataManager instance."""
		self.data_manager = data_manager
		self.widget_values = {}


	def pull_and_filter_data(self):
		"""Retrieve and filter data based on the current widget selections."""
		year = self.widget_values['year']
		province = self.widget_values['province']

		return self.data_manager.filter_data(year, province)
	

	def aggregate_data(self, filtered_df, metrics_to_aggregate):
		"""Aggregate data based on selected metrics and current widget values."""
		province = self.widget_values['province']
		municipality = self.widget_values['municipality']
		month = self.widget_values['month']
		date_format = self.widget_values['date_format']

		# Determine aggregation level based on widget selections
		if province == 'Netherlands' and month == False:
			aggregated_df = self.data_manager.aggregate_data(filtered_df, metrics_to_aggregate, 'Country')
		elif municipality:
			aggregated_df = self.data_manager.aggregate_data(filtered_df, metrics_to_aggregate, 'Municipality_name')
		elif month: 
			aggregated_df = self.data_manager.aggregate_data(filtered_df, metrics_to_aggregate, 'Month_of_statistics')
		else:
			aggregated_df = self.data_manager.aggregate_data(filtered_df, metrics_to_aggregate, 'Province')
		
		return aggregated_df
	
	def sort_data(self, aggregated_df):
		"""Sort the aggregated data based on current sorting widget values."""
		sort_by = self.widget_values['sort_by']
		sort_order = self.widget_values['sort_order']

		# Sort data based on user-defined criteria
		self.data_manager.sort_data(aggregated_df, sort_by, sort_order)


	def plot(self):
		"""Abstract method to plot data. Must be implemented by subclasses."""
		raise NotImplementedError("Subclass must implement abstract method")
	
class BarPlot(PlotTemplate):
	"""
	Bar plot class for visualizing aggregated data.
	"""

	def __init__(self, data_manager):
		"""Initialize BarPlot with the given DataManager instance."""
		super().__init__(data_manager)

	def plot(self):
		"""
		Create and display a bar plot based on current widget values.
		Filters, aggregates and sorts data before plotting.
		"""
		data = self.pull_and_filter_data()

		# Collect selected metrics to be visualized
		selected_metrics = []

		if self.widget_values['total_reported']:
			selected_metrics.append('Total_reported')

		if self.widget_values['hospital_admission']:
			selected_metrics.append('Hospital_admission')

		if self.widget_values['deceased']:
			selected_metrics.append('Deceased')

		if not selected_metrics:
			return # Exit function when no metrics were selected

		# Define colors for each metric
		metric_colors = {
			'Total_reported': 'blue',
			'Hospital_admission': 'orange',
			'Deceased': 'green'
		}

		column_colors = [metric_colors[metric] for metric in selected_metrics]

		# Aggregate data for the plot
		aggregated_data = self.aggregate_data(data, selected_metrics)

		# Determine x-axis and title based on data structure
		if 'Province' in aggregated_data.columns:
			x_column = 'Province'
			title_suffix = f"for {self.widget_values['province']} {self.widget_values['year'].lower()}"

		elif 'Municipality_name' in aggregated_data.columns:
			x_column = 'Municipality_name'
			title_suffix = f"for municipalities in {self.widget_values['province']} {self.widget_values['year'].lower()}"

		elif 'Month_of_statistics' in aggregated_data.columns:
			x_column = 'Month_of_statistics'
			title_suffix = f"for each month {self.widget_values['year'].lower()}"

			aggregated_data['Month_of_statistics'] = aggregated_data['Month_of_statistics'].map(self.month_mapping)

		elif 'Country' in aggregated_data.columns:
			x_column = 'Country'
			title_suffix = f"for {self.widget_values['province']} {self.widget_values['year'].lower()}"

		# Sort data if applicable
		if self.widget_values['sort_data'] and self.widget_values['sort_by'] in selected_metrics:
			self.sort_data(aggregated_data)
		
		# Plot data from dataframe
		ax = aggregated_data.plot(
			kind='bar',
			x=x_column,
			y=selected_metrics,
			width=0.4,
			color=column_colors,
			stacked=False,
			figsize=(10, 5)
		)

		# Customize plot elements
		ax.set_title(f"Total reported data {title_suffix}")
		ax.set_ylabel("Count")
		ax.legend(title="Categories", loc='upper right')
		ax.yaxis.get_major_formatter().set_scientific(False)

		plt.show()

	def month_mapping(self, month_number):
		"""Map month number to month name."""
		month_dict = {
			1: "January",
			2: "February",
			3: "March",
			4: "April",
			5: "May",
			6: "June",
			7: "July",
			8: "August",
			9: "September",
			10: "October",
			11: "November",
			12: "December"
		}

		return month_dict.get(month_number, "Invalid Month")

		
class LinePlot(PlotTemplate):
	"""
	Line plot class for visualizing aggregated data.
	"""

	def __init__(self, data_manager):
		"""Initialize LinePlot with the given DataManager instance."""
		super().__init__(data_manager)

	def plot(self):
		"""
		Create and display a line plot based on the current widget values.
		Filters, aggregates and visualizes data with a line plot.
		"""
		data = self.pull_and_filter_data()

		selected_metric = []

		# Collect selected metric
		if self.widget_values['total_reported']:
			selected_metric.append('Total_reported')
		elif self.widget_values['hospital_admission']:
			selected_metric.append('Hospital_admission')
		elif self.widget_values['deceased']:
			selected_metric.append('Deceased')

		if not selected_metric:
			return # Exit function if no metrics were selected
		
		# Aggregate data for the plot
		aggregated_data = self.aggregate_data(data, selected_metric)
		
		# Plot data from Dataframe
		ax = aggregated_data.plot(
			kind='line',
			x='Metric',
			y=selected_metric,
			width=0.4,
			color='blue',
			stacked=False,
			figsize=(10, 5)
		)

		# Customize plot elements
		ax.set_title(f"""{selected_metric} for {self.widget_values['province']} {self.widget_values['year']} """)
		ax.set_ylabel("Count")
		ax.legend(title="Categories", loc='upper right')
		ax.yaxis.get_major_formatter().set_scientific(False)

		plt.show()