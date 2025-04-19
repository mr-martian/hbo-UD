# Ancient Hebrew UD

This is an in-progress conversion of the Old Testament in Hebrew using data from https://github.com/etcbc/bhsa

# Status

Manually-verified trees can be found in the files named `data/checked/[book].conllu`. The statistics are roughly the following, though I will probably forget to update this table, so run `make [book]-report` for up-to-date numbers.

| Book | Sentences | Words |
|---|---|---|
| Genesis | 1494 / 1494 (100%) | 36822 / 36822 (100%) |
| Exodus | 1151 / 1151 (100%) | 29882 / 29882 (100%) |
| Leviticus | 820 / 820 (100%) | 21769 / 21769 (100%) |
| Numbers | 116 / 1179 (10%) | 1288 / 28923 (4%) |
| Deuteronomy | 21 / 879 (2%) | 226 / 26171 (1%) |
| Ruth | 85 / 85 (100%) | 2297 / 2297 (100%) |

As books are completed, they are released in CoNLL-U format to [the UD repo](https://github.com/UniversalDependencies/UD_Ancient_Hebrew-PTNK/) and in text-fabric format to [the BHSA extension module repo](https://github.com/mr-martian/bhsa-ud-tf).

# License

The original data is licensed under [Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)](https://creativecommons.org/licenses/by-nc/4.0/) and the resulting trees are under the same license.

Persistent link to original: [10.17026/dans-z6y-skyh](http://dx.doi.org/10.17026%2Fdans-z6y-skyh).

All code in this repository is under the MIT license.
