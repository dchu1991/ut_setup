# Universal Tester FW Setup Check Script

this is a program designed to be implemented for tester before every testing of the product.  compare FW and HW stacks of tester and see if it meets requirement.  logs can be found after execution.

- this package largely uses python standard libraries because i'm too lazy to build a docker image specifically for this task.
- this package has been tested on python 3.6.9 (tester python3 version) and it was working fine.

    usage: 
    ```
    python3 utester_fw_check.py Redstone/Delta
    ```

logs can be found in the logs directory.

possible future improvements:
- implement pathlib
- make installable
- parse results to a centralized db
- ...
