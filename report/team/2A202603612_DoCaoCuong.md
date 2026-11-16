# Báo cáo cá nhân — 2A202603612_DoCaoCuong

## 1. Thông tin thành viên

- Họ tên: Đỗ Cao Cường
- MSSV: 2A202603612
- Email: 26ai.cuongdc@vinuni.edu.vn
- GitHub: cuongdc03

## 2. Phần việc phụ trách

**Ledger và Evaluation.** Không viết shape. Phần việc gồm:

- Kiểm tra ledger và crash safety trên cả 4 shape (T11, T12, crash suite 20/20).
- Chạy benchmark 4 shape × 5 seed, sinh `src/reports/crash.json` và `src/reports/benchmark.json`.
- Làm ablation R4 (đổi bộ seed) và điền `research_card.md`.
- Điền `decision_adr.md` (chọn `single`), bảng đóng góp trong `TEAM.md`, và `group_report.md`.

## 3. Đóng góp cụ thể

**Commit:**

- `751d094`: thêm `src/reports/benchmark.json` và `src/reports/crash.json`.
- `b5b63e2`: thêm `src/reports/ablation_seeds.json` và `src/tests/test_reports_artifacts.py`.
- `6dc9159`: điền ADR, bảng thành viên và đóng góp trong `TEAM.md`, research card.
- Commit điền `group_report.md` và báo cáo này (hash ghi sau khi commit).

**Test đã thêm:** `src/tests/test_reports_artifacts.py` (4 test):

- `test_crash_report_is_20_of_20`: `crash.json` có `count` 20, `passed` 20, `crash_safety` `20/20`.
- `test_benchmark_covers_four_shapes_ten_claims_five_seeds`: đủ 4 shape, seed `11,22,33,44,55`, ít nhất 10 claim, latency `unavailable`, giá mô phỏng.
- `test_benchmark_summary_is_recomputed_from_trials`: số tóm tắt trong `by_shape` khớp khi tính lại bằng `lab8.metrics.summarize` từ `trials`. Nhờ vậy phát hiện file bị sửa tay.
- `test_seed_ablation_removes_swarm_seed_55_failure`: bộ seed của ablation không trùng bộ gốc, swarm pass < 1.0 ở bộ gốc và = 1.0 ở bộ ablation, ba shape còn lại giữ 1.0.

**Quyết định kỹ thuật:**

- Chọn R4 cho research card, vì hợp với vai Evaluation. Biến duy nhất đổi là bộ seed. Dùng `12,23,34,46,57`, không seed nào chia hết cho 5. Lần đầu dùng `45` nên chưa thấy thay đổi; xem mục 5 của báo cáo nhóm.
- Chọn `single` trong ADR, vì cost/success thấp nhất (33.41 VND mô phỏng) và công sức triển khai thấp. Ghi rõ trong ADR rằng chênh lệch với `workflow` chỉ khoảng 2.6%, và số liệu mới ở bộ public, chưa có hidden.
- Không ghi `0` cho secret leak và approval bypass khi chưa kiểm. Trước khi ghi đã kiểm: `CANARY_SECRET` chỉ xuất hiện trong `data/public_claims.jsonl` (dữ liệu đầu vào), 70/70 trial `single` qua tiêu chí chấm, và 20 test về secret, authorization, approval, trace contract xanh.

## 4. Bằng chứng

- Commit: `751d094`, `b5b63e2`, `6dc9159` trên nhánh `cuong/ledger-eval-reports`.
- `python -m lab8.crash_test --count 20 --out reports/crash.json`: `crash_safety 20/20`.
- `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json`:

| Shape | Pass | Pass^5 | Variance | Cost/success (VND, mô phỏng) |
| --- | --- | --- | --- | --- |
| workflow | 1.000 | 1.000 | 0 | 34.29 |
| single | 1.000 | 1.000 | 0 | 33.41 |
| orchestrator | 1.000 | 1.000 | 0 | 57.15 |
| swarm | 0.986 | 0.929 | 0.000816 | 49.57 |

- Ablation: `python -m lab8.benchmark ... --seeds 12,23,34,46,57 --out reports/ablation_seeds.json`: swarm lên 1.000 / 1.000 / 0.
- `python -m pytest -q -m student -o addopts=`: 248 passed. `python -m pytest -q`: 113 passed.
- `python -m lab8.check_submission`: `0 FAIL`.

## 5. Công cụ AI đã dùng

- **Claude Code (Claude).** Dùng để: đọc repo và tóm tắt phần việc của vai Ledger và Evaluation; chạy lệnh test, crash suite, benchmark; viết `test_reports_artifacts.py`; soạn nháp ADR, research card, bảng đóng góp và báo cáo nhóm.
- **Cách tự kiểm tra:**
  - Mọi con số lấy từ output của lệnh trên máy, hoặc đọc lại từ `benchmark.json` và `crash.json`, không chép từ trí nhớ.
  - Test mới tính lại metric từ `trials` bằng `lab8.metrics.summarize` để đối chiếu với số lưu trong file.
  - Lỗi của AI đã bắt được: chọn seed ablation `45` chia hết cho 5 nên kết quả không đổi; phát hiện nhờ so với kết quả dự kiến, rồi đổi seed và chạy lại. `pytest -k single` còn khớp cả shape khác, nên đếm fail theo hậu tố từng shape.
  - Đối chiếu commit hash và tên test trong `TEAM.md` với `git log` và `git show --stat`.
  - Chạy `check_submission` sau khi điền tài liệu.

## 6. Tự đánh giá

**Làm tốt**

- Mọi số trong ADR và báo cáo đều truy được về file do tool sinh ra (`benchmark.json`, `crash.json`, `ablation_seeds.json`), không sửa tay. Test `test_benchmark_summary_is_recomputed_from_trials` tính lại metric từ `trials` để phát hiện file bị sửa.
- Không ghi `0` cho secret leak và approval bypass khi chưa kiểm. Đã grep `CANARY_SECRET` và chạy các test liên quan trước khi ghi.
- Ablation R4 có hypothesis kiểm được, chỉ đổi một biến (seed) và kết quả khớp dự đoán. Khi chọn sai seed `45`, mình nhận ra từ kết quả không đổi, sửa và chạy lại.

**Còn yếu**

- Chưa chạy tự kiểm hidden trên `student_drop/`. Pass 1.000 chỉ đúng trên bộ public 14 claim với MockLLM, nên lý do chọn `single` (cost thấp nhất, chênh `workflow` khoảng 2.6%) chưa được kiểm trên hidden.
- Không viết shape nào. Phần đóng góp code của mình là test và báo cáo, ít hơn ba bạn viết shape.
- `crash_test` kiểm lớp host chứ không kiểm từng shape, nên mình chỉ dựa vào T11, T12 để nói shape truyền `crash_at` đúng. Chưa viết test riêng cho việc này.
- Ablation chỉ đổi một biến. Chưa thử prompt hay tool.
- Chưa đọc toàn văn paper R4, chỉ dựa vào mô tả của lớp.

**Sẽ làm khác nếu có thêm thời gian**

- Chạy tự kiểm hidden và cập nhật ADR nếu số liệu khác.
- Thêm ablation thứ hai đổi biến khác (ví dụ thứ tự claim) để tách thêm nhiễu.
- Viết test kiểm từng shape truyền `crash_at` vào `issue_refund`.
