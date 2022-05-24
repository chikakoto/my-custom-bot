# DSE I2400 Data Engineering: Infrastructure and Applications

Project: My Custom Search Bot


<!-- GETTING STARTED -->
## Getting Started

This is an example of how you set up this project locally.

To get this script up and running, please follow the following steps.

### Prerequisites

You need a web environment and python to run this project. 
* MAMP / XAMPP based on your OS 
* Python 3.7

### Installation

Here is the instraction how to set up this web application. 

1. Clone this repo

2. Copy the files under the htdocs folder at MAMP / XAMPP directory

3. Run Project2-DDL.sql on MySQL 
 
4. Install following python package 
   ```sh
   pip install beautifulsoup4
   ```
   For OCR
   ```sh
   pip install pytesseract
   ```
   ```sh
   pip install --ignore-installed Pillow==9.0.0
   ```
   ```sh
   pip install pdf2image
   ```
   ```sh
   pip install PyPDF2
   ```
   
5. Install OCR Engine and PDF rendering library

   The following commands are for Linux/Mac environment. If you are using Windows, please find out relevant command for your environment. 
   ```sh
   sudo apt install tesseract-ocr
   ```
   ```sh
   apt-get install poppler-utils
   ```
   
   If you are using Homebrew, use following commands. 
   ```sh
   brew install tesseract
   ```
   ```sh
   brew install poppler
   ```
   
6. Create your apache environment file
   
   6.1 Copy "envvars_" file and name it "envvars" in the Library/bin folder under MAMP/XAMP directory.
   
   6.2 Add following PATH to envvars file

    PATH="/usr/local/bin/:/usr/local/Cellar/tesseract/4.1.1/bin:usr/local/Cellar/poppler/21.08.0/bin"
    
    export PATH
    
    The tesseract and poppler destination will be different based on your environment. 

7. Restart MAMP/XAMPP

<p align="right">(<a href="#top">back to top</a>)</p>
