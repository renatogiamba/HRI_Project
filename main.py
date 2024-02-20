import os
import sys
sys.path.append(os.getenv("PEPPER_TOOLS_HOME") + "/cmd_server")
sys.path.append("pepper_utils")
import pepper_cmd
import pepper_animations

if __name__ == "__main__":
    pepper_cmd.begin()
    pepper = pepper_cmd.robot

    pepper_animations.hello(pepper)
    pepper_cmd.end()
