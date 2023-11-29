# ULog Information

## Logging start time
`Logging start time: 0:00:01, duration: 0:02:20`

## Dropouts
`Dropouts: count: 1, total duration: 0.0 s, max: 3 ms, mean: 3 ms`

## Info Messages
- **sys_mcu**: STM32F76xxx, rev. Z
- **sys_name**: PX4
- **sys_os_name**: NuttX
- **sys_os_ver**: ec20f2e6c5cc35b2b9bbe942dea55eabb81297b6
- **sys_os_ver_release**: 134349055
- **sys_toolchain**: GNU GCC
- **sys_toolchain_ver**: 9.3.1 20200408 (release)
- **sys_uuid**: 000200000000203331354e30501000450029
- **time_ref_utc**: 0
- **ver_data_format**: 1
- **ver_hw**: MODALAI_FC_V1
- **ver_hw_subtype**: V110
- **ver_sw**: a44c6769ea3daae32e91ec73db33c3d3c00bcaba
- **ver_sw_branch**: feature/heightSwitchChecks
- **ver_sw_release**: 17498880
- **ver_vendor_sw_release**: 16777216

## Info Multiple Messages (Verbose)
- **boot_console_output**: [['sercon: Registering CDC/ACM serial driver\nsercon: Successfully registered the CDC/ACM serial driver\nHW arch: MODALAI_FC_V1\nHW type: V110\nHW version: 0x00000001\nHW revision: 0x00000000\nFW git-hash: a44c6769ea3daae32e91ec', '73db33c3d3c00bcaba\nFW version: 1.11.3 0 (17498880)\nFW git-branch: feature/heightSwitchChecks\nOS: NuttX\nOS version: Release 8.2.0 (134349055)\nOS git-hash: ec20f2e6c5cc35b2b9bbe942dea55eabb81297b6\nBuild datetime: Jul 29 2', '022 09:50:10\nBuild uri: localhost\nToolchain: GNU GCC, 9.3.1 20200408 (release)\nPX4GUID: 000200000000203331354e30501000450029\nMCU: STM32F76xxx, rev. Z\nINFO  [param] selected parameter default file /fs/mtd_params\nINFO  [t', "une_control] Publishing standard tune 1\nBoard defaults: /etc/init.d/rc.board_defaults\nConfiguring VOXL-Flight - V110\nINFO  [dataman] Unknown restart, data manager file '/fs/microsd/dataman' size is 362560 bytes\nBoard se", "nsors: /etc/init.d/rc.board_sensors\nINFO  [modalai_esc] Opened UART ESC device\nvoxlpm #0 on I2C bus 3 (external, equal to '-b 3')\nvoxlpm #1 on I2C bus 3 (external, equal to '-b 3')\nicm42688p #0 on SPI bus 2 (devid=0x26)", '\nicm20602 #0 on SPI bus 1 (devid=0x38)\nbmp388 #0 on I2C bus 4\nBoard extras: /etc/init.d/rc.board_mavlink\nINFO  [mavlink] mode: Config, data rate: 800000 B/s on /dev/ttyACM0 @ 57600B\nStarting MAVLink on /dev/ttyS6\nINFO  ', '[mavlink] mode: Normal, data rate: 1200 B/s on /dev/ttyS6 @ 57600B\nERROR [mavlink] offboard mission init failed (-1)\nStarting MAVLink on /dev/ttyS4\nINFO  [mavlink] mode: Onboard, data rate: 46080 B/s on /dev/ttyS4 @ 921', '600B\nINFO  [tune_control] Publishing standard tune 2\nINFO  [init] Mixer: /etc/mixers/quad_x.main.mix on /dev/uart_esc\nERROR [param] Parameter SENS_EN_PX4FLOW not found\nINFO  [logger] logger started (mode=all)\nINFO  [log', 'ger] Start file log (type: full)\n\nNuttShell (NSH)\nnsh> \x1b[KINFO  [logger] [logger] /fs/microsd/log/sess024/log001.ulg\nINFO  [logger] Opened full log file: /fs/microsd/log/sess024/log001.ulg\n']]
- **perf_counter_preflight**: [['logger_sd_fsync_mission: 0 events, 0us elapsed, 0.00us avg, min 0us max 0us 0.000us rms', 'logger_sd_write_mission: 0 events, 0us elapsed, 0.00us avg, min 0us max 0us 0.000us rms', 'logger_sd_fsync: 0 events, 0us elapsed, 0.00us avg, min 0us max 0us 0.000us rms', 'logger_sd_write: 0 events, 0us elapsed, 0.00us avg, min 0us max 0us 0.000us rms', 'navigator: 1 events, 701us elapsed, 701.00us avg, min 701us max 701us   infus rms', 'land_detector: cycle: 3 events, 320us elapsed, 106.67us avg, min 12us max 296us 163.967us rms', 'turtle_control: cycle: 0 events, 0us elapsed, 0.00us avg, min 0us max 0us 0.000us rms', 'mc_pos_control: cycle time: 0 events, 0us elapsed, 0.00us avg, min 0us max 0us 0.000us rms', 'mc_hover_thrust_estimator: cycle time: 0 events, 0us elapsed, 0.00us avg, min 0us max 0us 0.000us rms', 'mc_att_control: cycle: 0 events, 0us elapsed, 0.00us avg, min 0us max 0us 0.000us rms', 'mc_rate_control: cycle: 73 events, 1722us elapsed, 23.59us avg, min 14us max 547us 62.183us rms', 'ekf2: update: 31 events, 146us elapsed, 4.71us avg, min 3us max 8us 0.824us rms', 'rc_input: publish interval: 0 events, 0.00 avg, min 0us max 0us 0.000us rms', 'rc_input: cycle time: 64 events, 470us elapsed, 7.34us avg, min 5us max 34us 5.428us rms', 'mavlink: send_start tx buffer full: 0 events', 'mavlink: send_bytes error: 0 events', 'mavlink: tx run interval: 26 events, 4078.19 avg, min 2351us max 13435us 2823.989us rms', 'mavlink: tx run elapsed: 26 events, 9596us elapsed, 369.08us avg, min 105us max 4674us 896.862us rms', 'mavlink: send_start tx buffer full: 0 events', 'mavlink: send_bytes error: 0 events', 'mavlink: tx run interval: 10 events, 10012.70 avg, min 9446us max 15238us 2070.886us rms', 'mavlink: tx run elapsed: 10 events, 1504us elapsed, 150.40us avg, min 77us max 698us 192.967us rms', 'mavlink: send_start tx buffer full: 0 events', 'mavlink: send_bytes error: 0 events', 'mavlink: tx run interval: 0 events, 0.00 avg, min 0us max 0us 0.000us rms', 'mavlink: tx run elapsed: 0 events, 0us elapsed, 0.00us avg, min 0us max 0us 0.000us rms', 'vehicle_imu: gyro data gap: 1 events', 'vehicle_imu: gyro update interval: 152 events, 2480.50 avg, min 2400us max 2582us 17.585us rms', 'vehicle_imu: accel data gap: 1 events', 'vehicle_imu: accel update interval: 152 events, 2480.50 avg, min 2400us max 2582us 17.585us rms', 'vehicle_imu: gyro data gap: 1 events', 'vehicle_imu: gyro update interval: 152 events, 2498.15 avg, min 2456us max 2569us 11.552us rms', 'vehicle_imu: accel data gap: 1 events', 'vehicle_imu: accel update interval: 152 events, 2498.15 avg, min 2456us max 2569us 11.552us rms', 'vehicle_air_data: cycle: 7 events, 231us elapsed, 33.00us avg, min 15us max 112us 35.393us rms', 'sensors: 50 events, 2947us elapsed, 58.94us avg, min 34us max 531us 68.635us rms', 'bmp388: comms errors: 0 events', 'bmp388: measure: 12 events, 13502us elapsed, 1125.17us avg, min 1086us max 1243us 53.598us rms', 'bmp388: read: 11 events, 10514us elapsed, 955.82us avg, min 941us max 1020us 25.420us rms', 'icm20602: DRDY missed: 0 events', 'icm20602: FIFO reset: 1 events', 'icm20602: FIFO overflow: 0 events', 'icm20602: FIFO empty: 0 events', 'icm20602: bad transfer: 0 events', 'icm20602: bad register: 0 events', 'icm42688p: DRDY missed: 0 events', 'icm42688p: FIFO reset: 1 events', 'icm42688p: FIFO overflow: 0 events', 'icm42688p: FIFO empty: 0 events', 'icm42688p: bad transfer: 0 events', 'icm42688p: bad register: 0 events', 'voxlpm: comms_errors: 0 events', 'voxlpm: sample: 6 events, 9320us elapsed, 1553.33us avg, min 1501us max 1692us 74.422us rms', 'voxlpm: comms_errors: 0 events', 'voxlpm: sample: 6 events, 9285us elapsed, 1547.50us avg, min 1505us max 1628us 58.305us rms', 'adc: sample: 285 events, 929us elapsed, 3.26us avg, min 2us max 80us 5.535us rms', 'modalai_esc: output update interval: 74 events, 2878.34 avg, min 1991us max 31997us 3462.687us rms', 'modalai_esc: cycle: 80 events, 118816us elapsed, 1485.20us avg, min 5us max 2939us 523.630us rms', 'control latency: 73 events, 136119us elapsed, 1864.64us avg, min 1359us max 2344us 293.367us rms', 'rc_update: 0 events, 0us elapsed, 0.00us avg, min 0us max 0us 0.000us rms', 'load_mon: cycle: 2 events, 215us elapsed, 107.50us avg, min 3us max 212us 147.785us rms', 'dataman: write: 0 events, 0us elapsed, 0.00us avg, min 0us max 0us 0.000us rms', 'dataman: read: 5 events, 111643us elapsed, 22328.60us avg, min 33us max 91228us 39498.469us rms', 'dma_alloc: 5 events', 'param_set: 187 events, 8899us elapsed, 47.59us avg, min 3us max 94us 24.906us rms', 'param_get: 2695 events, 10333us elapsed, 3.83us avg, min 2us max 348us 9.371us rms', 'param_find: 918 events, 3799us elapsed, 4.14us avg, min 1us max 50us 2.393us rms', 'param_export: 0 events, 0us elapsed, 0.00us avg, min 0us max 0us 0.000us rms']]
- **perf_top_preflight**: [[' PID COMMAND                   CPU(ms) CPU(%)  USED/STACK PRIO(BASE) STATE FD', '   0 Idle Task                     682 45.054   208/  512   0 (  0)  READY  3', '   1 hpwork                          0  0.000   344/ 1260 249 (249)  w:sig  3', '   2 lpwork                          0  0.000   344/ 1612  50 ( 50)  w:sig  3', '   3 init                          861  0.000  2064/ 2924 100 (100)  w:sem  3', '   4 wq:manager                      1  0.000   424/ 1252 255 (255)  w:sem  5', ' 390 log_writer_file               272  0.000   608/ 1164  60 ( 60)  w:sem  4', '  24 wq:hp_default                   7  0.399  1084/ 1900 240 (240)  w:sem  5', '  26 dataman                         0  0.000   768/ 1204  90 ( 90)  w:sem  4', '  28 wq:lp_default                   0  0.000  1048/ 1700 205 (205)  w:sem  5', ' 149 wq:I2C3                        16  0.099   892/ 1468 244 (244)  w:sem  5', ' 157 wq:SPI2                        41  2.697  1736/ 2332 252 (252)  w:sem  5', ' 159 wq:SPI1                        35  2.297  1580/ 2332 253 (253)  w:sem  5', ' 166 wq:I2C4                         4  0.299   876/ 1468 243 (243)  w:sem  5', ' 222 wq:nav_and_controllers         62  4.495  2104/ 7196 241 (241)  w:sem  5', ' 224 wq:rate_ctrl                   61  4.895  1184/ 1660 255 (255)  w:sem  5', ' 228 commander                      18  0.999  1280/ 3212 140 (140)  READY  6', ' 229 commander_low_prio              0  0.000   840/ 2996  50 ( 50)  w:sem  6', ' 236 mavlink_if0                     1  0.000  1376/ 2572 100 (100)  w:sig  3', ' 309 mavlink_if1                    13  1.098  1480/ 2484 100 (100)  w:sig  4', ' 310 mavlink_rcv_if1                10  0.399  2536/ 4068 175 (175)  w:sem  4', ' 318 mavlink_if2                    55  4.895  1808/ 2484 100 (100)  w:sig  4', ' 319 mavlink_rcv_if2                10  0.399  2520/ 4068 175 (175)  w:sem  4', ' 330 wq:UART5                        5  0.399   704/ 1396 233 (233)  w:sem  5', ' 345 wq:attitude_ctrl                0  0.000   432/ 1668 242 (242)  w:sem  5', ' 361 navigator                       2  0.099   960/ 1764 105 (105)  w:sem  5', ' 380 logger                         80  2.897  2712/ 3644 230 (230)  RUN    4', '', 'Processes: 26 total, 3 running, 23 sleeping, max FDs: 15', 'CPU usage: 26.37% tasks, 28.57% sched, 45.05% idle', 'DMA Memory: 5120 total, 1536 used 1536 peak', 'Uptime: 2.367s total, 0.682s idle']]

