# 训练师仿真实验 · 第十、十一章（Webots）

「训练师」全类型模块化机器人教研套装 —— **仿真设计篇 第十章（10.1–10.6）与第十一章（11.1–11.10）**，共 16 个实验的 Webots 工程与免安装实验包。

- 运行环境：Windows 10/11 64 位，Webots R2023b，Python 3.8 + robodyno 1.7.2 + OpenCV + NumPy
- 模型库：老师提供的 robodyno_webots PROTO（未修改）；世界文件与控制器按实验指导书的关键代码编写
- **免安装包**：见本仓库 **Releases** 页，下载 `TeachKit_Labs_Windows_v1.0.zip`（约 466 MB），内含 Webots 运行时与 Python，解压即用，无需安装、无需联网
  - SHA-256：`B8CAD020462764C8118727DB429C17C07BE6C1B66D4A9B41F5A276601B41B141`

## 快速开始（拿到免安装包的人）

1. 解压 ZIP 到短路径（如 `C:\Lab`），不要直接在压缩包预览窗口里运行；
2. 双击 `RoboKit_Labs\开始实验.cmd`，在启动台里选择实验 →「开始仿真」；
3. 观察 Webots 三维视图与底部 Console，按需自行截图（建议全屏，保留右下角系统时间）；
4. 换实验前先关闭当前 Webots 窗口；**11.6 手眼标定必须先于 11.7 / 11.8 运行**（包内已附一份预置标定，直接看 11.7/11.8 也不会卡住，复现实验请自己先跑 11.6）。

## 实验清单

| 编号 | 实验 | 世界文件 | 观察与截图时机 |
|---|---|---|---|
| 10.1 | 转动关节模块 | `w10_1_motor.wbt` | 橙杆转动中、到位后各一张（保留 pos/vel） |
| 10.2 | 直线滑台模块 | `w10_2_slider.wbt` | 滑台到 −0.10 m 稳定时 |
| 10.3 | 夹持器模块 | `w10_3_gripper.wbt` | 张/合各一张（两指行程较小） |
| 10.4 | 气动吸盘模块 | `w10_4_vacuum.wbt` | 红块贴杯口与释放落下 |
| 10.5 | 传送带模块 | `w10_5_conveyor.wbt` | 正转、反转各一张，红蓝块随带运动 |
| 10.6 | 摄像头模块 | `w10_6_camera.wbt` | 相机预览 + 控制台像素坐标 |
| 11.1 | 关节空间滑条 | `w11_1_joint_slider.wbt` | 小幅拖动 J1/J2，滑条窗与臂同屏 |
| 11.2 | 笛卡尔空间滑条 | `w11_2_cartesian_slider.wbt` | 拖动 X/Y 后拍新位姿与滑条值 |
| 11.3 | 六轴画圆 | `w11_3_draw_circle.wbt` | 笔尖在水平画板上画出红圈 |
| 11.4 | 定点搬运（吸盘） | `w11_4_vacuum_handling.wbt` | 吸起、放置、done |
| 11.5 | 定点搬运（夹爪） | `w11_5_gripper_handling.wbt` | 夹起、叠放 |
| 11.6 | 手眼标定 | `w11_6_calibration.wbt` | 网格采集过程；末行 `eye2arm.json written` |
| 11.7 | 小场景视觉搬运（吸盘） | `w11_7_visual_small_vacuum.wbt` | 识别→抓取→放置→all done |
| 11.8 | 小场景视觉搬运（夹爪） | `w11_8_visual_small_gripper.wbt` | 同上（夹爪） |
| 11.9 | 大场景传送带搬运（吸盘） | `w11_9_visual_large_vacuum.wbt` | 送料→吸取→放置→all done |
| 11.10 | 大场景传送带搬运（夹爪） | `w11_10_visual_large_gripper.wbt` | 同上（夹爪） |

## 仓库结构

```
kit/worlds        16 个实验世界（.wbt）
kit/controllers   各实验控制器（Python）+ 共用模块 common/
kit/shared        eye2arm.json（11.6 手眼标定结果，11.7/11.8 使用）
deploy            打包与启动台脚本（build.py / launch.py / labs.py / start.cmd / guide.txt）
docs              软件来源与许可说明
使用说明.md       面向使用者的完整操作说明（与包内文件一致）
```

> 模型库 `protos/` 体积较大（221 MB），未纳入仓库；完整内容在 Release 的免安装包中。需要单独源码可与维护者联系获取。

## 与指导书代码的差异（如实记录）

实验按指导书关键代码实现，为在 Webots R2023b 中稳定运行做了以下适配：

1. **电机模式**：robodyno 的 Webots 电机默认模式为 UNKNOWN，需显式设置 `position_mode()` / `position_track_mode()`，并按设备上限设置可用力矩；
2. **夹爪**：模型的 `RobotHand` 有两个手指电机（`0x1A::motor` / `0x1A::right`），控制器同时驱动两根并合拢到 10 mm，场景接触摩擦设为 5，保证 24 mm 方块可被夹起；
3. **气动吸附（10.4 演示）**：Webots 的 Connector 在该装配下不稳定，用 Supervisor 实现等价的"吸住/松开"；
4. **传送带（10.5、11.9、11.10）**：Track 对块体无有效承托摩擦，方块由 Supervisor 按带速运送（10.5 用 WORKPIECES 整体位移，11.9/11.10 由送料 Supervisor 推进）；
5. **控制器间通信**：`kit/shared/` 下的文件（`eye2arm.json`、`scene.txt`、`belt.txt`、`done.txt`），Windows 下原子写加入了重试；
6. **固定底座**：六轴模型使用自带 `fixedBase TRUE`（不修改 PROTO），保证底座固定在桌面。

## 软件来源与许可

- Webots R2023b：Cyberbotics，Apache-2.0；发布包保留对应版本运行文件，不含安装程序。许可见包内 `runtime/webots/LICENSE.txt`
- Webots 模型资产：<https://cyberbotics.com/webots_assets_license>
- robodyno Webots 模型库：由任课教师提供（robodyno_webots PROTO 套件）
- 实验指导书与报告模板版权归原编写方，仅供课程学习使用

详见 [docs/软件来源与许可.txt](docs/软件来源与许可.txt)。