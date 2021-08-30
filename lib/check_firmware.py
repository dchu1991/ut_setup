import subprocess


class CheckTesterFirmwareSetups:
    """collection of all get FW version methods in the tester"""

    @staticmethod
    def _get_output(cmd: str) -> str:
        """return the stdout of the corresponding command"""
        return subprocess.check_output([cmd], shell=True, encoding='utf-8')

    def checkBMC(self, pos: str) -> str:
        """primary and secondary BMC versions"""
        if pos == '0':
            out = self._get_output('ipmitool raw 0x32 0x8f 0x09 0x01').split()
        if pos == '1':
            out = self._get_output('ipmitool raw 0x32 0x8f 0x09 0x02').split()

        return f'{out[0]}.{out[1]}.{int(out[2],16)}'

    def checkSBIOS(self, pos: str) -> str:
        """primary and secondary SBIOS versions"""
        if pos == '0':
            out = self._get_output('ipmitool raw 0x30 0x24 0').split()
        if pos == '1':
            out = self._get_output('ipmitool raw 0x30 0x24 1').split()

        return f'{int(out[0],16)}.{int(out[1],16)}'

    def checkMBFPGA(self) -> str:
        """get MB FPGA version"""
        out = self._get_output('ipmitool raw 0x30 0x0f 0x00').split()
        return f'{out[1]} {out[2]}'

    def checkMIDFPGA(self) -> str:
        """get Middle board FPGA version"""
        out = self._get_output('ipmitool raw 0x30 0x81 2 0x78 2 45').split()
        return f'{out[0]} {out[1]}'

    def checkPSU(self, pos: str) -> str:
        """all 6 PSU versions"""
        if pos == '0':
            out = self._get_output(
                'ipmitool raw 0x30 0x81 0x03 0x80 0x08 0xe2').split()[1:7]
        if pos == '1':
            out = self._get_output(
                'ipmitool raw 0x30 0x81 0x03 0x82 0x08 0xe2').split()[1:7]
        if pos == '2':
            out = self._get_output(
                'ipmitool raw 0x30 0x81 0x03 0x84 0x08 0xe2').split()[1:7]
        if pos == '3':
            out = self._get_output(
                'ipmitool raw 0x30 0x81 0x04 0x80 0x08 0xe2').split()[1:7]
        if pos == '4':
            out = self._get_output(
                'ipmitool raw 0x30 0x81 0x04 0x82 0x08 0xe2').split()[1:7]
        if pos == '5':
            out = self._get_output(
                'ipmitool raw 0x30 0x81 0x04 0x84 0x08 0xe2').split()[1:7]

        return f'{out[0][1]}.{out[1][1]}/{out[2][1]}.{out[3][1]}/{out[4][1]}.{out[5][1]}'

    def checkPLX(self, dev_bus: str) -> str:
        """get pcie switch version by address"""
        out = self._get_output(
            f'./utils/pcimem /sys/bus/pci/devices/0000:{dev_bus}/resource0 0x29D b 2>/dev/null').split('\n')[-2]
        return f'{out[-2]}.{out[-1]}'

    def checkOS(self) -> str:
        """get OS release version"""
        out = self._get_output("cat /etc/diagos-release").split('\n')[3]
        return out.split('=')[1][1:-1]

    def checkHostName(self) -> str:
        """get hostname"""
        return self._get_output("hostname").rstrip()

    def checkSPI(self, index: str) -> str:
        """get interposer SPI ROM version by nvflash index"""
        out = self._get_output(
            f'./utils/nvflash_mfg -v -i {index} | egrep "^Version"').rstrip()
        return out.split(':')[1].strip()
