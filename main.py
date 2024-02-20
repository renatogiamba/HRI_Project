import os
import sys
import time
sys.path.append(os.getenv("PEPPER_TOOLS_HOME") + "/cmd_server")
sys.path.append("pepper")
import pepper_cmd
import blackjack_pepper

if __name__ == "__main__":
    pepper_cmd.begin()
    pepper = blackjack_pepper.BlackjackPepper()

    loop = True

    try:
        while loop:
            front_person_scanned = False
            back_person_scanned = False
            person_scanned = False

            while not person_scanned:
                front_person_scanned, back_person_scanned = pepper.scan_for_person(
                    1.2, True
                )
                pepper.reset_sonars()
                person_scanned = front_person_scanned or back_person_scanned

                if front_person_scanned:
                    pepper.on_front_person_scanned()
                    pepper.introduce()
                    loop = False
                if back_person_scanned:
                    pepper.on_back_person_scanned()
                time.sleep(1.)

    except KeyboardInterrupt:
        loop = False
    
    pepper_cmd.end()
