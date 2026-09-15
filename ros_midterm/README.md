# คู่มือทำ Midterm: ROS2 + TurtleBot3 (ทำเป็นคู่ 2 คน)

โค้ดทั้งหมดอยู่ในโฟลเดอร์ `ros2_ws/src/` พร้อมใช้งาน (2 แพ็กเกจ):

- `turtlebot3_midterm_interfaces` — เก็บนิยาม action `Rotate.action`
- `turtlebot3_midterm` — เก็บโหนดทั้ง 6 ตัวตามที่โจทย์กำหนด

> เหตุผลที่แยกเป็น 2 แพ็กเกจ: การสร้าง custom action ต้องใช้ `ament_cmake`
> (ไม่ใช่ `ament_python`) เพื่อ generate โค้ด Python จากไฟล์ `.action`
> จึงต้องมีแพ็กเกจ interface แยกต่างหาก แล้วให้แพ็กเกจโหนด python
> ไป `depend` มันอีกที — นี่คือรูปแบบมาตรฐานของ ROS2

---

## ขั้นตอนที่ 0: เตรียมเครื่อง

ต้องมีครบ 3 อย่าง (ทำในเครื่อง/VM ของตัวเอง ไม่ใช่ในแชทนี้):

1. Ubuntu 22.04 + ROS2 Humble (หรือเวอร์ชันที่อาจารย์กำหนด)
2. `sudo apt install ros-humble-turtlebot3*`
3. ตั้งค่า `export TURTLEBOT3_MODEL=burger` ใน `~/.bashrc`

ทดสอบว่า Gazebo รันได้ก่อน:
```bash
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_gazebo empty_world.launch.py
```
ถ้า TurtleBot3 ขึ้นในโลกว่างได้ แปลว่าพร้อมแล้ว

---

## ขั้นตอนที่ 1: วางโค้ดลง workspace ของตัวเอง

```bash
mkdir -p ~/ros2_ws/src
cp -r ros2_ws/src/turtlebot3_midterm_interfaces ~/ros2_ws/src/
cp -r ros2_ws/src/turtlebot3_midterm ~/ros2_ws/src/
```



## ขั้นตอนที่ 2: build

```bash
cd ~/ros2_ws
colcon build
source install/setup.bash
```

ถ้า build แพ็กเกจ interfaces ไม่ผ่าน ให้เช็คว่าติดตั้ง
`ros-humble-rosidl-default-generators` แล้วหรือยัง

ทุกครั้งที่เปิด terminal ใหม่ ต้อง `source install/setup.bash` ก่อนรันโหนด

---

## ขั้นตอนที่ 3: ทดสอบทีละ Section

เปิด terminal แยกไว้เสมอ 1 terminal สำหรับ Gazebo

### เปิด simulation (ทุก section ใช้อันนี้)
```bash
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_gazebo empty_world.launch.py
```

### Section A — Publisher & Subscriber (27 คะแนน)

**Terminal 2:**
```bash
ros2 run turtlebot3_midterm circle_publisher
```
หุ่นยนต์ต้องวิ่งเป็นวงกลมรัศมี ~0.5 ม. ทันที
(v=0.2 m/s, w=v/r=0.4 rad/s — ปรับ `linear_speed` ในโค้ดได้ถ้าอยากได้ความเร็วอื่น
แต่รัศมีต้องคง 0.5 ม.)

**Terminal 3:**
```bash
ros2 run turtlebot3_midterm odom_logger
```
ควรเห็น log พิมพ์ x, y, yaw ต่อเนื่องขณะหุ่นวิ่งวงกลม — นี่คือสิ่งที่ต้อง
โชว์คู่กันในวิดีโอ (Gazebo + terminal นี้พร้อมกัน)

กด `Ctrl+C` ทั้งสอง terminal ก่อนไป section ถัดไป (แล้ว reset โลกใน Gazebo
หรือรีสตาร์ท simulation ใหม่ ถ้าอยากให้หุ่นเริ่มจากจุดเดิม)

### Section B — Service (27 คะแนน)

**Terminal 2:**
```bash
ros2 run turtlebot3_midterm square_service_server
```

