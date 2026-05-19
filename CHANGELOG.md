# Changelog

## v2.0.3
### Fixes
 - Fixed a bug where it would download entries in the wrong folder


## v2.0.2
### Fixes
 - Fixed an issue where using an absolute path for the download location in the config file would cause the program to crash


## v2.0.1
### Fixes
 - Fixed inconsistencies in environment variable handling so the `--config` flag now works as intended


## v2.0.0
### Added 
 - Support for Mangakatana
 - Support for per site metadata style configuration
### Tweaks
 - Renamed environment variable: `inkpull_config` to `INKPULL_CONFIG`
### Fixes
 - Mangataro no longer crashes.


## v1.2.0
### Added
 - Support for Mangataro
### Fixes
 - Some typos
### Removed
 - Changing configs from the CLI, due to poor UX and error-prone. You can still open config file in a text editor with `--config` command


## v1.1.1
### Fixes
- Atsumaru metadata now properly parses the 'tags'


## v1.1.0
### Added 
 - Support for Atsumaru
### Fixes
 - In metadata parsing 'author' and 'artist' are now correct data type


## v1.0.0
### Added
 - Initial release
 - Scraping support for Toonily and WeebCentral
 - Basic CLI support