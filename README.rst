VocExcel
********
Another Excel to RDF converter for SKOS vocabs, but one that include profile-based validation of results.

How to use
==========

Creating vocabularies
---------------------
The file *VocExcel-template.xlsx* in this repository contains the Excel template to be used to create vocabularies. The template contains notes on use, examples of simple & complex vocabularies and lookup lists of values (e.g. organisations). Vocab authors only need this file to create vocabulary content by filling it out.

Use one Excel workbook per vocabulary.

Generating RDF from Excel
-------------------------
There are several methods available to process vocabularies entered into the Excel template using resources in this repository:

1. Windows command line
2. Shell command line script (Linux/Unix/Mac)
3. Python script
4. Python module
5. Online - *coming soon!*

Methods 1 & 2 all use the same options. See the section `Command Line Arguments`_.

1. Windows command line
```````````````````````
There is a Windows EXE file, ``vocexcel.exe``, in the ``vocexcel/bin/`` folder that can be used like this:

::

    c:\\Users\\nick> vocexcel.exe vocabulary-x.xlsx

The command above will generate a vocabulary RDF file in the same directory as the ``vocexcel.exe`` program.

2. Shell command line script (Linux/Unix/Mac)
``````````````````````````````````````````
The script ``vocexcel/bin/vocexcel.sh`` can be run as a shell script on Linux/Unix/Mac with the same options as the Windows EXE program.

::

    ~$ sh vocexcel.sh vocabulary-x.xlsx

Note that to run this shell script, you need to have installed a Python environment that contains this program's dependencies which are all listed in ``requirements.txt``. The shell script then needs to be told where the Python environment is: see the ``PYTHON`` variable in the script.

3. Python script
````````````````
The Python script ``convert.py`` in the ``vocexcel/`` directory can be run on Wondows/Unix/Linux/Mac systems like this:

::

    ~$ python convert.py vocabulary-x.xlsx

As long as a Python environment containing the program's needed modules, listed in ``requirements.txt`` are installed.

4. Python module
````````````````
The converter program can be called from other Python programs, perhaps as part of a chain of processing. For this, you would need code like this:

::

    from vocexcel import convert
    from pathlib import Path

    convert.convert_file(Path(".") / "path" / "to" /"vocab-file.xlsx")

This will create a file ``vocab-file.ttl`` in the same directory as the ``vocab-file.xlsx``.

There are several options for ``convert_file()``, just see the function itself in ``vocexcel/convert.py``.

5. Online
`````````
*Coming soon!*.

We will be providing a web page for easy use.


Command Line Arguments
``````````````````````
All command line options can be printed out by the Windows, Linux/Unix/Mac versions of the tools by specifying ``-h`` for 'help' like this:

::

    > vocexcel.exe -h

    ~$ sh vocexcel.sh -h

It will print something like this with any updates actually available in the tool:

::

    usage: convert.py [-h] [-v] [-lp] [-val] [-p PROFILE] [-of {file,string}] [-s SHEET] excel_file

    positional arguments:
      excel_file            The Excel file to convert to a SKOS vocabulary in RDF

    optional arguments:
      -h, --help            show this help message and exit
      -v, --version         The version of this copy of VocExel. (default: False)
      -lp, --listprofiles   This flag, if set, must be the only flag supplied. It will cause the program to list all the vocabulary profiles that this converter, indicating
                            both their URI and their short token for use with the -p (--profile) flag when converting Excel files (default: False)
      -val, --validate      Validate output file (default: False)
      -p PROFILE, --profile PROFILE
                            A profile - a specified information model - for a vocabulary. This tool understands several profiles andyou can choose which one you want to convert
                            the Excel file according to. The list of profiles - URIs and their corresponding tokens - supported by VocExcel, can be found by running the program
                            with the flag -lp or --listprofiles. (default: vocpub)
      -of {file,string}, --outputformat {file,string}
                            The format of the vocabulary output. (default: file)
      -s SHEET, --sheet SHEET
                            The sheet within the target Excel Workbook to process (default: vocabulary)

Note that the ``excel_file`` parameter is always required except for the 'help' (``-h``) option, so if you want tpo print out the version of the program, you will need to put in a fake file location like this:

::

    > vocexcel.exe -v .

    ~$ sh vocexcel.sh -v .



License
=======
This code is licensed using the GPL v3 licence. See the `LICENSE
file <LICENSE>`_ for the deed. Note that Excel is property of Microsoft.


Contact
=======

| *Lead Developer*:
| **Nicholas Car**
| *Data System Architect*
| `SURROUND Australia Pty Ltd <https://surroundaustralia.com>`_
| nicholas.car@surroundaustralia.com

| **Company support**:
| info@surroundaustralia.com