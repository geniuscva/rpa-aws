# Team Allocation

Dự án scope classic, không có giai đoạn Team Formation (1.5 SKIP). Vì vậy toàn bộ
Bolt do một "mob" AI thực hiện — tức agent `aidlc-developer-agent` — trong một
phiên làm việc (lựa chọn staffing: một phiên chạy toàn bộ Construction). Không có
Program Board vì chỉ có một team.

Một **mob** ở đây là nhóm thực thi một Bolt; với dự án solo/local, mob là một
agent developer duy nhất.

| Bolt | Unit | Mob/chủ sở hữu |
|---|---|---|
| Bolt 1 | U1 ConsumeData | aidlc-developer-agent |
| Bolt 2 | U2 DataEntryAccuity | aidlc-developer-agent |
| Bolt 3 | U3 DataEntryTraCuuThue | aidlc-developer-agent |
| Bolt 4 | U4 DataEntryAMLD | aidlc-developer-agent |
| Bolt 5 | U5 TongHopVaGuiMail | aidlc-developer-agent |

Chế độ chạy Construction: unit-major, serial, một phiên (solo). Mỗi Unit chạy
trọn vẹn thiết kế + code + kiểm rồi tới checkpoint hoàn thành của Unit đó.
