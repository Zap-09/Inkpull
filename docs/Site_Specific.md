## Table of Contents

- [Supported sites](#supported-sites)
- [Flags and site details](#flags-and-site-details)

## Supported sites

- [Toonily](#toonily) (toonily.com)
- [Weebcentral](#weebcentral) (weebcentral.com)
- [Atsumaru](#atsumaru) (atsu.moe)

## Flags and site details

- ### Toonily
    - Requirements
        - None
    - Available flags `-s` and `-c`
        - use `-s` when you want to download the whole series
        - use `-c` when you just want one chapter
    - Examples:
        - `inkpul toonily -s <series url>`
        - `inkpul toonily -c <chapter url>`

- ### Weebcentral
    - Requirements
        - None
    - Available flags `-s` and `-c`
        - use `-s` when you want to download the whole series
        - use `-c` when you just want one chapter
    - Examples:
        - `inkpul weebcentral -s <series url>`
        - `inkpul weebcentral -c <chapter url>`

- ### Atsumaru
    - Requirements
        - None
    - Available flags `-s`, `-c`, `-g`
        - use `-s` when you want to download the whole series
        - use `-c` when you want just one chapter
        - use `-g` pick the scanlation group when downloading a series, missing means all sources.
    - Examples:
        - `inkpull atsumaru -s <series url> -g <group name>`
        - `inkpull atsumaru -s <series url>`
        - `inkpull atsumaru -c <chapter url>`
        - Note: Currently there are only 2 filters for sources in the default config. If you find a new scanlation group make a bug report with the manga and I will add the scanlation id to default config.

[Back to main page](https://github.com/Zap-09/Inkpull)