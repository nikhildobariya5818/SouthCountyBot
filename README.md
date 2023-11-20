***South Florida Records Pull Program***

**Introduction**

This Python program is designed to fetch public records from Miami-Dade and Broward counties in South Florida. It provides a comprehensive set of functionalities to extract various types of public records available online.

**Installation**

Prerequisites
Python 3.x: If not installed, download and install Python from Python's official website.
Dependencies: Install required libraries using the following command:


```bash 
   pip install pandas apscheduler
``` 
[additional_libraries]

**Additional Libraries:**

Some functionalities require additional libraries depending on the specific extraction requirements.

**Usage**

1. **Clone the Repository**: Use git clone <repository-url> to get the code on your local machine.

2. **Install Dependencies**: Ensure the required dependencies are installed.

3. **Run the Program**: Execute the CountyMenu() function in the Python file to initiate the program.


**Features**
Miami-Dade County Menu

 **Record Options:**
- Lis Pendens, Death Certificates, Probates, Code Violations, Public unpaid accounts, and more.
**Address Extraction:**
- Ability to extract addresses from custom files based on Folio, Address, or Owner details.
**Special Functionality:**
- Includes a feature called 'realforeclose'.

Broward County Menu

**Record Extraction:**
- Functionalities for Lis Pendens, Death Certificates, Probates, and Property Tax Liens.
**Address Extraction:**
- Similar address extraction functionalities for custom files.

Scheduled Runs

**Automated Runs:**
- Schedule specific times for automated record extraction.


**File Structure**
**Input/:** Place input files for address extraction in this directory.
**Output/:** Extracted records will be saved in this directory.
**TaxDelinquent/:** Reserved for tax delinquent files.


**Instructions**
- Input Requirements: Ensure to input necessary information when prompted, such as file names, date ranges, etc.
- Error Handling: Most functionalities have error handling implemented.