**Terminal 3:**
```bash
ros2 run turtlebot3_midterm square_service_client
```
เรียกครั้งเดียว หุ่นควรวิ่งเป็นสี่เหลี่ยมจัตุรัสด้านละ 0.5 ม. ครบ 4 ด้าน
แล้วหยุดสนิท โค้ดใช้ค่าจาก `/odom` จริงในการเช็คระยะทาง/มุมเลี้ยว
ไม่ได้ใช้แค่ตั้งเวลา จึงแม่นกว่า

ถ้าสี่เหลี่ยมเบี้ยว ลองลด `linear_speed` / `angular_speed` ในไฟล์
`square_service_server.py` ลง (ความเร็วสูงทำให้ odometry คลาดเคลื่อนจาก slip)

### Section C — Action (36 คะแนน)

**Terminal 2:**
```bash
ros2 run turtlebot3_midterm rotate_action_server
```

**Terminal 3:**
```bash
# หมุน 180 องศา (ค่า default)
ros2 run turtlebot3_midterm rotate_action_client
# หรือระบุมุมเอง (เรเดียน) เช่น 90 องศา = 1.5708
ros2 run turtlebot3_midterm rotate_action_client 1.5708
```
ต้องเห็น feedback (remaining angle) พิมพ์ทุก ~0.1 วินาที ระหว่างหมุน
แล้วจบด้วย "Goal reached successfully" เมื่อหมุนถึงมุมเป้าหมาย
(ยอมคลาดเคลื่อนได้ ±10 องศาตามเกณฑ์ — โค้ดตั้ง tolerance ไว้ที่ 2 องศา
ซึ่งเข้มกว่าเกณฑ์อยู่แล้ว)

**เรื่อง Kp:** ในโค้ดตั้ง `Kp = 1.0` ไว้เป็นค่าเริ่มต้น ให้ลองปรับดูจริงกับ
Gazebo ของตัวเอง — ถ้าหุ่นหมุนช้าเกินไป/สั่นไม่ถึงเป้า ให้เพิ่ม Kp
ถ้าหุ่นแกว่งเลยเป้าไปมา (overshoot) ให้ลด Kp ค่าที่ได้จากการลองจริง
พร้อมเหตุผลที่ปรับ ต้องเขียนอธิบายไว้ใน Section E (รายงาน) — ห้ามลอกค่าจากที่นี่ตรงๆ
โดยไม่ทดลองเอง เพราะอาจารย์ให้คะแนนจากค่าที่ "นักศึกษาเลือกเอง" และ
"อธิบายได้ว่าได้มาอย่างไร"

---

## ขั้นตอนที่ 4: ทำความเข้าใจโค้ด (สำคัญมาก)

โจทย์บอกชัดว่า **ใช้ AI ช่วยได้ แต่ต้องอธิบายโค้ดของตัวเองได้ทุกบรรทัด**
ทั้งสองคนควรเข้าใจอย่างน้อยประเด็นเหล่านี้ เพราะอาจารย์อาจถามสด:

1. **quaternion → yaw**: ทำไมต้องแปลง? เพราะ ROS เก็บ orientation เป็น
   quaternion (x,y,z,w) ไม่ใช่มุมองศาตรงๆ สูตร `atan2` ที่ใช้คือการดึง
   เฉพาะแกน yaw (การหมุนรอบแกน Z) ออกมา
2. **v = w × r**: ที่มาของสูตรความเร็วเชิงมุมสำหรับวงกลม
3. **P controller**: `cmd_vel = error × Kp` ทำไมยิ่งใกล้เป้าหมาย
   ความเร็วยิ่งลด (error น้อยลง → คำสั่งความเร็วน้อยลง) และทำไมต้อง
   clamp ค่าสูงสุด (`max_ang_vel`) ไม่ให้เกินสเปกของหุ่นจริง
4. **โครงสร้าง action**: goal / result / feedback ต่างกันอย่างไร,
   ทำไม feedback ต้องส่งเป็นระยะ (10 Hz) แต่ result ส่งครั้งเดียวตอนจบ
5. **ทำไม service กับ action ต่างกัน**: service (`Empty`) เหมาะกับงาน
   สั้น ไม่ต้องรู้ความคืบหน้า ส่วน action เหมาะกับงานที่ใช้เวลานาน
   และอยากรู้ระหว่างทาง (feedback) และยกเลิกได้ (cancel)

---

