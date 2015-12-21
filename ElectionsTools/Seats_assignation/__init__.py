
"""
TODO
----
* Code desempate methods
* Support for the multicandidate options (post-transformation)
|--- SNTF(Single non transfarable vote)
|----STV (Single transfarable voting)

-Recrutinio tools


Bibliography
------------
https://github.com/vehrka/dhondt/blob/master/dhondt.py
https://github.com/vokimon/envote
https://github.com/heldergg/labs
https://github.com/aldatsa/electoral-calculator
https://github.com/vehrka/dhondt
https://github.com/msoltysik/docs/tree/7d150d74e811c27ddf3ecdfbf2508676b98c80c2/RLA
https://github.com/cabalamat/euroel/tree/aa280ff5a59d27428bcc390367507e19335fa1a8
https://github.com/heldergg/labs/tree/90822391a67f4fc53fa99ce3b4ac0e30c94935ce/labs_django/hcapp
https://github.com/OKFN-Spain/dhondt/blob/e550bec3e299568409769f0f2edc65b6aaa9ff6b/dhondt.py



"""

from seats_assignation import Mix_assignation
from major_residual import MResidual_assignation
from dhondt import DHondt_assignation
from first_past_the_post import FPTP_assignation

from seats_assignation import create_bunch_assignators
