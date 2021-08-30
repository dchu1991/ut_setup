import os
import logging
import traceback
import json

from typing import Any, List
from lib.check_firmware import CheckTesterFirmwareSetups
from lib.check_hardware import CheckTesterHardwareSetups


class CompareError(Exception):
    """this error is raised upon any comparison errors."""

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class SetupCheckFail(Exception):
    """intended only for failing setup checks."""

    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class TesterInfo:
    """get all tester related info

    this class stores all tester related info to attributes:
    -   testertype: Delta/Redstone
    -   check_result: list of dict containing all compare results

    load tester info according to hardware, and perform basic checks for consistency
    -   gpu addresses, check number for consistency
    -   lr10 addresses, check number for consistency
    TODO: pcie topology checks

    and also contains several methods:
    -   compareFW: execute read_func, and compares read_ver with expected_ver, raise Exceptions if encountered.
        append results to check_result
    -   dump*: dump all relevant info to files
    -   tracebacklog: log traceback to file
    -   check_active*: adaptive checks for PLX, interposer SPI roms respectively.

    """

    check_result: list = []
    check_fw = CheckTesterFirmwareSetups()
    check_hw = CheckTesterHardwareSetups()

    def __init__(self, testertype: str) -> None:
        self.testertype = testertype
        # i'll leave it to someone interested in implementing pcie checks.
        self.gpu_addr, self.lr10_addr = self.check_hw._get_nv_modules()
        self.num_gpus = len(self.gpu_addr)
        self.num_lr10 = len(self.lr10_addr)

        # logs dir init
        self.log_dir = os.path.join(os.getcwd(), 'logs')
        if not os.path.exists(self.log_dir):
            os.mkdir(self.log_dir)
        self.logger = self._init_logger(os.path.join(
            self.log_dir, 'UniversalTesterFirmwareSetupCheck.log'))

        self._tester_info_checkin()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.logger.info(f'dumping test info.')
        self.dump_result()
        self.dump_testerinfo()
        self.count_fails(self.check_result)

    # protected methods

    def _tester_info_checkin(self) -> None:

        if self.testertype not in self.check_hw.testertype_dict.keys():
            raise TypeError(
                'please specify a valid testertype: [Delta, Redstone]')

        gpus_per_board = self.check_hw.testertype_dict[self.testertype]['gpus_per_board']
        lr10s_per_board = self.check_hw.testertype_dict[self.testertype]['lr10s_per_board']

        if self.num_gpus % gpus_per_board != 0:
            raise CompareError(
                f"number of GPUs must be multiple of {gpus_per_board} for tester type {self.testertype}, but found {self.num_gpus} instead.")

        self.num_of_DUTs = self.num_gpus // gpus_per_board

        if self.num_lr10 != lr10s_per_board * self.num_of_DUTs:
            raise CompareError(
                f"number of lr10s must be multiple of {lr10s_per_board}, but got {self.num_lr10} instead."
            )

        # PLX switches
        if self.num_of_DUTs == 1:
            # confirmed true for Redstone/Delta
            self.plx_check_list = [
                'TesterSideSwitches', 'LowerBoardSideSwitches']

        elif 2 <= self.num_of_DUTs <= 4:
            self.plx_check_list = [
                'TesterSideSwitches', 'LowerBoardSideSwitches', 'UpperBoardSideSwitches']

        else:
            # only proceed in the presense of DUTs, and also catch other abnormalities
            raise ValueError('number of DUTs must be in the range of 1-4')

    def _init_logger(self, log_file: str) -> logging.Logger:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(message)s",
            datefmt="%Y-%m-%d %I:%M:%S",
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(
                    filename=log_file, mode='w')
            ]
        )
        return logging.getLogger()

    def _tracebacklog(self, filename: str, msg: str) -> None:
        tlogger = logging.getLogger(name='traceback')
        file_h = logging.FileHandler(filename=filename, mode='w')
        file_h.setLevel(logging.INFO)
        tlogger.addHandler(file_h)
        tlogger.info(msg)

    @staticmethod
    def count_fails(res: List[dict]) -> None:
        fails = 0
        for item in res:
            if item['result'] == "Fail":
                fails += 1
        if fails:
            raise SetupCheckFail(f'found {fails} setup check fails.')

    # general methods

    def compareFW(self, expected_ver: str, func_name: str, name: str, **kwargs: Any) -> None:
        """monstrous function...

        -   takes in the read function, execute it (with kwargs if any) to find the read_ver
        -   compare with the expected version
        -   store results in dict, later append to self.check_results
        -   log info as the function progresses

        """

        read_func = getattr(self.check_fw, func_name)
        ret_dict = {
            'name': name,
            'fuction': read_func.__name__
        }
        self.logger.info(f'checking {name}...')

        try:
            if kwargs:
                self.logger.debug(f'additional argument is {kwargs}')
                ret_dict['args'] = kwargs

            read_ver = read_func(**kwargs)
            self.logger.info(f'read version is {read_ver}')
            ret_dict['read_version'] = read_ver
            self.logger.info(f'expected version is {expected_ver}')
            ret_dict['expected_version'] = expected_ver

            if expected_ver != read_ver:
                raise CompareError(
                    f'expected version: {expected_ver} doesn\'t match with read version: {read_ver}')

        except CompareError as exception_msg:
            self.logger.warning(f'the comparison failed')
            ret_dict['result'] = 'Fail'
            ret_dict['errormsg'] = exception_msg

        except Exception as exception_msg:
            self.logger.error(
                f'calling the function {read_func.__name__} with argument {kwargs} failed')
            self.logger.error(
                f'logging traceback to {read_func.__name__}_callfail.log')
            self._tracebacklog(os.path.join(
                self.log_dir, f'{read_func.__name__}_callfail.log'), msg=traceback.format_exc())
            ret_dict['result'] = 'Fail'
            ret_dict['errormsg'] = exception_msg

        else:
            self.logger.info('the comparison passed')
            ret_dict['result'] = 'Pass'

        finally:
            self.check_result.append(ret_dict)

    def checkout_activePLX(self, fw_config: dict) -> None:
        self.logger.info('checking the PLX switches')
        for k1 in self.plx_check_list:
            for k2 in fw_config[k1]:
                ver = fw_config[k1][k2]['version']
                addr = fw_config[k1][k2]['addr']
                self.compareFW(expected_ver=ver, func_name="checkPLX",
                               name=f'PLX FW {k2}', dev_bus=addr)

    def checkout_activeSPI(self, expected_ver: str) -> None:
        self.spi_indexes = self.check_hw.get_SPI_list()
        self.num_spi = len(self.spi_indexes)

        if self.num_spi != 2*self.num_of_DUTs:
            raise CompareError(
                f"number of SPI roms should be {2*self.num_of_DUTs}, but only found {self.num_spi}")

        self.logger.info('checking the Universal Interposer SPI ROM versions')
        for i, addr in self.spi_indexes:
            self.compareFW(expected_ver=expected_ver, func_name="checkSPI",
                           name=f'universal interposer SPI ROM at nvflash index {i} and topology address {addr}', index=i)

    def dump_result(self, filename: str = "output.json") -> None:
        full_filename = os.path.join(self.log_dir, filename)
        self.logger.info(f'dumping test results to {full_filename}...')
        with open(full_filename, mode='w') as f:
            json.dump(self.check_result, f, indent=4, default=str)

    def dump_testerinfo(self, filename: str = 'setup_check_info.json') -> None:
        full_filename = os.path.join(self.log_dir, filename)
        self.logger.info(f'dumping setup check info to {full_filename}...')
        with open(full_filename, mode='w') as f:
            json.dump(self.__dict__, f, indent=4, default=str)
