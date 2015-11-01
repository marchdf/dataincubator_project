Description 
=========== 
The objective of this project is to determine which rental properties need implementation of energy efficiency measures. The target audience for this project is a property management company who has many properties and tenants and pays for tenants' heating (a feature of many competitive rental markets). Energy consumption alone is not a good indicator of what properties most need energy efficiency measures. Building size, occupancy and other factors all impact energy use. Further, a year to year comparison based solely on energy consumption does not account for weather differences from one to the next. Tenant and year-to-year weather variations over the years affect the energy use of each building. 

To minimize costs, the landlord must be able to identify which buildings are inefficient while controlling for tenant and weather variations. Upon identification, the landlord can allocate resources efficiently to target the most inefficient buildings. In addition, the landlord can identify whether new tenants are using more energy than previous tenants. Once identified, the landlord could employ behavioral strategies (for example, targeted installations of wifi-enabled smart thermostats) to encourage tenants to become more energy efficient.

Current Results and Discussion
==============================
In the last 3 years, the monthly utility bill for a given rental location was approximately twice as high in the peak usage months in 2013 and 2014 compared to 2012 (see plot 1: https://github.com/marchdf/utility_analysis/blob/master/plots/utilities.png). The property management company does not know whether this is due to tenant variation, new building inefficiencies, increased gas prices, or worse weather conditions in 2013 and 2014. 

The first step to identify the issues is to account for gas rate price fluctuations. DTE Energy provides the monthly price of gas for a hundred cubic feet (ccf). The monthly gas usage can be found by dividing the utility bill by the gas rate per ccf. The monthly gas usage is a good indicator of building energy use. 

The next step is to control for weather variations as very cold winters could be driving the usage increase. While average outside temperature could be used to do this, a better measure of temperature effects on heating is the heating degree day (hdd). For each month, calculate the sum of the difference between a base temperature (usually 65F) and the average daily temperature. This measures the monthly cumulative degrees below a base temperature and is a good indicator of the severity of the cold weather. 

Plotting the gas usage as a function of heating degree days for each month and year (https://github.com/marchdf/utility_analysis/blob/master/plots/HDDvsC.png where the colors indicate different years and the numbers in the symbol correspond to the month of the year) illustrates the differences between 2012 and 2013/2014. Linear fits of the data shows the different trend among the years. At comparable heating degree day values, the gas usage for 2013/2014 was much higher than in 2012. This allows us to conclude that the weather was not the main driver for the gas usage increases observed in 2013/2014. 


Further Scope
=============
Unfortunately the data does not enable us to say whether this difference is due to tenant changes or new building inefficiencies (for example, old furnace and new building leaks). Working with property management companies for this project would allow us to control for these variables as well.

Utility bills of individual rental properties is confidential and their access is limited. In this context, I have restricted the analysis to my own property in Ann Arbor, MI. The dataset for this particular analysis is therefore small. The weather data scrapped from WeatherUnderground is larger but still just restricted to one location. This could easily be scaled to a larger area depending on the region of interest. Finally, yearly tenant variation for my residence was not available publicily.

Sources
=======
The utility rates are taken from DTE Energy's website (https://www2.dteenergy.com/wps/wcm/connect/902be969-c10b-4232-9a85-f878c8f98093/rateCard.pdf?MOD=AJPERES) and utility bills are my own. Weather data is scrapped from WeatherUnderground with the Python script.
