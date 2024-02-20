import os
import sys
sys.path.append(os.getenv("PEPPER_TOOLS_HOME") + "/cmd_server")
import pepper_cmd

def hello(pepper):
    motion_service = pepper.motion_service
    joint_names = [
        "RElbowRoll", "RElbowYaw", "RHand", "RShoulderPitch", "RShoulderRoll",
        "RWristYaw"
    ]
    joint_values = [1.32, 1.42, 1.71, -0.03, -0.10, -1.01]
    times = [0.8, 0.8, 0.8, 0.8, 0.8, 0.8]

    motion_service.angleInterpolation(joint_names, joint_values, times, True)
    motion_service.angleInterpolation("RElbowYaw", 1.83, 0.8, True)
    motion_service.angleInterpolation("RElbowYaw", 1.04, 0.8, True)
    motion_service.angleInterpolation("RElbowYaw", 1.42, 0.8, True)
    pepper.normalPosture()
