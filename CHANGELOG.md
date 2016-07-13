## Changelog

If you need more details about the changes made visit the
[releases](https://github.com/conda/conda-env/releases) page
on Github. Every release commit has all the information about
the changes in the source code.

#### v2.5.2 (07/13/16)

- Fix #257 environment.yml parsing errors. (@jseabold, #261)
- Fix #254 Override file's name using --name command line argument. (@jseabold, #262)


#### v2.5.1 (06/16/16)

- Remove selectors. (@kalefranz, #253)
- Add integration tests. (@malev, #206)
- Fix conda env remove by proxying to conda remove --all. (@mcg1969, #251)
- Fix unexpected prune parameter in pip installer. (@kdeldycke, #246)

#### v2.5.0 (06/13/16)

- Add a mechanism to let an environment disable the default channels (@mwiebe, #229)
- Fix conda env create <username>/<env name> (@oyse, #228)
- Move activate scripts to conda main repo, (@msarahan, #234)
- Add conda.pip module from conda (@ilanschnell, #235)
- Implement --prune options for "conda env update" (@nicoddemus, #195)
- Preprocessing selectors, (@Korijn, #213)

#### v2.4.5 (12/08/15)

- Store quiet arg as True (default to False) (@faph, #201)
- Initial support for requirements.txt as env spec (@malev, #203)
- Fix PROMPT reverting to $P$G default (@tadeu, #208)
- Fix activation behavior on Win (keep root Scripts dir on PATH); improve behavior with paths containing spaces (@msarahan, #212)

#### v2.4.4 (10/26/15)

- Change environment's versions when uploading. (@ijstokes, #191)
- Support specifying environment by path, as well as by name. (@remram44, #60)
- activate.bat properly searches CONDA_ENVS_PATH for named environments. (@mikecroucher, #164)
- Add Library\\bin to path when activating environments. (@malev, #152)

#### v2.4.3 (10/18/15)

- Better windows compatibility
- Typos in documentation

#### v2.4.2 (08/17/15)

- Support Jupyter

#### v2.4.1 (08/12/15)

- Fix `create` bug

#### v2.4.0 (08/11/15)

- `update` works with remote definitions
- `CONDA_ENV_PATH` fixed
- Windows prompt fixed
- Update `pip` dependencies
- `Library/bin` add to path in win
- Better authorization message
- Remove `--force` flag from upload
- New version created every time you run upload
- Using `conda_argparse2` now
- Fix `activate` script in ZSH
- `--no-builds` flag in attach
- Create environment from notebooks

#### v2.3.0 (07/09/15)

- `--force` flag on `create`
- `--no-builds` flag on `export`
- `conda env attach` feature

#### v2.2.3 (06/18/15)

- Reimplement `-n` flag

#### v2.2.2 (06/16/15)

- Allow `--force` flag on upload

#### v2.2.1 (6/8/15)

- Fix py3 issue with exceptions

### v2.2.0 (6/15/15)

- Create environment from remote definitions
- Upload environment definitions to anaconda.org
