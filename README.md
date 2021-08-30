# Universal Tester FW Setup Check Script

this is a program designed to be implemented for tester before every testing of the Redstone/Delta

this package largely uses python standard libraries because i'm too lazy to build a docker image specifically for this task.

this package has been tested on python 3.6.9 (tester python3 version) and it was working fine.

    usage: python3 utester_fw_check.py Redstone/Delta

logs can be found in the logs directory.

################################################################################

##RELEASE NOTE

rev 5.1:

    added dimm_info and cpu_info for future imporovements
    added context manager for TesterInfo and slightly modified usage

rev 5.0:

    added check_hardware to suppport for hardware related checks.
    lifted some weights off test_info to check_hardware as well.

rev 4.1:

    included some hardware checks, will raise Errors if not consistent.
    added tester info dumping to testerinfo.json
    raising exceptions everywhere

rev 4.0:

    cleaned up UT_Check so that it is completely free of global variables
    shoveled all tester specific info and comparison methods into test_info
    cleaner to myself... sort of.

rev 3.1:

    move the global variable into class attribute, and implemented dump_result method
    fixed the missing logs directory problem

rev 3.0:

    made the check-fw routine into staged-action and improvise scenes

rev 2.2:

    re-check the check BMC command with Andrey
    facelift with PEP-8 standard

rev 2.1:

    added sys.exit with non-zero exit codes
    idea to include checks for HW as well...?

rev 2.0: 

    improvements on logging: included traceback logs, formatted the logs as well.
    included an output.json for parsing the results.

rev 1.0: 

    implemented a mechanism to deal with the cases when the tester is not fully loaded.
    the log file 'UniversalTesterFirmwareSetupCheck.log' logs every test outcome 

################################################################################
