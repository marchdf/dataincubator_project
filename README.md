Description 
=========== 
The objective of this project is to determine which rental properties need implementation of energy efficiency measures. The target audience for this project is a property management company who has many properties and tenants and pays for tenants' heating (a feature of many competitive rental markets). Energy consumption alone is not a good indicator of what properties most need energy efficiency measures. Building size, occupancy and other factors all impact energy use. Further, a year to year comparison based solely on energy consumption does not account for weather differences from one to the next. Tenant and year-to-year weather variations over the years affect the energy use of each building. 

To minimize costs, the landlord must be able to identify which buildings are inefficient while controlling for tenant and weather variations. Upon identification, the landlord can allocate resources efficiently to target the most inefficient buildings. In addition, the landlord can identify whether new tenants are using more energy than previous tenants. Once identified, the landlord could employ behavioral strategies (for example, targeted installations of wifi-enabled smart thermostats) to encourage tenants to become more energy efficient.

Current Results and Discussion
==============================
In the last 3 years, the monthly utility bill for a given rental location was observed to be approximately twice as high in the peak usage months in 2013 and 2014 compared to 2012 (see plot 1: https://github.com/marchdf/utility_analysis/blob/master/plots/utilities.png). The property management company does not know whether this is due to tenant variation, new building inefficiencies, increased gas prices, or worse weather conditions in 2013 and 2014. 

The first step to identify the issues is to adjust the utility bill data to take into account gas rate price fluctuations. DTE provides the monthly price of gas for a hundred cubic feet (ccf). The monthly gas usage can be found by dividing the utility bill by the gas rate per ccf. The monthly gas usage is a good indicator of building energy use. 





Further Scope
=============
Utility bills of individual rental properties is confidential and their access is limited. In this context, I have restricted the analysis to my own property in Ann Arbor, MI. The dataset for this particular analysis is therefore small. The weather data scrapped from WeatherUnderground is larger but still just restricted to one location. This could easily be scaled to a larger area depending on the region of interest.

Sources
=======
The utility rates are taken from DTE Energy's website (https://www2.dteenergy.com/wps/wcm/connect/902be969-c10b-4232-9a85-f878c8f98093/rateCard.pdf?MOD=AJPERES) and utility bills are my own. Weather data is scrapped from WeatherUnderground with the Python script.
