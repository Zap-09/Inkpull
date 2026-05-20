## Table of Contents

- [Supported sites](#supported-sites)
- [Flags and site details](#flags-and-site-details)

## Supported sites

- [Toonily](#toonily) (toonily.com)
- [Weebcentral](#weebcentral) (weebcentral.com)
- [Atsumaru](#atsumaru) (atsu.moe)
- [MangaTaro](#mangataro) (mangataro.org)
- [MangaKatana](#mangakatana) (mangakatana.com)

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
    - Available flags `-s`, `-c`, `-sm`, `-a`
        - use `-s` when you want to download the whole series
        - use `-c` when you want just one chapter
        - `-sm` enables smart chapter selection. It will automatically select chapter from all sources with no duplicate
          chapter.
        - `-a` downloads all available chapters.
        <hr>

        - Note: `-a` takes priority over `-sm` if both are persent.
        - Note 2: `-a` and `-sm` only work with `-s`
    - Examples:
        - `inkpull atsumaru -s <series url>`
        - `inkpull atsumaru -c <chapter url>`
        - `inkpull atsumaru -s <series_url> -sm`
        - `inkpull atsumaru -s <series_url> -a`


- ### MangaTaro
    - Requirements
        - None
    - Available flags `-s`, `-c`
        - use `-s` when you want to download the whole series
        - use `-c` when you just want one chapter
    - Examples:
        - `inkpull mangataro -s <series url>`
        - `inkpull mangataro -c <chapter url>`

- ### MangaKatana
    - Requirements
        - None
    - Available flags `-s`, `-c`
        - use `-s` when you want to download the whole series
        - use `-c` when you just want one chapter
    - Examples:
        - `inkpull mangakatana -s <series url>`
        - `inkpull mangakatana -c <chapter url>`

[Back to main page](https://github.com/Zap-09/Inkpull)
