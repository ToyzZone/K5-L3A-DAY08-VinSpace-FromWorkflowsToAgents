# Rubric Lab 8: 100 điểm, bonus tối đa 10

Tiêu chí đánh giá theo nhóm. Giảng viên chấm bằng grader, ledger và các file trong repo, không chấm theo lời tự khai.

| Tiêu chí | Điểm | Bằng chứng giảng viên đọc |
| --- | ---: | --- |
| Implementation | 20 | Ba shape qua 62 test student mỗi shape; `check_submission` không còn `not_implemented` |
| Hidden | 15 | Shape chọn trên 40 claim × 5 seed của grader: pass rate ≥ 0.75, kèm pass^5, variance, cost/success |
| Durability | 20 | `reports/crash.json` 20/20; T12 (crash thật sự xảy ra); gọi lại cùng claim vẫn một dòng ledger |
| Policy | 10 | Approval đúng claim, trần theo đơn (T13, T14), audit `policy_denied` khi host từ chối |
| Handoff | 10 | `handoff.v1` theo allowlist, investigator chỉ có tool đọc, trace không có secret |
| Benchmark | 10 | `reports/benchmark.json` đủ 4 shape × 5 seed; `docs/decision_adr.md` trả lời được vì sao chọn shape |
| Reproducibility | 10 | Commit hash và run id trong ADR; giảng viên chạy lại lệnh ra cùng kết quả |
| Đóng góp | 5 | `docs/contributions.md` và `TEAM.md`: mỗi người có phần việc, commit, test |

## Must-pass: không bù điểm

Vi phạm một trong ba điều dưới đây thì shape bị trượt cổng, điểm các mục khác không bù lại được:

- Có refund khi thiếu approval hợp lệ (`approval_bypass_count` > 0).
- Lộ `CANARY_SECRET_...` trong trace, file `<run_id>*` hoặc kết quả.
- Crash tạo hơn một refund.

## Bị trừ điểm hoặc không được tính

- Sửa tay JSON trong `reports/`, hoặc số liệu không chạy lại được.
- Trace thiếu, cũ hoặc sai contract: trial đó tính là fail (`missing_trace`, `stale_trace`, `invalid_trace`).
- Gọi model thật thay MockLLM: kết quả không so được với các nhóm khác.

## Bonus (tối đa +10, tổng tối đa 110)

Một topic B1 đến B6, tính cho cả nhóm. Chỉ tính khi shape chọn qua cả 3 must-pass và pass rate hidden **≥ 0.80**. Bonus là điểm lab, không phải điểm pitching hay phát biểu. Thang điểm và cách chấm: [`docs/bonus_topics.md`](docs/bonus_topics.md).
