# Achilles Web - EMIF Catalogue Fingerpint Plugin

[Achilles Web](https://github.com/OHDSI/AchillesWeb) is an interactive web site for reviewing the results of the [Achilles R package](https://github.com/OHDSI/Achilles)

![Example](https://raw.githubusercontent.com/bioinformatics-ua/catalogue/new/achilles/emif/achilles/static/achilles/images/achilles_example.png)

## Integration on the Catalogue

This django application provides support for the fingerprint plugin of the same name (available to developers - see more information on the deployed catalogue developer section ).

## Features

* Support for **external data** via datasource URL
* Suport for **ZIP upload**

#### External URL

URL must provide a valid JSON object with the default structure. (As specified in [Achilles Web Documentation](https://github.com/OHDSI/AchillesWeb)

Report REST API must be implemented, mantained and served by Data Owners.
Data Owners must allow Cross Site Requests made by ` http://yoursite.url`

No report URL are ever made available to clients. Hiding data provider API.

Datasource URL should return a JSON object with the following structure:

![Datasource Structure](https://raw.githubusercontent.com/bioinformatics-ua/catalogue/new/achilles/emif/achilles/static/achilles/images/achilles_datasource_structure.png)


### ZIP Upload

Run [OHDSI's Achilles R-program](https://github.com/OHDSI/Achilles) on your data
Run:

      exportToJson(connectionDetails,"CDM_SCHEMA", "RESULTS_SCHEMA", "&lt;some_folder&gt;/reports")

Zip the resulting folder (be sure to maintain the folder structure inside the zip archive - see image for more details)

Upload it to our server

**The resulting zip file _MUST_ contain a folder named 'reports' with all report data following the structure shown in the image, otherwise it won't work**

![Zip Structure](https://raw.githubusercontent.com/bioinformatics-ua/catalogue/new/achilles/emif/achilles/static/achilles/images/achilles_zip_structure.png)
