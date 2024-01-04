import sys
import argparse
from pathlib import Path
import logging
from vocexcel import profiles
from vocexcel.utils import EXCEL_FILE_ENDINGS, KNOWN_TEMPLATE_VERSIONS, KNOWN_FILE_ENDINGS, RDF_FILE_ENDINGS, ConversionError
from vocexcel.convert import excel_to_rdf, rdf_to_excel


def main(args=None):

    if args is None:  # vocexcel run via entrypoint
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(
        prog="vocexcel",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "-i",
        "--info",
        help="The version and other info of this instance of VocExcel.",
        action="store_true",
    )

    parser.add_argument(
        "-l",
        "--listprofiles",
        help="This flag, if set, must be the only flag supplied. It will cause the program to list all the vocabulary"
        " profiles that this converter, indicating both their URI and their short token for use with the"
        " -p (--profile) flag when converting Excel files",
        action="store_true",
    )

    parser.add_argument(
        "file_to_convert",
        nargs="?",  # allow 0 or 1 file name as argument
        type=Path,
        help="The Excel file to convert to a SKOS vocabulary in RDF or an RDF file to convert to an Excel file",
    )

    parser.add_argument(
        "-v", "--validate",
        help="Validate output file",
        action="store_true"
    )

    parser.add_argument(
        "-p",
        "--profile",
        help="A profile - a specified information model - for a vocabulary. This tool understands several profiles and"
        "you can choose which one you want to convert the Excel file according to. The list of profiles - URIs "
        "and their corresponding tokens - supported by VocExcel, can be found by running the program with the "
        "flag -lp or --listprofiles.",
        default="vocpub-46",
    )

    parser.add_argument(
        "-o",
        "--outputfile",
        help="An optionally-provided output file path. If not provided, output is to standard out.",
        required=False,
    )

    parser.add_argument(
        "-f",
        "--outputformat",
        help="An optionally-provided output format for RDF outputs. 'graph' returns the in-memory graph object, "
        "not serialized RDF.",
        required=False,
        choices=["longturtle", "turtle", "xml", "json-ld", "graph"],
        default="longturtle",
    )

    parser.add_argument(
        "-s",
        "--sheet",
        help="The sheet within the target Excel Workbook to process",
        default="vocabulary",
    )

    parser.add_argument(
        "-t",
        "--templatefile",
        help="An optionally-provided Excel-template file to be used in SKOS-> Excel converion.",
        type=Path,
        required=False,
    )

    # 1 - info, 2 - warning, 3 - violation
    # error severity level
    parser.add_argument(
        "-e",
        "--errorlevel",
        help="The minimum severity level which fails validation",
        default=1,
    )

    # print severity level
    parser.add_argument(
        "-m",
        "--messagelevel",
        help="The minimum severity level printed to console",
        default=1,
    )

    # log to file
    parser.add_argument(
        "-g",
        "--logfile",
        help="The file to write logging output to",
        type=Path,
        required=False,
    )

    args = parser.parse_args(args)

    if not args:
        # show help if no args are given
        parser.print_help()
        parser.exit()

    if args.listprofiles:
        s = "Profiles\nToken\tIRI\n-----\t-----\n"
        for k, v in profiles.PROFILES.items():
            s += f"{k}\t{v.uri}\n"
        print(s.rstrip())
    elif args.info:
        # not sure what to do here, just removing the errors
        from vocexcel import __version__

        print(f"VocExel version: {__version__}")
        from vocexcel.utils import KNOWN_TEMPLATE_VERSIONS

        print(
            f"Known template versions: {', '.join(sorted(KNOWN_TEMPLATE_VERSIONS, reverse=True))}"
        )
    elif args.file_to_convert:
        if not args.file_to_convert.suffix.lower().endswith(tuple(KNOWN_FILE_ENDINGS)):
            print(
                "Files for conversion must either end with .xlsx (Excel) or one of the known RDF file endings, '{}'".format(
                    "', '".join(RDF_FILE_ENDINGS.keys())
                )
            )
            parser.exit()

        # input file looks like an Excel file, so convert Excel -> RDF
        if args.file_to_convert.suffix.lower().endswith(tuple(EXCEL_FILE_ENDINGS)):
            try:
                o = excel_to_rdf(
                    args.file_to_convert,
                    profile=args.profile,
                    sheet_name=args.sheet,
                    output_file_path=args.outputfile,
                    output_format=args.outputformat,
                    error_level=int(args.errorlevel),
                    message_level=int(args.messagelevel),
                    log_file=args.logfile,
                    validate=args.validate,
                )
                if args.outputfile is None:
                    print(o)
            except ConversionError as err:
                logging.error("{0}".format(err))
                return 1

        # RDF file ending, so convert RDF -> Excel
        else:
            try:
                o = rdf_to_excel(
                    args.file_to_convert,
                    profile=args.profile,
                    output_file_path=args.outputfile,
                    template_file_path=args.templatefile,
                    error_level=int(args.errorlevel),
                    message_level=int(args.messagelevel),
                    log_file=args.logfile,
                )
                if args.outputfile is None:
                    print(o)
            except ConversionError as err:
                logging.error(f"{err}")
                return 1


if __name__ == "__main__":
    retval = main(sys.argv[1:])
    if retval is not None:
        sys.exit(retval)
