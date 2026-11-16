# Nộp bài Lab 8

Bài nhóm. Nhóm nộp **một repo** (repo của trưởng nhóm), nhưng **mỗi cá nhân** vẫn tự nộp link repo đó lên LMS bằng tài khoản cá nhân của mình. Ai không nộp link thì không có điểm, dù nhóm đã nộp.

## Đặt tên repo nhóm

```text
K5-L3-DAY08-TenNhom-WorkflowsToAgents
```

Không dấu, không khoảng trắng, các phần ngăn cách bằng `-`. `TenNhom` viết liền, không dấu. Repo phải public, hoặc đã mời giảng viên vào.

## Cấu trúc phải nộp

| File | Nội dung |
| --- | --- |
| `lab8/shapes/workflow.py`, `single.py`, `orchestrator.py` | Ba shape, giữ nguyên chữ ký `run_claim` |
| `reports/benchmark.json` | Do `lab8.benchmark` tạo: đủ 4 shape, seed `11,22,33,44,55`, ≥ 10 claim |
| `reports/crash.json` | Do `lab8.crash_test` tạo, `crash_safety` = `20/20` |
| `docs/decision_adr.md` | Shape chọn, commit hash, run id, số đo |
| `docs/architecture.md`, `docs/research_card.md` | Đã điền |
| `docs/contributions.md` | Mỗi thành viên một dòng |
| `TEAM.md` | Danh sách thành viên và mục cá nhân |
| `docs/bonus_report.md` | Chỉ khi làm bonus |

Không sửa tay file JSON trong `reports/`. Giảng viên chạy lại đúng các lệnh tạo ra chúng.

## Deadline (giờ Việt Nam, GMT+7)

| Ca lab | Hạn nộp |
| --- | --- |
| Lab sáng | **23h59** cùng ngày lab |
| Lab chiều / tối | **11h59** ngày hôm sau |

Coach có thể gia hạn tối đa 48 giờ, báo trước cho cả lớp.

## Checklist trước khi nộp

1. `python -m pytest -q` xanh.
2. Chạy benchmark và crash test để tạo hai file trong `reports/` (lệnh ở README, mục *Các lệnh trong buổi lab*).
3. Commit, chạy `git rev-parse --short HEAD`, ghi hash và run id vào `docs/decision_adr.md`, commit tiếp.
4. `python -m lab8.check_submission` ra `0 FAIL`, rồi push.
5. Mỗi thành viên nộp link repo lên LMS.

Các mục `check_submission` kiểm tra: README, mục *Checklist nộp bài*.
