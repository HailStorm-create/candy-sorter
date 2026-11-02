# Claude's contributions

I helped. Claude Code (an AI coding assistant) worked alongside me on this project.

## What Claude did
- Taught me the inverse kinematics math (I derived and coded `ik.py` myself), and added `from_servo` and the self-test to it
- Wrote the camera code: capture, and video recording with the on-screen boxes (`capture.py`)
- Wrote the camera calibration fit, where the arm draws its own dots (`pixel_to_arm.py`, `calib_dots.py`)
- Wrote candy detection (`detect.py`) and the data collection script (`collect.py`)
- Wrote the sorter (`sort_candy.py`): grab strategies, grip check, drops and watch mode
- Cleaned up the dataset crops and found the shadow problem that became the "nothing" class
- Taught me the training script step by step while I built `train.py`

## What I did
- The idea, the build and the whole physical setup
- Inverse kinematics (`ik.py`)
- Collected and labeled all 461 candy crops
- Built and ran the training script
- Tested, tuned and ran everything on the real robot
