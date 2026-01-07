from enum import Enum

from gmatpyplus import GmatObject


class SolverIterations(Enum):
    all = 'all'
    current = 'current'
    none = 'none'


# TODO add Report class in command.py that triggers writing to a ReportFile
class ReportFile(GmatObject):
    # TODO complete documentation of ReportFile.__init__() parameters.
    def __init__(self, name: str, parameters: list, file: str, write_report: bool = True, write_headers: bool = True,
                 left_justify: bool = True, zero_fill: bool = False, fixed_width: bool = True,
                 append_to_existing_file: bool = False, delimiter: str = ' ',
                 solver_iterations: SolverIterations = SolverIterations.current, column_width: int = 23,
                 precision: int = 16) -> None:
        """
        Saves report data to a text file.

        :param name:
        :type name: str
        :param parameters:
        :type parameters: list
        :param file:
        :type file: str
        :param write_report:
        :type write_report: bool
        :param write_headers:
        :type write_headers: bool
        :param left_justify:
        :type left_justify: bool
        :param zero_fill:
        :type zero_fill: bool
        :param fixed_width:
        :type fixed_width: bool
        :param append_to_existing_file:
        :type append_to_existing_file: bool
        :param delimiter:
        :type delimiter: str
        :param solver_iterations:
        :type solver_iterations: SolverIterations
        :param column_width:
        :type column_width: int
        :param precision:
        :type precision: int
        """

        # """
        # TODO add missing parameters from below to __init__()
        # gmat.Help('RF1') output:
        #
        # ReportFile  RF1
        #
        #    Field                                   Type   Value
        #    --------------------------------------------------------
        #
        #    SolverIterations                        List   Current
        #    UpperLeft                            Rvector   [0, 0]
        #    Size                                 Rvector   [0, 0]
        #    RelativeZOrder                       Integer   0
        #    Maximized                            Boolean   false
        #    Filename                            Filename   RF1.txt
        #    Precision                            Integer   16
        #    Add                              ObjectArray   {}
        #    WriteHeaders                         Boolean   true
        #    LeftJustify                            OnOff   On
        #    ZeroFill                               OnOff   Off
        #    FixedWidth                           Boolean   true
        #    Delimiter                             String
        #    ColumnWidth                          Integer   23
        #    WriteReport                          Boolean   true
        #    AppendToExistingFile                 Boolean   false
        # """

        self._parameters: list = parameters
        self._file: str = file
        self._write_report: bool = write_report
        self._write_headers: bool = write_headers
        self._left_justify: bool = left_justify
        self._zero_fill: bool = zero_fill
        self._fixed_width: bool = fixed_width
        self._append_to_existing_file: bool = append_to_existing_file
        self._delimiter: str = delimiter
        self._solver_iterations: SolverIterations = solver_iterations
        self._column_width: int = column_width
        self._precision: int = precision

        super().__init__('ReportFile', name)