## Data Points Information
| Name (multi id, message size in bytes) | number of data points | total bytes |
| --- | --- | --- |
| actuator_armed (0, 20) | 289 | 5780 |
| actuator_controls_0 (0, 48) | 39128 | 1878144 |
| actuator_outputs (0, 76) | 40043 | 3043268 |
| battery_status (0, 112) | 470 | 52640 |
| commander_state (0, 9) | 289 | 2601 |
| cpuload (0, 16) | 282 | 4512 |
| debug_key_value (0, 22) | 3 | 66 |
| debug_vect (0, 30) | 13546 | 406380 |
| ekf2_timestamps (0, 20) | 27869 | 557380 |
| estimator_innovation_test_ratios (0, 144) | 683 | 98352 |
| estimator_innovation_variances (0, 144) | 683 | 98352 |
| estimator_innovations (0, 144) | 683 | 98352 |
| estimator_sensor_bias (0, 56) | 138 | 7728 |
| estimator_status (0, 284) | 683 | 193972 |
| hover_thrust_estimate (0, 41) | 189 | 7749 |
| input_rc (0, 66) | 143 | 9438 |
| logger_status (0, 35) | 141 | 4935 |
| manual_control_setpoint (0, 67) | 6997 | 468799 |
| multirotor_motor_limits (0, 10) | 141 | 1410 |
| position_setpoint_triplet (0, 344) | 1 | 344 |
| rate_ctrl_status (0, 24) | 7012 | 168288 |
| safety (0, 12) | 138 | 1656 |
| sensor_accel (0, 43) | 1405 | 60415 |
| sensor_accel (1, 43) | 1405 | 60415 |
| sensor_baro (0, 32) | 1405 | 44960 |
| sensor_combined (0, 45) | 27869 | 1254105 |
| sensor_gyro (0, 40) | 1405 | 56200 |
| sensor_gyro (1, 40) | 1405 | 56200 |
| sensor_preflight (0, 20) | 591 | 11820 |
| sensor_selection (0, 20) | 1 | 20 |
| system_power (0, 23) | 282 | 6486 |
| telemetry_status (0, 104) | 141 | 14664 |
| telemetry_status (1, 104) | 140 | 14560 |
| test_motor (0, 22) | 1 | 22 |
| trajectory_setpoint (0, 76) | 334 | 25384 |
| vehicle_air_data (0, 36) | 1621 | 58356 |
| vehicle_angular_acceleration (0, 28) | 38958 | 1090824 |
| vehicle_angular_velocity (0, 28) | 39066 | 1093848 |
| vehicle_attitude (0, 41) | 25827 | 1058907 |
| vehicle_attitude_setpoint (0, 57) | 15868 | 904476 |
| vehicle_command (0, 52) | 7 | 364 |
| vehicle_control_mode (0, 26) | 289 | 7514 |
| vehicle_imu (0, 53) | 282 | 14946 |
| vehicle_imu (1, 53) | 282 | 14946 |
| vehicle_imu_status (0, 52) | 141 | 7332 |
| vehicle_imu_status (1, 52) | 141 | 7332 |
| vehicle_land_detected (0, 17) | 145 | 2465 |
| vehicle_local_position (0, 156) | 1301 | 202956 |
| vehicle_local_position_setpoint (0, 76) | 667 | 50692 |
| vehicle_rates_setpoint (0, 32) | 25739 | 823648 |
| vehicle_status (0, 51) | 289 | 14739 |
| vehicle_status_flags (0, 38) | 289 | 10982 |
| vehicle_visual_odometry (0, 254) | 3664 | 930656 |
| vehicle_visual_odometry_aligned (0, 254) | 631 | 160274 |

