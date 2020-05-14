# atf-preprocessor
A script for converting the different ATF flavors to eBL ATF 

This script converts .atf files which are encoded according to the oracc and c-ATF standards to the eBL-ATF standard.
* For a description of eBL-ATF see: [eBL-ATF specification](https://github.com/ElectronicBabylonianLiterature/ebl-api/blob/master/docs/ebl-atf.md)
* For a list of differences between the ATF flavors see: [eBL ATF and other ATF flavors](https://github.com/ElectronicBabylonianLiterature/generic-documentation/wiki/eBL-ATF-and-other-ATF-flavors)
# Usage
<!-- usage -->
```sh-session
$ python convert_atf.py [-h] -i INPUT [-o OUTPUT] [-t] [-v]
```
<!-- usagestop -->
- ## Command line options
  * `-h` shows help message and exits the script
  * `-i` path to the input directory (`required`)
  * `-o` path to the output directory
  * `-v` display status messages
- ## Testing

