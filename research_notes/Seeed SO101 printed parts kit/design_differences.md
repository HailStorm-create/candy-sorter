# Seeed "fine-tuned" SO-ARM101 printed parts vs. official TheRobotStudio SO-101 design

Research date: 2026-10-23. About 18 tool calls. Several sources (Pakronics, Switch Science) returned HTTP 429 when fetched in full, so some of their content is known only from search-engine snippets. Those items are flagged below.

## 1. What exactly did Seeed change?

### Takeaway
Seeed has not published a changelog, a diff, or modified STLs. The only public description is the one-line listing text ("fine-tuned for easier installation", "feature a Servo Adaptor Board for Seeed Studio XIAO", "slightly different than the official documents on Github"). Seeed's own SO-101 wiki links only the official TheRobotStudio STLs and says nothing about the changes.

### Cited Findings
- The reseller listing text, copied from Seeed, says the parts "have been fine-tuned for easier installation and feature a Servo Adaptor Board for Seeed Studio XIAO. The parts will be slightly different than the official documents on Github." — [RobotShop (US)](https://robotshop.com/products/seeedstudio-so-arm101-ai-arm-3d-printed-parts); [RobotShop CA](https://ca.robotshop.com/products/seeedstudio-so-arm101-ai-arm-3d-printed-parts)
- Kit contents: 12 leader parts (black), 11 follower parts (white) and 12 clamp parts (grey). Material is PLA+, with 15% infill for leader and clamps and 30% for follower. "Motors not included, just 3-D printed parts." — [RobotShop CA](https://ca.robotshop.com/products/seeedstudio-so-arm101-ai-arm-3d-printed-parts) (contents from the search snippet; the full-page fetch did not show the parts list)
- Openelab's listing for the older Seeed SO-ARM100 printed kit uses the same wording ("fine-tuned... Servo Adaptor Board for Seeed Studio XIAO... somewhat different from the official documents on Github"). So this is a long-running Seeed practice and not specific to SO-101. — [openelab SO-ARM100 (SV)](https://openelab.io/sv/products/seeed-studio-so-arm100)
- The Switch Science (Japan) listing also says the shape differs slightly from the official GitHub design because the parts were tuned for easier assembly. — [Switch Science 10706](https://www.switch-science.com/products/10706) (search snippet only; the full fetch returned 429)
- Seeed's SO-ARM10x LeRobot wiki links its STL downloads straight to TheRobotStudio's official files (`STL/SO101/Follower/Ender_Follower_SO101.stl`, `Prusa_Follower_SO101.stl`, and the matching Leader files). It does not mention any Seeed-modified geometry. — [Seeed wiki lerobot_so100m_new](https://wiki.seeedstudio.com/lerobot_so100m_new/)
- The only Seeed-specific printed extras on the wiki are an optional TPU soft gripper and a camera-mount insert, from a separate repo (`xiehuangbao888/soarm_soft_gripper`). — [Seeed wiki](https://wiki.seeedstudio.com/lerobot_so100m_new/)
- The official repo's common parts include `Base_SO101.stl`, `Base_motor_holder_SO101.stl` and `WaveShare_Mounting_Plate_SO101.stl`. The Waveshare plate is the only board-specific mount in the official design. — [TheRobotStudio/SO-ARM100 README](https://github.com/TheRobotStudio/SO-ARM100)
- The official README lists Seeed only as a kit vendor ("They include 3d printed kits"). It says nothing about Seeed's modifications. — [TheRobotStudio/SO-ARM100](https://github.com/TheRobotStudio/SO-ARM100)

### Inferences
- The one named change is a mount for Seeed's own XIAO servo adaptor board. Most likely it replaces or reworks the official `WaveShare_Mounting_Plate_SO101.stl` or the board area on the base. "Fine-tuned for easier installation" most plausibly means hole and slot tolerances. Neither is confirmed.
- Seeed's wiki points buyers to the unmodified official STLs and an unchanged assembly flow. That suggests Seeed treats its changes as cosmetic or fit-related rather than functional, but this is an inference.

### Gaps
- No Seeed STL or STEP source, changelog, or wiki section describing the modifications was found. No GitHub repo from Seeed or Seeed-Projects with modified SO-101 STLs turned up in searches.
- No Reddit, Discord or blog post comparing Seeed-printed parts with self-printed official parts was found.
- Whether the Seeed kit includes the official Waveshare plate, a Seeed-specific plate, or neither could not be verified.

## 2. Do joint positions and link lengths match the official SO-101 URDF?

### Takeaway
No report of kinematic differences was found: no complaints about link lengths, gripper geometry or servo orientation in Seeed parts. No positive confirmation of a match was found either. The Seeed wiki tells Seeed buyers to use the standard so101 software and the official STLs, which implicitly assumes the same kinematics. Treat "same kinematics" as likely but unverified, and measure it yourself.

### Cited Findings
- The official `Simulation/SO101/` folder contains `so101_new_calib.urdf/.xml`, `so101_new_calib_camera.urdf/.xml`, `so101_old_calib.urdf/.xml`, `so101_leader_new_calib.urdf`, `scene.xml` and `joints_properties.xml`. — [TheRobotStudio Simulation/SO101](https://github.com/TheRobotStudio/SO-ARM100/tree/main/Simulation/SO101)
- New calibration (the default) puts each joint's virtual zero at the middle of its range. Old calibration puts zero at the pose where the arm is "fully extended horizontally". The URDFs were generated from Onshape with onshape-to-robot. STS3215 properties were adapted from Open Duck Mini. — [Simulation/SO101 README](https://github.com/TheRobotStudio/SO-ARM100/tree/main/Simulation/SO101)
- The README says LeRobot treats the gripper as a linear 0–100 value (0 is closed, 100 is open). This mapping "is not yet reflected" in the URDF or MuJoCo files. — [Simulation/SO101 README](https://github.com/TheRobotStudio/SO-ARM100/tree/main/Simulation/SO101)
- The Seeed wiki says SO-101 and SO-100 assembly is the same except for added cable clips and the leader gear ratios. For the follower, it says the only difference is the end-effector installation after step 12. It says nothing about changed joint geometry. — [Seeed wiki](https://wiki.seeedstudio.com/lerobot_so100m_new/)

### Inferences
- LeRobot calibration stores per-arm homing offsets and ranges. Small differences in horn seating or part tolerance are absorbed into calibration and do not matter for teleop or imitation learning.
- URDF-based IK and MuJoCo sim-to-real depend on link lengths and axis placement. If Seeed's "fine-tuning" had changed those, the official URDF would be wrong. No evidence says it did, but nothing confirms it didn't. Before relying on URDF IK, measure axis-to-axis distances on the built Seeed arm (shoulder-lift to elbow, elbow to wrist-flex, wrist to gripper tip) and compare them with the joint origins in `so101_new_calib.urdf`.
- The gripper tip / TCP is the most likely place for a small difference, for example if the Seeed jaw is the soft or alternative gripper. Check the gripper part against the official STL if TCP accuracy matters.

### Gaps
- No measurements or side-by-side CAD comparison of Seeed vs. official parts were found.
- Servo horn orientation and joint zero direction in Seeed's assembly were not independently verified. The wiki uses the same steps, so they are presumably identical.

## 3. Does the Seeed follower work with standard LeRobot setup and calibration?

### Takeaway
Yes. Seeed's wiki uses the stock `lerobot-setup-motors --robot.type=so101_follower` and `lerobot-calibrate --robot.type=so101_follower` commands, with the same motor IDs (gripper is 6 down to shoulder_pan 1) and the same mid-range-then-full-sweep calibration as the Hugging Face docs. The Seeed-specific parts are a recommended Seeed fork of LeRobot, power-supply notes by kit edition, and a mid-position helper tool.

### Cited Findings
- Seeed's commands are `lerobot-setup-motors --robot.type=so101_follower --robot.port=/dev/ttyACM0`, `--teleop.type=so101_leader` for the leader, and `lerobot-calibrate --robot.type=so101_follower ... --robot.id=...`. The setup script "will automatically set the id and baudrate for that motor". — [Seeed wiki](https://wiki.seeedstudio.com/lerobot_so100m_new/)
- The Hugging Face SO-101 docs use the same commands and say the same thing: move all joints to mid-range, press Enter, then sweep each joint through its full range. The docs give the leader gear ratios as 1/191, 1/345, 1/191, 1/147, 1/147, 1/147. — [HF LeRobot SO-101 docs](https://huggingface.co/docs/lerobot/so101)
- Seeed-specific notes:
  - The wiki recommends Seeed's LeRobot fork, which "has been verified with SO-ARM10x".
  - It gives Seeed servo SKUs: leader ST-3215-C044 (1:191) on L1/L3, C001 (1:345) on L2, C046 (1:147) on L4–L6. Follower is C001 (7.4 V), or C018/C047 (12 V, Pro) at 1:345.
  - Standard Edition kits use 5 V supplies for both arms. Pro uses 5 V for the leader and 12 V for the follower.
  - A "SoARM middle-position tool" writes position 2048 to clear errors like "Magnitude 30841 exceeds 2047".
  - It says that "it is normal that the terminal does not receive a signal from servo 5" during calibration.
  - It says JetPack 6.2 "is not supported yet".
  - Source: [Seeed wiki](https://wiki.seeedstudio.com/lerobot_so100m_new/)

### Inferences
- The robot type in software is plain `so101_follower`/`so101_leader`, so a Seeed-built arm is the same robot to LeRobot. The Seeed fork is optional. Upstream LeRobot's so101 classes should work, since the motors and IDs are identical.
- A 12 V Pro follower and a 7.4 V/5 V Standard follower differ in torque, not in software config.

### Gaps
- What Seeed's fork changes relative to upstream LeRobot was not investigated.
- The source of the "servo 5 no signal is normal" note was not established. It may be a firmware or board quirk.

## 4. What is the "Servo Adaptor Board for Seeed Studio XIAO", and can a non-Seeed board be used?

### Takeaway
It is Seeed's own small Feetech/ST-series bus-servo driver PCB (42 x 25 mm, 5–12 V input, USB or UART selectable). It ships in Seeed's SO-ARM101 servo-motor kit, not in the printed-parts kit; the printed kit only has a mount shaped for it. LeRobot talks to any such board as a plain USB serial port, so the board choice does not matter for software. The open question is physical: whether a Waveshare board fits the Seeed base mount.

### Cited Findings
- Seeed's wiki covers two related products:
  - The Bus Servo Driver Board has no onboard MCU or case and is driven by an external host.
  - The XIAO Bus Servo Adapter has an onboard XIAO ESP32-C3 and a 3D-printed case.
  - Both talk UART to ST/SC series (Feetech) servos.
  - USB mode needs a back solder bridge closed (pads differ between v1 and v2) plus a 2.54 mm jumper on the front 2-pin header. UART mode is the default, with the header unshorted.
  - The wiki links LeRobot's Feetech driver as a packet example.
  - Source: [Seeed wiki bus_servo_driver_board](https://wiki.seeedstudio.com/bus_servo_driver_board/)
- Specs: 5–12 V DC input, a 2-pin 3.5 mm screw terminal for power, a 2.5 mm 3-pin servo connector, 42 x 25 mm excluding protrusions, about 15 g. Roughly £4.5–4.7 in the UK, A$10.98 in Australia, about $5 in Japan. — [The Pi Hut](https://thepihut.com/products/bus-servo-driver-board-for-seeed-xiao); [RobotShop UK](https://uk.robotshop.com/products/seeedstudio-bus-servo-driver-board-xiao); [Pakronics](https://www.pakronics.com.au/products/bus-servo-driver-board-for-seeed-studio-xiao-ss105990190) (search snippets)
- Switch Science describes this board as tuned for LeRobot and the SO-ARM101, with a USB control interface. — [Switch Science 11115](https://www.switch-science.com/products/11115) (search snippet; Japanese)
- Seeed's SO-ARM101 servo kit (without printed parts) includes "STS3215 servo motors, a Servo Adaptor Board for Seeed Studio XIAO, studs, screws, power and USB-C cables". — [Pakronics servo kit](https://www.pakronics.com.au/products/new-so-arm101-low-cost-ai-arm-servo-motor-kit-for-lerobot-without-3d-printed-parts-ss114993666) (search snippet; the full fetch returned 429). RobotShop UK says only "servo motors, an adapter board, and cables". — [RobotShop UK](https://uk.robotshop.com/products/seeed-studio-so-arm101-ai-arm-servo-motor-kit-pro-lerobot-w-o-3d-printed-parts)
- A Pakronics listing reportedly says boards bought after 3 March 2025 use the "Servo Adaptor Board for Seeed Studio XIAO" datasheet, and earlier boards use the "Serial Bus Servo Drive Board" datasheet. So Seeed changed the board in its kits around then. — Pakronics, via a search-result summary only ([Pakronics assembled kit](https://pakronics.com.au/products/so-arm101-low-cost-ai-arm-servo-motor-kit-pro-for-lerobot-assembled-version-ss100046482)). Unverified; the page returned 429.
- The official SO-101 BOM's "Motor Control Board" is a Waveshare bus servo adapter, and the official design has `WaveShare_Mounting_Plate_SO101.stl`. — [TheRobotStudio README](https://github.com/TheRobotStudio/SO-ARM100)
- The HF docs are board-agnostic ("controller board"). Their only board-specific note is "If you are using a Waveshare controller board, make sure that the two jumpers are set on the `B` channel (USB)." — [HF LeRobot SO-101 docs](https://huggingface.co/docs/lerobot/so101)

### Inferences
- Software: LeRobot only needs a serial port (`--robot.port=/dev/ttyACM0`, or a COM port on Windows) that speaks the Feetech protocol at the configured baud. A Waveshare Bus Servo Adapter (A), a Feetech FE-URT-1, or the Seeed board all work identically once in USB mode (Waveshare: jumpers on B; Seeed: solder bridge plus jumper). Board choice is irrelevant to calibration, URDF or IK.
- The printed-parts kit's "feature a Servo Adaptor Board" most likely means a mount sized for the 42 x 25 mm Seeed board. The Waveshare board is a different size, so it may not fit the Seeed mount. Fallbacks: print the official `WaveShare_Mounting_Plate_SO101.stl`, or zip-tie or double-side-tape the board to the base or table, since the board isn't structural. Neither fallback was confirmed.
- If buying Seeed printed parts with a non-Seeed motor kit (for example a Waveshare-board kit), budget for printing or improvising a board mount.

### Gaps
- Whether the Seeed printed kit physically includes a board, or only a mount, is not stated explicitly. The evidence (the board is listed in the servo kit and the printed kit is "parts only") points to a mount only.
- Mount hole spacing on the Seeed base, and whether a Waveshare board fits it, were not found anywhere.
- The USB-serial chip on the Seeed board (relevant to drivers on Windows or macOS) was not stated on the wiki.

## 5. Does Seeed's assembly guide differ from the official SO-101 guide?

### Takeaway
Not materially. Seeed's wiki follows the same joint-by-joint sequence: 20 image steps for the leader and 17 for the follower. Its stated differences are SO-100 vs. SO-101 differences (cable clips, leader gear ratios, end-effector), not Seeed-part differences. The HF guide uses video steps with explicit screw specs (M2x6 for motors, M3x6 for horns and links).

### Cited Findings
- Seeed: "The only differences are the addition of cable clips on SO-ARM101" and the different leader gear ratios. For the follower, the only difference is the end-effector (gripper/handle) installation after step 12. The guide has 20 leader steps and 17 follower steps, image-based. — [Seeed wiki](https://wiki.seeedstudio.com/lerobot_so100m_new/)
- HF official: assembly runs Joint 1 to 5, then gripper/handle. Motors use M2x6 screws, horns and links use M3x6. Setup assigns motor IDs before assembly, and the controller board is "attached to the base of the arm" afterwards. — [HF LeRobot SO-101 docs](https://huggingface.co/docs/lerobot/so101)

### Inferences
- If Seeed's part tweaks had changed the assembly order or the screws, its guide would probably say so. The unchanged guide supports the view that the tweaks are tolerance and board-mount changes only.

### Gaps
- Seeed's assembly images were not compared frame-by-frame with the HF videos. The images may show a different board-mount step, which the text extraction would not capture.
