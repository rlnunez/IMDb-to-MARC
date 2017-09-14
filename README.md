# IMDb to MARC

This is a python script that will convert IMDb information in to a MARC file. If also provided with an OCLC ID, the script will also grab information from OCLC regarding the title.

## Getting Started

Use the videos.txt file to enter the IMDb ID (REQ), OCLC ID (OPT), UPC (REC), PRICE (OPT), and TV Season (OPT). The format should be:

IMDbID|OCLC,UPC,$PRICE,1

### Prerequisites

* Python 2.7.x
* pip install imdbpy
* pip install pymarc
* pip install csv
* pip install unidecode
* pip install requests
* pip install lxml
* pip install rdflib

## Deployment

It's taken a while for the code to get this far. There is still a bit of work that needs to be done to split it into more reasonable and reusable chunks. 

## Contributing

Looking for people to help improve the code when possible


## Authors

* **Rob Nunez** - *Initial work* - [rlnunez](https://github.com/rlnunez)

See also the list of [contributors](https://github.com/rlnunez/IMDb-to-MARC/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* [IMDbpy](https://github.com/alberanid/imdbpy)
* [pyMARC](https://github.com/edsu/pymarc)
