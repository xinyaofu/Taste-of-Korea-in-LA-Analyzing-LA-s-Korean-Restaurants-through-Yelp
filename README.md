# Taste of Korea in LA: Analyzing LA’s Korean Restaurants through Yelp

## Name of the Project
Taste of Korea in LA: Analyzing LA’s Korean Restaurants through Yelp

## Created by
Xinyao Fu 

## Instructions to create a conda enviornment
This project was developed using PyCharm with a Conda Python 3.11 interpreter. Follow these steps to set up a similar environment.

### Step 1: Install Anaconda
If you haven't already, install anaconda from https://www.anaconda.com/download

### Step 2: Clone the Repository
Clone this repository to your device, you can run: <br>
git clone https://github.com/USC-DSCI-510/final-project-xinyaofu.git <br> 
cd final-project-xinyaofu

### Step 3: Create the Conda Environment
Create a new Conda environment with Python 3.11, you can run: <br>  
conda create -n [environment_name] python=3.11 <br>  
Replace '[environment_name]' with your desired environment name.

### Step 4: Activate the Created Environment
Activate the environmemt you just created, you can run: <br>  
conda activate [environment_name]

### Step 5: Set Up Pycharm
Open PyCharm and configure it to use the Conda environment you just created.

1. Open your project in PyCharm.
2. Go to `File > Settings > Project: final-project-xinyaofu > Python Interpreter`.
3. Click on the gear icon, select `Add interpreter`, and choose 'Conda Environment'.
4. Select 'Existing environment' and browse to the Conda environment path.
5. Apply the changes and close the settings.

You can also add the interpreter by clicking the python interpreter button in the lower right corner of the PyCharm interface. 

### Step 6: Run the Project
Now you can run the project using Pycharm. 

## Instructions on how to install the required libraries
The file requirements.text lists all the external libraries this project has used. <br>
To install all the required libraries, you can run: <br>  
pip install -r requirements.txt

## Instructions on how to download the data
There are two python files to get the data. Due to Yelp's limit on daily API calls, run get_data.py first, after 24 hours, run get_data_2.py, and after another 24 hours, run get_data_2.py again to get the full raw data. The data will be stored in a database file named restaurants_data.db.

## Instructions on how to clean the data
Run clean_data.py to clean the data. The cleaned data will be stored in a database file named cleaned_data.db

## Instrucions on how to run analysis code
Run run_analysis.py to run the analysis code. The codes includes a sentiment analysis, an outliers analysis, a text analysis and a price analysis, and all analysis results can be seen by running the codes. The results of text analysis will also be stored in a database file named data_analysis.db.

## Instructions on how to create visualizations
Run visualization_results.py to create visualizations. The created visualizations can be found in the results dictionary. 
