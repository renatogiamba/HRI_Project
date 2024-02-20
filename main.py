import os
import sys
sys.path.append(os.getenv("PEPPER_TOOLS_HOME") + "/cmd_server")
import pepper_cmd

if __name__ == "__main__":
    pepper_cmd.begin()
    pepper = pepper_cmd.robot

    pepper.say("Hello")
    pepper_cmd.end()