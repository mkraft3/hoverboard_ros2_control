// Copyright 2023 Robert Gruberski (Viola Robotics Sp. z o.o. Poland)
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#pragma once

#include <cstdint>

#define HEAD_FRAME 0xABCD

// enum class MOTOR_STATES {
//     UNOCUPPIED = 0b00,
//     RUN = 0b01,
//     BRAKE = 0b11,
//     LOCK_SHAFT = 0b10,
// };

typedef struct __attribute__((packed)) {
    uint16_t head;          // 0xABCD
    int16_t  cmd1;
    int16_t  cmd2;
    int16_t  speedR_meas;   // RPM rechts
    int16_t  speedL_meas;   // RPM links
    int16_t  batVoltage;    // V * 100
    int16_t  boardTemp;     // °C * 10
    uint16_t cmdLed;
    uint16_t checksum;
} MotorWheelFeedback;

typedef struct {
    uint16_t head = HEAD_FRAME;
    int16_t  steer;
    int16_t  speed;
    uint16_t checksum;
} MotorWheelDriveControl;
