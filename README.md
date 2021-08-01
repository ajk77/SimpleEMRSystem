# Simple EMR System

This code can be used for Electronic Medical Record Research.

## Getting Started

First, have a look in the screenshots directory to become familiar with the interface design. 

### Prerequisites

Python 3 or Docker Compose

### Installing


#### Python 

1. Clone repository
2. cd into project directory
3. enter "pip install -r requirements.txt"

#### Docker

1. Clone repository 

#### Python installation notes
It is strongly recommended that you use a virtual environment.
1. if you do not have virtualenv, enter "pip install virtualenv"
2. enter "python -m venv __name_of_environment__"
3. enter "__name_of_environment__/Scripts/activate"
4. then follow the Python installation instructions shown above
5. to terminate the virtual environment, enter "deactivate"

### Deployment

##### Python 

1. cd into project directory
2. enter "python manage.py runserver"
3. open web browser to http://127.0.0.1:8000/SEMRinterface/
4. terminate using ctrl+c

#### Docker
1. cd into project directory 
2. enter "docker-compose up"
3. open web browser to http://127.0.0.1:8000/SEMRinterface/
4. terminate using ctrl+c

### Notes

The SEMRinterface in meant to run in full screen mode on a 1920 x 1080 resolution monitor. Responsive html is not
currently supported. 

## Secondary Use

### Included data
Two example studies are included in the Simple EMR System repository: demo_study and synthea_study. Demo_study includes three synthetic patient cases created by scrambling the contents of de-identified records from a larger set of patients from a hospital’s Cerner EMR system. Synthea_study includes 25 intensive care unit (ICU) encounters from the Synthea COVID-19 dataset (available at https://synthea.mitre.org/downloads).

Included case data can be found at:
1. https://github.com/ajk77/SimpleEMRSystem/tree/master/resources/synthea_study
2. https://github.com/ajk77/SimpleEMRSystem/tree/master/resources/demo_study (update coming soon)

### Importing custom patient data
To preprocess Synthea cases for display on the Simple EMR System: 
1. Download the source data and extract it into the ‘resources’ folder. 
2. Adjust parameters, such as the input and output directories, in the Synthea data loading script (‘loaddata_synthea.py’) and execute the script. 
3. View details about each processed case in ‘list_case_dicts.json’. 
4. Select cases to use in the study and add them to ‘case_details.json’ 
5. assign them to users in ‘user_details.json’. 
6. adjust display groups, medication routes, display names, and display locations in ‘variable_details.json,’ ‘med_details.json,’ and ‘data_layout.json.’ 

To load in data from other sources, you will need to create a custom 'loaddata' file. If your data source is a database, consider usings Django's Models.py (https://docs.djangoproject.com/en/3.1/topics/db/models/). 

You may also edit JSON file directly in order to create custom cases.

### Eye-tracking research
Components related to eye-tracking are turned off in this version because accuracy across different environments can 
not be guaranteed. If you are interested in using SEMRinterface with a remote eye-tracking device, please see the
following:
* EyeBrowserPy (<https://github.com/ajk77/EyeBrowserPy>)
* Leveraging Eye Tracking to Prioritize Relevant Medical Record Data: Comparative Machine Learning Study 
(<https://www.jmir.org/2020/4/e15876/>)
* Eye-tracking for clinical decision support: A method to capture automatically what physicians are viewing in 
the EMR (<https://www.ncbi.nlm.nih.gov/pubmed/28815151>)

## Versioning

Version 3.0. For the versions available, see https://github.com/ajk77/SimpleEMRSystem

## Authors

* Andrew J King - Doctoral Candidate (at time of creation)
	* Website (https://www.andrewjking.com/)
	* Twitter (https://twitter.com/andrewsjourney)
* Shyam Visweswaran - Principal Investigator
	* Website (http://www.thevislab.com/)
	* Twitter (https://twitter.com/Shyam_Vis)
* Gregory F Cooper - Doctoral Advisor

##Citation
King AJ, Calzoni L, Tajgardoon M, Cooper G, Clermont G, Hochheiser H, Visweswaran S. A simple electronic medical record system designed for research. JAMIA Open. 2021 July 31;4(3):ooab040.
(<https://academic.oup.com/jamiaopen/article/4/3/ooab040/6332673>)

## Impact
This interface has been used in the following studies:
* King AJ, Cooper GF, Clermont G, Hochheiser H, Hauskrecht M, Sittig DF, Visweswaran S. Leveraging Eye Tracking to 
Prioritize Relevant Medical Record Data: Comparative Machine Learning Study. J Med Internet Res 2020;22(4):e15876. 
(<https://www.jmir.org/2020/4/e15876/>)
* King AJ, Cooper GF, Clermont G, Hochheiser H, Hauskrecht M, Sittig DF, Visweswaran S. Using Machine Learning to 
Selectively Highlight Patient Information. J Biomed Inform. 2019 Dec 1;100:103327. 
(<https://www.sciencedirect.com/science/article/pii/S1532046419302461>)
* King AJ, Cooper GF, Hochheiser H, Clermont G, Hauskrecht M, Visweswaran S. Using machine learning to predict 
the information seeking behavior of clinicians using an electronic medical record system. AMIA Annu Symp Proc. 
2018 Nov 3-7; San Francisco, California p 673-682. [Distinguished Paper Nomination] 
(<https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6371238/>)
* King AJ, Hochheiser H, Visweswaran S, Clermont G, Cooper GF. Eye-tracking for clinical decision support: 
A method to capture automatically what physicians are viewing in the EMR. AMIA Joint Summits. 2017 Mar 27-30; 
San Francisco, California p 512-521. [Best Student Paper] (<https://www.ncbi.nlm.nih.gov/pubmed/28815151>)
* King AJ, Cooper GF, Hochheiser H, Clermont G, Visweswaran S. Development and preliminary evaluation of a 
prototype of a learning electronic medical record system. AMIA Annu Symp Proc. 2015 Nov 14-18; San Francisco, 
California p.1967-1975. [Best Student Paper] (<https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4765593/>)

## License

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

## Acknowledgments

* Harry Hochheiser
	* Twitter (https://twitter.com/hshoch)
* Gilles Clermont
* Milos Hauskrecht 