## ขั้นตอนที่ 5: Section D — วิดีโอสาธิต (5 คะแนน)

อัดวิดีโอเดียวต่อเนื่อง 3–5 นาที (ใช้โปรแกรมอัดหน้าจอ เช่น OBS Studio หรือ
SimpleScreenRecorder) โดยเรียงลำดับ:

1. รัน `circle_publisher` + `odom_logger` พร้อมกัน ให้เห็นทั้ง Gazebo
   (หุ่นวิ่งวงกลม) และ terminal (ค่า x,y,yaw ไหลอยู่) — พากย์เสียง
   อธิบายว่ากำลังทำอะไร
2. เรียก `square_service_client` ให้เห็นหุ่นวิ่งครบสี่เหลี่ยมแล้วหยุด
3. ส่ง goal ด้วย `rotate_action_client` ให้เห็น feedback พิมพ์ระหว่าง
   หมุน และข้อความผลลัพธ์ตอนจบ

เช็คก่อนส่ง: จอ Gazebo กับ terminal ต้องอ่านออกชัดทั้งคู่ (ฟอนต์อย่าเล็กไป),
ความยาวอยู่ใน 3–5 นาทีพอดี, มีเสียงพากย์ตลอด ไม่ใช่เงียบแล้วใส่ซับ

---

## ขั้นตอนที่ 6: Section E — รายงาน (5 คะแนน)

ทำ PDF 2–3 หน้า ต้องมีครบ:

- ชื่อ-รหัสนักศึกษาทั้งสองคน + ชื่อแพ็กเกจ (`turtlebot3_midterm`,
  `turtlebot3_midterm_interfaces`)
- **Node diagram**: วาดกล่องแทนแต่ละโหนดทั้ง 6 ตัว
  (`circle_publisher`, `odom_logger`, `square_service_server`,
  `square_service_client`, `rotate_action_server`, `rotate_action_client`)
  ลากเส้นเชื่อมพร้อมกำกับชื่อ topic/service/action และชนิดข้อความ เช่น
  `circle_publisher --/cmd_vel (geometry_msgs/Twist)--> Gazebo/TurtleBot3`,
  `odom_logger <--/odom (nav_msgs/Odometry)-- Gazebo/TurtleBot3`,
  `square_service_client --draw_square (std_srvs/Empty)--> square_service_server`,
  `rotate_action_client <--rotate (turtlebot3_midterm_interfaces/Rotate)--> rotate_action_server`
- สกรีนช็อตอย่างละ 1 รูปของ section A, B, C ตอนทำงานจริง
- ค่า Kp ที่เลือกใช้จริง (จากการทดลองของคุณเอง ไม่ใช่ 1.0 เฉยๆ ถ้าคุณ
  ปรับค่าอื่น) พร้อมอธิบายว่าลองค่าไหนมาบ้าง แล้วทำไมถึงเลือกค่านี้
- Reflection สั้นๆ: ส่วนไหนยากที่สุด ครั้งหน้าจะทำต่างไปอย่างไร
- ถ้าใช้ AI ช่วย ต้องระบุว่าใช้ตรงไหน แก้ไขอะไรต่อหลังจากนั้น
  (เช่น "ให้ AI ร่างโครง P controller มา แล้วปรับ Kp และเพิ่มการ clamp
  ความเร็วสูงสุดเอง")

---

## ขั้นตอนที่ 7: ส่งงาน (ทำเป็นกลุ่ม 2 คน — ส่งครั้งเดียวต่อกลุ่ม)

ส่ง 3 ไฟล์ผ่าน Google Classroom โดยมีชื่อ+รหัสทั้งสองคนกำกับทุกไฟล์:

1. **โค้ด**: บีบอัดทั้ง workspace (หรืออย่างน้อยทั้งสองแพ็กเกจ) เป็นไฟล์เดียว
   ```bash
   cd ~/ros2_ws/src
   zip -r turtlebot3_midterm_GroupXX.zip turtlebot3_midterm turtlebot3_midterm_interfaces
   ```
2. **วิดีโอ**: ไฟล์ 3–5 นาที หรือลิงก์ที่เปิดสิทธิ์ดูได้
3. **รายงาน**: PDF 2–3 หน้าตามข้อ 6

ส่งไม่ครบ 3 อย่าง = ถือว่าส่งไม่สมบูรณ์
