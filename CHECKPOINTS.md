# Checkpoints Lab 8

Buổi lab 13:30 đến 17:30 (lab sáng dùng cùng lịch, dời theo giờ của lớp). Mỗi checkpoint có nhiệm vụ, sản phẩm, điều cần hiểu và một bước tự kiểm tra.

## Checkpoint M0 (13:30): cài đặt, chia vai

- **Nhiệm vụ:** cài môi trường, chạy smoke, đọc output contract và trace contract trong README, chia vai theo shape.
- **Sản phẩm:** `python -m lab8.smoke` pass trên máy từng người.
- **Cần hiểu:** host (policy, ledger, handoff) đã có sẵn; nhóm chỉ viết ba shape.
- **Tự kiểm tra:** `python -m pytest -q` ra `N passed, 248 deselected`, không có `failed`. Ma trận student lúc mới clone: 186 failed, 62 passed.

## Checkpoint M1 (13:45): ba shape

- **Nhiệm vụ:** viết `workflow.py`, `single.py`, `orchestrator.py` theo hướng dẫn đầu mỗi file.
- **Sản phẩm:** ba shape trả `RunResult` hợp lệ, cùng chữ ký `run_claim`.
- **Cần hiểu:** tiền do code tính (`compute_compensation`), model không chọn số tiền và không commit refund.
- **Tự kiểm tra:** `python -m pytest -q -m student -o addopts= -k workflow` (đổi `-k` theo shape) xanh 62 test.

## Checkpoint M2 (14:30): handoff, ledger, crash

- **Nhiệm vụ:** handoff theo allowlist cho orchestrator, ghi tiền qua `durability.issue_refund`, truyền `crash_at`.
- **Sản phẩm:** shape mới qua test host; `python -m pytest -q` vẫn xanh.
- **Cần hiểu:** sau crash, ledger quyết định có ghi lại hay không, checkpoint thì không. Tóm tắt bằng LLM không thay được allowlist.
- **Tự kiểm tra:** `python -m lab8.demo.buggy_workflow` in `unsafe refund rows: 2`; shape của nhóm qua T12.

## Checkpoint M3 (15:30): 20 crash, approval, secret

- **Nhiệm vụ:** chạy crash suite, kiểm approval đúng claim, quét secret trong trace. Hạn chót đăng ký topic bonus tự đề xuất.
- **Sản phẩm:** `reports/crash.json` với `crash_safety` = `20/20`.
- **Cần hiểu:** ba must-pass không bù điểm: approval, secret, crash.
- **Tự kiểm tra:** không có chuỗi `CANARY_SECRET_` trong thư mục `traces/`.

## Checkpoint M4 (16:15): benchmark, chọn shape

- **Nhiệm vụ:** benchmark 4 shape × 5 seed trên ≥ 10 claim public, rồi tự kiểm trên `student_drop/` giảng viên phát.
- **Sản phẩm:** `reports/benchmark.json`, `docs/decision_adr.md` có shape chọn và số đo.
- **Cần hiểu:** pass rate, pass^5, seed variance, cost/success ([`docs/metrics.md`](docs/metrics.md)); vì sao swarm fail ở seed 55.
- **Tự kiểm tra:** ADR trả lời được: pass nhỉnh hơn có đáng cost và variance cao hơn không.

## 17:00: nộp

- **Nhiệm vụ:** README, hash, run id, `check_submission`.
- **Sản phẩm:** repo theo [`SUBMISSION.md`](SUBMISSION.md).
- **Tự kiểm tra:** `python -m lab8.check_submission` ra `0 FAIL`.
