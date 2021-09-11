SEMRinterface/resources/README.md

Author AndrewJKing.com | @AndrewsJourney
Last updated: 2021/09/10

The resources folder contains experimental structure and patient case data. See "demo_study" for an example. To create your own studies, copy, rename, and edit the contents of demo_study. 


Each "X_study" folder contains the following configuration files. 
- case_details.json defines how the cases are epoched and displayed. Each case has a list with min and max display times and the instructions for that point in time. 
- data_layout.json defines the organization of data groups on the user interface. (Also see SEMRinterface\templates\SEMRinterface\case_viewer.html).
- med_detials.json defines global details about each medication. 
- user_details.json defines the users and their case assignments. 
- variable_details.json define global details about each observation. 
- stored_results.txt is where user selections are stored. 

The "cases_all" directory contains one subdirectory for each case. The subdirectory contains the data files.
- demographics.json
- medications.json
- note_panel_data.json
- observations.json

### Note
- html ids cannot contain dashes. So if processing your own Synthea data (or any other source), make sure to relace dashes with underscores in any observation or medication keys (e.g., 8310-5 -> 8310_5)