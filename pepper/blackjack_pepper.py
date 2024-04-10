import os
import sys
import time
sys.path.append(os.getenv("PEPPER_TOOLS_HOME") + "/cmd_server")
import pepper_cmd

class BlackjackPepper():
    def __init__(self):
        self._instance = pepper_cmd.robot

        self.reset_posture()
        self.reset_sonars()
        self.reset_asr()
    
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
    
    def reset_posture(self):
        self._instance.normalPosture()
    
    def reset_asr(self):
        memory_service = self._instance.memory_service

        memory_service.insertData(self._instance.fakeASRkey, "")
    
    def scan_for_person(self, person_pos, front):
        memory_service = self._instance.memory_service

        if front:
            memory_service.insertData(
                "Device/SubDeviceList/Platform/Front/Sonar/Sensor/Value",
                float(person_pos)
            )
        else:
            memory_service.insertData(
                "Device/SubDeviceList/Platform/Back/Sonar/Sensor/Value",
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

        return front_person_scanned, back_person_scanned
    
    def on_back_person_scanned(self):
        print "[Pepper]: Person scanned behind me"
        self.say("Hello! You are behind me.")
        self.say("Please, come in front so that I can see you.")

    def on_front_person_scanned(self):
        print "[Pepper]: Person scanned in front of me"
        self.say("Hello! I'm Pepper the robot.")
        self.hello()
    
    def say(self, sentence, require_answer=False):
        self._instance.say(sentence)
        if require_answer:
            return self.listen()
        return None
    
    def listen(self):
        memory_service = self._instance.memory_service

        answer = memory_service.getData(self._instance.fakeASRkey)
        while not answer:
            time.sleep(5.)
            self.say("Sorry, I didn't hear you.")
            self.say("Can you repeat, please?")
            answer = memory_service.getData(self._instance.fakeASRkey)
            memory_service.insertData(self._instance.fakeASRkey, "")
        return answer
    
    '''def introduce(self):
        self.say("I'm Pepper the robot.")
        name = self.say("What's your name?", require_answer=True)
        self.say("Hi " + name + "! Nice to meet you!")'''
    
    def hello(self):
        motion_service = self._instance.motion_service

        joint_names = [
            "RElbowRoll", "RElbowYaw", "RHand", "RShoulderPitch", "RShoulderRoll",
            "RWristYaw"
        ]
        joint_values = [1.32, 1.42, 1.71, -0.03, -0.10, -1.01]
        times = 0.8
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
    
    def victory(self):
        motion_service = self._instance.motion_service

        joint_names = [
            "RShoulderPitch", "RShoulderRoll", "RElbowRoll", "RWristYaw", "RHand",
            "HipRoll", "HeadPitch",
            "LShoulderPitch", "LShoulderRoll", "LElbowRoll", "LWristYaw", "LHand"
        ]
        joint_values = [
            -0.141, -0.46, 0.892, -0.8, 0.98,
            -0.07, -0.07,
            -0.141, 0.46, -0.892, 0.8, 0.98
        ]
        motion_service.angleInterpolation(joint_names, joint_values, 1., True)

        for step in range(2):
            joint_names = [
                "RElbowYaw", "LElbowYaw", "HipRoll", "HeadPitch"
            ]
            joint_values = [2.7, -1.3, -0.07, -0.07]
            motion_service.angleInterpolation(joint_names, joint_values, 0.6, True)

            joint_names = [
                "RElbowYaw", "LElbowYaw", "HipRoll", "HeadPitch"
            ]
            joint_values = [1.3, -2.7, -0.07, -0.07]
            motion_service.angleInterpolation(joint_names, joint_values, 0.6, True)

        self._instance.normalPosture()
    
    def sad(self):
        motion_service = self._instance.motion_service

        joint_names = [
            "RElbowRoll", "RElbowYaw", "RShoulderPitch", "RShoulderRoll",
            "LElbowRoll", "LElbowYaw", "LShoulderPitch", "LShoulderRoll",
            "HeadPitch", "HipPitch"
        ]
        joint_values = [1.38, 0.382, 1.33, -0.69, -1.42, -0.333, 1.24, 0.699, 0.445, -0.52]
        motion_service.angleInterpolation(joint_names, joint_values, 0.6, True)

        motion_service.angleInterpolation("HeadYaw", 0.30, 0.4, True)
        motion_service.angleInterpolation("HeadYaw", -0.30, 0.4, True)
        motion_service.angleInterpolation("HeadYaw", 0.30, 0.4, True)

        self._instance.normalPosture()
    
    def slide_tile_left(self):
        motion_service = self._instance.motion_service

        joint_names = [
                "RElbowRoll", "RElbowYaw", "RHand", "RShoulderPitch", 
                "RShoulderRoll", "RWristYaw"
                ]
        joint_values = [1.38, 1.23, 0.92, 1.20, -0.25, -1.22]
        motion_service.angleInterpolation(joint_names, joint_values, 0.8, True)
     
        motion_service.angleInterpolation("RHand", 0.52, 0.3, True)
     
        joint_names = ["RElbowRoll", "RElbowYaw", "RShoulderRoll", "RWristYaw"]
        joint_values = [1.30, 1.28, -0.92, -0.60]
        motion_service.angleInterpolation(joint_names, joint_values, 0.6, True)

        self._instance.normalPosture()

    def slide_tile_right(self):
        motion_service = self._instance.motion_service

        joint_names = [
                "RElbowRoll", "RElbowYaw", "RHand", "RShoulderPitch", 
                "RShoulderRoll", "RWristYaw"
                ]
        joint_values = [1.30, 1.28,  0.92, 1.20, -0.92, -0.60]
        motion_service.angleInterpolation(joint_names, joint_values, 0.8, True)
     
        motion_service.angleInterpolation("RHand", 0.52, 0.3, True)
     
        joint_names = ["RElbowRoll", "RElbowYaw", "RShoulderRoll", "RWristYaw"]
        joint_values = [1.38, 1.23, -0.25, -1.22]
        motion_service.angleInterpolation(joint_names, joint_values, 0.6, True)

        self._instance.normalPosture()

    def slide_tile_up(self):
        motion_service = self._instance.motion_service

        joint_names = [
                "RElbowRoll", "RElbowYaw", "RHand", "RShoulderPitch", 
                "RShoulderRoll", "RWristYaw"
                ]
        joint_values = [1.34, 1.39, 0.92, 1.20, -0.26, -1.17]
        motion_service.angleInterpolation(joint_names, joint_values, 0.8, True)
     
        motion_service.angleInterpolation("RHand", 0.52, 0.3, True)
     
        joint_names = ["RElbowRoll", "RShoulderPitch"]
        joint_values = [0.91, 0.83]
        motion_service.angleInterpolation(joint_names, joint_values, 0.6, True)

        self._instance.normalPosture()

    def slide_tile_down(self):
        motion_service = self._instance.motion_service

        joint_names = [
                "RElbowRoll", "RElbowYaw", "RHand", "RShoulderPitch", 
                "RShoulderRoll", "RWristYaw"
                ]
        joint_values = [0.91, 1.39, 0.92, 0.83, -0.26, -1.17]
        motion_service.angleInterpolation(joint_names, joint_values, 0.8, True)
     
        motion_service.angleInterpolation("RHand", 0.52, 0.3, True)
     
        joint_names = ["RElbowRoll", "RShoulderPitch"]
        joint_values = [1.34, 1.20]
        motion_service.angleInterpolation(joint_names, joint_values, 0.6, True)

        self._instance.normalPosture()
    