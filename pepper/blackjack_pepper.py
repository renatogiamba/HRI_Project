import os
import sys
sys.path.append(os.getenv("PEPPER_TOOLS_HOME") + "/cmd_server")
import pepper_cmd

class BlackjackPepper():
    def __init__(self):
        self._instance = pepper_cmd.robot

        self.reset_sonars()
    
    def reset_sonars(self):
        memory_service = self._instance.memory_service

        memory_service.insertData(
            "Device/SubDeviceList/Platform/Front/Sonar/Sensor/Value",
            10.0
        )
        memory_service.insertData(
            "Device/SubDeviceList/Platform/Back/Sonar/Sensor/Value",
            10.
        )
    
    def scan_for_person(self, person_pos):
        memory_service = self._instance.memory_service

        memory_service.insertData(
            "Device/SubDeviceList/Platform/Front/Sonar/Sensor/Value",
            float(person_pos)
        )
        front_sonar_value = memory_service.getData(
            "Device/SubDeviceList/Platform/Front/Sonar/Sensor/Value"
        )
        back_sonar_value = memory_service.getData(
            "Device/SubDeviceList/Platform/Back/Sonar/Sensor/Value"
        )

        front_person_scanned = front_sonar_value < 1.5
        back_person_scanned = back_sonar_value < 1.5

        if front_person_scanned:
            print("Front person approached.")
        if back_person_scanned:
            print("Back person approached.")

        return front_person_scanned, back_person_scanned

    
    def hello(self):
        motion_service = self._instance.motion_service

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

        self._instance.normalPosture()

    def hand_shake(self):
        motion_service = self._instance.motion_service

        joint_names = [
            "RElbowRoll", "RElbowYaw", "RHand", "HeadPitch", "HeadYaw"
        ]
        joint_values = [1.25, 1.63, 0.98, 0.052, -0.31]
        times = 0.8
        motion_service.angleInterpolation(joint_names, joint_values, 0.8, True)

        for step in range(3):
            joint_names = [
                "RElbowRoll", "RHand"
            ]
            joint_values = [1.53, 0.54]
            motion_service.angleInterpolation(joint_names, joint_values, 0.3, True)

            joint_values = [1.15, 0.54]
            motion_service.angleInterpolation(joint_names, joint_values, 0.3, True)

            if step == 2:
                joint_values = [1.53, 0.54]
                motion_service.angleInterpolation(joint_names, joint_values, 0.3, True)
    
        motion_service.angleInterpolation("RHand", 0.98, 0.3, True)
    
        self._instance.normalPosture()
