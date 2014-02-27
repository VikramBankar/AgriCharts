__author__ = 'Vikram Bankar'
import AgriCharts

A = AgriCharts.AgriCharts()
if A.production:
    A.collect_data()
else:
    A.extract_html()