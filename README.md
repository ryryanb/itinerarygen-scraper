# itinerarygen-scraper
Scrape data for itinerary generator system using Python. Budget hostels and attractions/"things to do" data are gathered and saved in database for later use.

Python version used: 3.9.1

Modules to be installed:
beautifulsoup4==4.9.3
bs4==0.0.1
lxml==4.6.2
PyMySQL==0.10.1
regex==2020.11.13
requests==2.25.1
urllib3==1.26.2

Instructions:
1. Create database tables by running sql script, "itinerarygen.sql"
2. Gather the links for Tripadvisor destinations by running "scrapeTARegions.py"
   Example of links gathered would be:
        https://www.tripadvisor.com.ph/Hotels-g150800-Mexico_City_Central_Mexico_and_Gulf_Coast-Hotels.html
        https://www.tripadvisor.com.ph/Hotels-g186338-London_England-Hotels.html
3. Run "scrapeTAdestinations.py" to visit destination/city links for "Things to Do" and gather all the popular sites and activities for each destination.
4. "scrapeTAattractiondetails.py" is run to gather the details for each found attraction/"things to do". Details include name, coordinates, city, country, number of reviews, rating
5. Run "scrapeHW.py" to gather budget hostel data from Hostelworld.

The scraped data will be used in itinerarygen system which suggests itineraries based on given user parameters. System is being refactored and will be posted in a separate repository.
   


