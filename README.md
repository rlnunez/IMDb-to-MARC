# IMDb to MARC

This is a python script that will convert IMDb information in to a MARC file. If also provided with an OCLC ID, the script will also grab information from OCLC regarding the title.

## Getting Started

Call the script using command line arguments: 

Command | Description | Required
------------ | ------------- | -------------
-f or --File | Path to the CSV file | Required if not provided with an IMDb ID and UPC
-o or --OCLC | OCLC Number | 
-i or --IMDB | IMDB ID | Required if --file or -f is not provided
-u or --UPC | Item's UPC | Required if --file or -f is not provided
-p or --Price | Item's Price | 
-s or --Season | The season number (if a TV Show is given) [default: 1] | 
-q or --Quiet | Will suppress the script's output | 

### CSV File format:
**Note:** Heading order does not matter

OCLC | IMDB | Price | UPC | Season
------------ | ------------- | ------------- | ------------- | -------------
988741899 | tt5897948 | $19.99 | 888295556514 | 
988741899 | 5897948 |  | 888295556514 | 



### Prerequisites

* Python 2.7.x
* pip install imdbpy
* pip install pymarc
* pip install csv
* pip install unidecode
* pip install requests
* pip install lxml
* pip install rdflib
* pip install argparse
* pip install inflect

## Development TODO

- [x] Commandline support
- [x] Better batch generation support (read CSV file with headings)
- [ ] Support for other item types
- [ ] Integrate with LC Subject Headings and Name Authority
- [ ] GUI
- [ ] Boatloads of code cleanup

## Contributing

Looking for people to help improve the code when possible.


## Authors

* **Rob Nunez** - *Initial work* - [rlnunez](https://github.com/rlnunez)

See also the list of [contributors](https://github.com/rlnunez/IMDb-to-MARC/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* [IMDbpy](https://github.com/alberanid/imdbpy)
* [pyMARC](https://github.com/edsu/pymarc)
