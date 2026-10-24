# Seeed Studio SO-ARM101 Pre-Printed Parts Kit: Contents and Real-World Quality

Research date: 2026-10-23. Buyer context: owns 6 third-party STS3215 servos (RCmall 6-pack, possibly 7.4V), a non-Seeed driver board, a 5V PSU and clamps; building only the follower arm.

Overall evidence quality: **thin.** I found no detailed independent teardown, YouTube build review, or Reddit/GitHub thread specifically about the Seeed pre-printed kit's print quality or missing parts. Most hard facts come from vendor listings. User reports are few and some come from other vendors' printed parts. Several sites (OpenELab, armdojo, dcadditivepros, MakerWorld, rcdrone) returned HTTP 429/403 and could not be read.

## 1. Exact contents: follower vs leader parts, hardware, adaptor board, and follower completeness

### Takeaway
The kit is printed plastic only: 11 follower parts (white), 12 leader parts (black) and 12 clamp parts (grey), in PLA+. No vendor clearly promises screws, horns, servos or electronics, and at least one says they are not included. The 11 and 12 counts match the official SO-101 part list exactly, which suggests the follower set is a complete follower arm, including a driver-board mounting plate. The Servo Adaptor Board itself is almost certainly not in the box.

### Cited Findings
- RobotShop's listing gives the contents as 12x Leader Part (Black), 11x Follower Part (White), 12x Clamps Part (Grey). It says the parts are PLA+, with 15% infill for leader and clamp parts and 30% for follower parts. — [RobotShop (search snippet of listing)](https://robotshop.com/products/seeedstudio-so-arm101-ai-arm-3d-printed-parts)
- When fetched directly, the RobotShop page said only "Motors not included, just 3-D printed parts", that the parts are "fine-tuned for easier installation", and that they "will be slightly different than the official documents on Github". It lists no screws or hardware. Price was 38.21 USD, SKU RB-See-1200, with no reviews or Q&A. — [RobotShop](https://www.robotshop.com/products/seeedstudio-so-arm101-ai-arm-3d-printed-parts)
- The RobotShop page mentions a "Servo Adaptor Board for Seeed Studio XIAO", but in a product-family description, not as a box item. — [RobotShop](https://www.robotshop.com/products/seeedstudio-so-arm101-ai-arm-3d-printed-parts)
- Unmanned Tech (UK) lists "12 Leader parts and 11 Follower parts", "3D-printed PLA/ABS", and "color may vary based on production run". It says "Servos and electronics are not included" and that screws and servo horns "may vary depending on current stock and supplier availability". It does not say whether screws are included, mentions no clamps, and only links an adaptor-board datasheet. It also links a "Finedtune" version on MakerWorld. — [Unmanned Tech](https://www.unmannedtechshop.co.uk/products/so-arm101-low-cost-ai-arm-3d-printed-skeleton)
- Seeed's own page (SKU 114993668, $30.99, or $28.99 each for 10+) says it "Includes all 3D-printed structural parts" without itemizing them. It shows a 92% rating from 11 reviews, but the review text did not load. — [Seeed Studio](https://www.seeedstudio.com/SO-101-3D-printed-Enclosure-p-6428.html)
- Seeed's Motor Kit does not include the 3D-printed parts or a camera; the printed parts are sold separately. — [Seeed Studio kit page (search summary)](https://www.seeedstudio.com/SO-ARM101-Low-Cost-AI-Arm-Kit-p-6426.html); [CNX Software, May 2025](https://www.cnx-software.com/2025/05/02/so-arm101-open-source-dual-robotic-arm-kit-works-with-hugging-faces-lerobot/)
- Mouser describes the motor kit as including servos, an adapter board and cables. It describes the "AI Arm printed skeleton kit" as including the 3D-printed parts. — [Mouser](https://www.mouser.com.tr/new/seeed-studio/seeed-studio-robot-so-arm101-kit)
- OpenELab (search snippet) says the printed-only kit must be paired with the Seeed SO-ARM101 Pro Servo Motor Kit to be fully functional. Switch Science says a separate power supply and a host PC or Jetson are also needed. — [OpenELab](https://openelab.com/products/seeed-studio-so-arm101-kit); [Switch Science](https://www.switch-science.com/collections/ai/products/10744)
- The official SO-101 individual part files are:
  - **Common to both arms (9):** Base_motor_holder_SO101, Base_SO101, Motor_holder_SO101_Base, Motor_holder_SO101_Wrist, Under_arm_SO101, Upper_arm_SO101, Rotation_Pitch_SO101, Wrist_Roll_Pitch_SO101, WaveShare_Mounting_Plate_SO101
  - **Leader only (3):** Handle_SO101, Trigger_SO101, Wrist_Roll_SO101
  - **Follower only (2):** Moving_Jaw_SO101, Wrist_Roll_Follower_SO101

  — [TheRobotStudio/SO-ARM100 README](https://github.com/TheRobotStudio/SO-ARM100)
- The official repo has a separate "Seeed Studio mounting plate" for the XIAO bus servo driver board, updated in merged PR #127 (Sep 2, 2025). In GitHub issue #131 (Oct 5, 2025), a user noted that the official parts only had a Waveshare plate while "all the available kits switched to the Bus Servo Driver Board for Seeed Studio XIAO". The reply pointed to the Seeed plate in the repo. — [Issue #131](https://github.com/TheRobotStudio/SO-ARM100/issues/131); [Issues search, PR #127](https://github.com/TheRobotStudio/SO-ARM100/issues?q=seeed)

### Inferences
- The official files add up exactly to the vendor counts: 9 common + 2 follower-only = 11 follower parts, and 9 common + 3 leader-only = 12 leader parts. So the 11 white parts are very likely:
  - base
  - base motor holder
  - base-motor holder
  - wrist motor holder
  - rotation pitch (shoulder)
  - upper arm
  - under arm
  - wrist roll pitch
  - wrist roll follower (which carries the fixed jaw)
  - moving jaw
  - a driver-board mounting plate

  On that basis the follower set covers every structural part of a complete follower arm. This comes from the counts, not from a published Seeed packing list.
- The mounting plate in Seeed's kit is probably shaped for Seeed's XIAO Servo Adaptor Board, not the Waveshare board. The buyer's non-Seeed driver board may not fit it. They may need to print or improvise a mount, or skip the plate, since it is not structural.
- "Mount only, no board" is the most likely reading for the Servo Adaptor Board. No listing puts the board in the box, Unmanned Tech says electronics are excluded, and the board ships with Seeed's motor kit. This is inferred, not confirmed.
- Screws are best assumed **not included**. No listing lists screws as a box item, and the STS3215 servos normally come with their own horn screws. The OpenELab assembly guide uses M2x6 screws for motor mounting and M3x6 for horns and segment joints (see section 3). The buyer should check what came with the RCmall servos.
- The buyer already owns clamps, so the 12 grey clamp parts are extra or spare.

### Gaps
- No official Seeed packing list naming each of the 11, 12 and 12 parts was found. The Seeed product page's details and reviews tabs did not render, and the OpenELab listing returned 429.
- The make-up of the 12 grey "clamp parts" is not confirmed (for example, how many clamps and whether each has a body, screw and pad).
- Seeed's own page does not say whether screws are included. No unboxing photo or video confirming it was found.
- Material is stated inconsistently: "PLA+" on RobotShop versus "PLA/ABS" on Unmanned Tech.
- Unmanned Tech shows "4.9/5 based on 273 reviews". This is probably a store-wide widget, not reviews of this product, so it is not counted as evidence.

## 2. Print quality reported by users (material, infill, layers, warping, accuracy, support remnants)

### Takeaway
Seeed states PLA+ with 30% infill for follower parts, which is denser than the 15% community default. I found no user report specifically about the Seeed kit's layer quality, warping, accuracy or support remnants. The few nearby reports range from "super high quality" to "extremely poor print quality", but they come from other vendors' printed parts.

### Cited Findings
- Seeed and RobotShop state PLA+, with 30% infill for the follower and 15% for the leader and clamps. — [RobotShop (search snippet)](https://robotshop.com/products/seeedstudio-so-arm101-ai-arm-3d-printed-parts)
- The official and wiki print guidance is PLA+, 15% infill, a 0.4 mm nozzle at 0.2 mm layers or a 0.6 mm nozzle at 0.4 mm layers, and supports everywhere except slopes over 45°. It specifies no supports in horizontal-axis screw holes. — [Seeed wiki LeRobot SO-101 guide](https://wiki.seeedstudio.com/lerobot_so100m_new/); [TheRobotStudio README](https://github.com/TheRobotStudio/SO-ARM100)
- Seeed's page shows 92% from 11 reviews. The individual review text was not readable. — [Seeed Studio](https://www.seeedstudio.com/SO-101-3D-printed-Enclosure-p-6428.html)
- PartaBot sells a full SO-ARM101 kit with PLA+ parts and does not say who printed them, so these are **not confirmed Seeed parts**. Of its 9 reviews, 7 were top-rated. Comments ranged from "Extremely poor print quality and no easy access to assembly instructions" to "Great product! Super high quality". — [PartaBot](https://partabot.com/products/so-arm101)
- Earlier search summaries said OpenELab's printed-skeleton listing had 6 reviews averaging about 4.67/5, mostly praising easy setup and good condition on arrival. The page itself could not be fetched (429), so the review text was not verified. — [OpenELab](https://openelab.io/products/seeed-studio-arm101-low-cost-ai-arm-3d-printed-skeleton)
- A builder who had made the older SO-100 said the SO-101 design "is more refined" and "the tolerances are better", and that assembly was "noticeably easier". This describes the design and they printed their own parts, so it says nothing about Seeed's prints. — [Kamath Robotics](https://kamathrobotics.com/so-101-kicking-off-a-new-series)

### Inferences
- 30% infill on follower parts should make them somewhat stiffer and give screws more to bite than a 15% home print. That helps the follower arm, which carries the load.
- Without Seeed-specific reports, the buyer should run a quick inspection on arrival. Check for support scars in the servo pockets and screw holes, and for warped flat bases.

### Gaps
- No Reddit, Discord or YouTube report specifically about the Seeed kit's layer quality, warping, dimensional accuracy or support remnants was found.
- The Seeed review text was not accessible.
- A secondary materials-guide blog (dcadditivepros.com) could not be fetched (429), and it may sell printed parts. Its claims appear only in search snippets: clamps splitting along layer lines, long arm sections separating, tight motor pockets and stripped screw bosses. They are general SO-101 claims, not about Seeed, and unverified. — [dcadditivepros (unverified snippet)](https://dcadditivepros.com/blogs/news/so-101-printed-parts-material-guide)

## 3. Fit with STS3215 servos, horns and screws

### Takeaway
Reports describe a tight, press-fit servo pocket that needs force. Burrs from printing can block screw holes or catch during assembly. Screws can strip the plastic or fail to reach the horn, and one user needed roughly 10 mm M3 screws. None of these reports is confirmed to involve Seeed-printed parts. The Akizuki report likely does (a Seeed sales channel), but that is not certain.

### Cited Findings
- A builder (March 27, 2026) bought printed parts and the Pro motor kit from Akizuki Denshi Tsusho:
  - Parts are "molded to exactly the right size", so pushing a motor into its slot takes "quite a bit of courage and force".
  - Burrs can catch during assembly. They recommend scraping contact surfaces with a flat-head screwdriver.
  - Burrs around screw holes forced them to remove screws after fastening several.
  - They advise test-passing screws through the parts before final assembly.
  - The printed "receiver" held up even when pried open strongly.

  — [LAplust Tech Blog (note.com)](https://note.com/laplust/n/n1ce78dcea58b?hl=en)
- TheRobotStudio's README names Akizuki Denshi as one of Seeed's sales channels for kits that include printed parts. — [TheRobotStudio README](https://github.com/TheRobotStudio/SO-ARM100)
- A PartaBot reviewer (printer of parts unknown) wrote:
  - "removing a motor from its 3D-printed groove is challenging"
  - "the screws were stripping the print and sometimes did not go inside the motor horn"
  - they needed "longer screws (e.g., 10mm)" and suggested longer M3 screws.

  — [PartaBot](https://partabot.com/products/so-arm101)
- The OpenELab-hosted SO-101 assembly guide (search summary) gives the fasteners as M2x6 for motor mounting (4 per motor, 2 top and 2 bottom), M3x6 for horns, and M3x6 for joining arm segments. — [OpenELab "Build Your Own SO-101 Robot!"](https://openelab.io/blogs/seeed-studio/build-your-own-so-101-robot)
- The official repo has STS3215 fit-gauge prints (Gauge_0, Gauge_tight_1). This shows the pocket fit is meant to be snug and depends on the printer. — [TheRobotStudio README](https://github.com/TheRobotStudio/SO-ARM100)

### Inferences
- If the Akizuki parts are Seeed's, which is likely but unconfirmed, tight servo pockets are by design ("fine-tuned for easier installation" notwithstanding). Light deburring with a knife or flat screwdriver is normal, not a defect.
- Third-party STS3215 clones should share the standard STS3215 case dimensions. The RCmall servos are probably the 7.4V C001 variant. If their housings differ slightly from genuine Feetech units, the press fit could be tighter or looser. No report covering this was found.
- Buying a small assortment of M2x6 to M2x8 and M3x6 to M3x10 self-tapping or machine screws is cheap insurance against stripped bosses and short horn screws.

### Gaps
- No report of cracked Seeed parts during servo insertion was found.
- No report on fit with non-Feetech or clone STS3215s in Seeed-printed parts was found.
- Whether the Seeed kit's screw bosses are sized for self-tapping or machine screws is not documented.

## 4. Missing, broken, wrong or duplicate parts on arrival, and how they were handled

### Takeaway
No reports were found of Seeed printed-parts kits arriving with missing, broken, wrong or duplicate parts, or of how Seeed or resellers handled such claims. That is an absence of evidence, not evidence of reliability.

### Cited Findings
- PartaBot reviewers (not confirmed Seeed parts) said "Includes everything, arrived quickly, works perfectly". Another listed boards, servos, cables, power supplies, webcam and fasteners as included. None reported missing parts. — [PartaBot](https://partabot.com/products/so-arm101)
- OpenELab reviews were summarized in search as mentioning good condition on arrival, but could not be verified directly. — [OpenELab](https://openelab.io/products/seeed-studio-arm101-low-cost-ai-arm-3d-printed-skeleton)
- Unmanned Tech showed the item as sold out and "awaiting stock" on the research date. — [Unmanned Tech](https://www.unmannedtechshop.co.uk/products/so-arm101-low-cost-ai-arm-3d-printed-skeleton)
- A search of TheRobotStudio/SO-ARM100 issues for "seeed" found no defect or missing-part issues. It found only #188, #187, #184, #161, #131, #127 and #42, which are docs, links, mounting plate and servo alternatives. — [GitHub issue search](https://github.com/TheRobotStudio/SO-ARM100/issues?q=seeed)

### Inferences
- Since every part is available as an STL in the official repo, a missing or broken follower part can be reprinted locally or at a print shop. This is a practical fallback whatever the vendor's policy.

### Gaps
- Seeed's and RobotShop's return or replacement handling for printed parts was not found.
- No Reddit or Discord threads on Seeed kit arrival problems were found. Reddit was not directly searchable here, and LeRobot Discord is not indexed.

## 5. Known issues or revisions of the Seeed kit (v1 vs later)

### Takeaway
Seeed's printed parts are a "fine-tuned" variant that differs slightly from the official GitHub STLs. The main documented change in the ecosystem is the move from a Waveshare mounting plate to a Seeed XIAO board plate (repo update Sep 2025). No Seeed version numbers or changelog were found.

### Cited Findings
- RobotShop says Seeed's parts are "fine-tuned for easier installation" and "will be slightly different than the official documents on Github". — [RobotShop](https://www.robotshop.com/products/seeedstudio-so-arm101-ai-arm-3d-printed-parts)
- Unmanned Tech links a separate "Finedtune" version on MakerWorld, presumably Seeed's tuned files. The MakerWorld page returned 403 and could not be checked. — [Unmanned Tech](https://www.unmannedtechshop.co.uk/products/so-arm101-low-cost-ai-arm-3d-printed-skeleton); [MakerWorld model 1287622 (not readable)](https://makerworld.com/models/1287622)
- "Update Seeed Studio mounting plate for SO-101" (PR #127) was merged Sep 2, 2025. Issue #131 (Oct 2025) notes kits switched to the Seeed XIAO bus servo driver board. — [GitHub](https://github.com/TheRobotStudio/SO-ARM100/issues?q=seeed); [Issue #131](https://github.com/TheRobotStudio/SO-ARM100/issues/131)
- The Seeed wiki says SO-100 source files were removed from the official repo after the SO-101 update, and that SO-101 prints are compatible with the SO-100 motor kit. It mentions a follower end-effector installation difference after Step 12. — [Seeed wiki](https://wiki.seeedstudio.com/lerobot_so100m_new/)
- The Unmanned Tech listing says "color may vary based on production run", which implies several production batches. — [Unmanned Tech](https://www.unmannedtechshop.co.uk/products/so-arm101-low-cost-ai-arm-3d-printed-skeleton)
- A LeRobot wrist-roll calibration problem (leader and follower zero points not matching) is a software issue tied to the full_turn_motor list, not a printed-part defect. It can look like a hardware fault. — [huggingface/lerobot issue #3193](https://github.com/huggingface/lerobot/issues/3193)

### Inferences
- The kit appears to be a single SO-101 generation. Batch differences are most likely in color, mounting plate and possibly supplier, not geometry. This is unconfirmed.

### Gaps
- No Seeed changelog, part revision number or v1/v2 naming for the printed kit was found.
- What exactly Seeed "fine-tuned" (tolerances, hole sizes, which parts) is undocumented in the sources reached.
- The MakerWorld tuned-file page and its comments could not be accessed.
