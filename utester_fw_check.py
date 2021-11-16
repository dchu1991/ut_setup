import json
import sys
from xml.etree import ElementTree as ET

from lib.test_info import TesterInfo


def main() -> None:

    if len(sys.argv) != 2:
        raise ValueError(
            'argument length not correct.  expected to specify and only specify testertype')

    # load config files and staged actions
    fwconfig = json.load(
        open('./ConfigFiles/UniversalTesterFirmwareConfig.json'))
    root = ET.parse('./staged_actions.xml').getroot()

    # context managerify the test object
    with TesterInfo(sys.argv[1]) as test:

        # static checks
        for child in root:
            test.compareFW(**child.attrib)

        # adaptive part -- adjusted according to different # of DUTs
        test.checkout_activePLX(fwconfig['PLX'])

        # this part is already adaptive whatsoever
        if test.testertype == 'Redstone':
            test.checkout_activeSPI(fwconfig['SPI_rom'])


if __name__ == '__main__':
    main()
