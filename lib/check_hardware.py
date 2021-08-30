import subprocess
import re
import json

from typing import List, Tuple


class CheckTesterHardwareSetups:
    """collection of all hardware attributes and check methods"""

    testertype_dict: dict = {
        'Redstone': {
            'gpus_per_board': 4,
            'lr10s_per_board': 0
        },
        'Delta': {
            'gpus_per_board': 8,
            'lr10s_per_board': 6
        }
    }
    dimm_info: list = []
    cpu_info: list = []

    def __init__(self) -> None:
        pass

    @staticmethod
    def _get_output(cmd: str) -> str:
        return subprocess.check_output([cmd], shell=True, encoding='utf-8')

    def _get_nv_modules(self) -> Tuple[list, list]:
        lspci = self._get_output('lspci')
        # a list of all gpu addr
        gpus = re.findall(
            r'([0-9a-f]{2}:00.0) 3D controller: NVIDIA Corporation Device', lspci)
        # a list of all lr10 addr
        lr10s = re.findall(
            r'([0-9a-f]{2}:00.0) Bridge: NVIDIA Corporation Device', lspci)
        return (gpus, lr10s)

    def check_pcie_status(self, addr: str) -> Tuple[str, str]:
        out = self._get_output(f"lspci -vvs {addr}")
        m = re.search(r'LnkSta: Speed ([\d\.]+)GT/s, Width x(\d+)', out)
        return m.groups()  # speed, width

    def get_SPI_list(self) -> List[tuple]:
        nvflash_list = self._get_output('./utils/nvflash_mfg --list')
        return re.findall(
            r'<(\d+)> +PEX880.*B:([A-F0-9]+),.*\n', nvflash_list)

    def get_lshw(self) -> None:
        out = self._get_output('lshw -json')
        out_dict = json.loads(out)

        for i in [1, 2, 3, 4]:
            # these are lists
            self.dimm_info += out_dict['children'][0]['children'][i]['children']

        for i in [8, 12]:
            self.cpu_info.append(
                out_dict['children'][0]['children'][i])  # these are dicts

        # for i in range(12):
        #     # 0 BIOS
        #     # 1 System Memory
        #     # 2 System Memory
        #     # 3 System Memory
        #     # 4 System Memory
        #     # 5 L1 cache
        #     # 6 L2 cache
        #     # 7 L3 cache
        #     # 8 CPU
        #     # 9 L1 cache
        #     # 10 L2 cache
        #     # 11 L3 cache
        #     # 12 CPU
        #     out_dict['children'][0]['children'][i]
