# Báo cáo cá nhân — 2A202603637_NguyenMinhThong

## 1. Thông tin thành viên

- Họ tên: Nguyễn Minh Thông
- MSSV: 2A202603637
- Email: 26ai.thongnm@vinuni.edu.vn
- GitHub: [ToyzZone](https://github.com/ToyzZone)

## 2. Phần việc phụ trách

Shape B `single` (`src/lab8/shapes/single.py`): một vòng ReAct qua `lab8.runtime.run_react`, tối đa 8 bước. Model chỉ được chọn tool đọc; sau vòng lặp, code của shape tính quote bằng `compute_compensation` và gọi `durability.issue_refund` với quote đầy đủ. Gồm cả phần CP3 của shape này: truyền `crash_at`, không bắt `InjectedCrash` (T11, T12), và trace không ghi claim row, order row thô hay ticket.

## 3. Đóng góp cụ thể

**Commit** (nhánh `thong_branch`, merge vào `main` qua PR #2, merge commit `00ef9d5`):

- `1db513a` — viết shape `single` (`src/lab8/shapes/single.py`) và 2 test.
- `3cc59d8` — tạo báo cáo cá nhân này.

**Test đã thêm** (`src/tests/test_single_shape.py`, chạy trong cổng host `python -m pytest -q`):

- `test_model_asking_for_issue_refund_is_rejected`: thay `decide` bằng một "model" đòi gọi `issue_refund` cho C-001. Kết quả phải là `failed` / `tool_rejected`, ledger không có dòng nào, không có audit `refund_committed`.
- `test_trace_never_holds_ticket_secret_or_order_pii`: chạy `single` trên cả 14 claim public, trace không được chứa ticket, `parent_secret`, header, SĐT, địa chỉ, tên hàng, ghi chú nội bộ.

**Quyết định kỹ thuật:**

1. **Ranh giới model / code.** `decide` (phần "model", mỗi bước một lệnh MockLLM) chỉ chọn tool đọc theo thứ tự `get_claim_view` → `lookup_order` → `compute_compensation` rồi dừng. Sau vòng lặp, code đọc status và số tiền từ kết quả tool, không lấy từ câu trả lời của model, không đọc số ngày trễ trong ticket.
2. **Truyền quote đầy đủ** vào `durability.issue_refund`. Host tự trừ phần đơn đã được hoàn (T13, T14); shape tự trừ trước thì host trừ hai lần. Không gọi `lookup_refund_history` vì host đã giữ trần theo đơn, gọi thêm chỉ tốn một tool call.
3. **Trace.** Mỗi bước ReAct chỉ ghi tên tool. Ngoài ra ghi order view (chỉ các field trong `ORDER_FIELDS`), quote và quyết định cuối. Cố ý không ghi claim view (có ticket), `parent_secret`, header: ticket là dữ liệu người dùng và có thể chứa thông tin cá nhân.
4. **`run_claim` không ném lỗi.** Model đòi tool ghi hoặc tool lạ → `failed` / `tool_rejected`; hết 8 bước → `failed` / `step_cap`. Riêng `InjectedCrash` vẫn được để văng ra, vì T12 cần thấy crash xảy ra thật.

## 4. Bằng chứng

- Commit: <https://github.com/ToyzZone/K5-L3A-DAY08-VinSpace-FromWorkflowsToAgents/commit/1db513a>
- PR: <https://github.com/ToyzZone/K5-L3A-DAY08-VinSpace-FromWorkflowsToAgents/pull/2>
- Ma trận student của `single` (chạy trong `src/`): `python -m pytest -q -m student -o addopts= -k "single and not workflow and not orchestrator and not swarm"` → **62 passed**. Lệnh `-k single` trong CHECKPOINTS khớp cả tên test `test_public_single_run_cases` nên chạy cả 4 shape; phải dùng filter trên.
- Trên `main` sau khi đủ 3 shape (`e829d91`): `python -m pytest -q` → 109 passed; ma trận student cả 4 shape → 248 passed.
- Kiểm tra test có bắt được lỗi: bỏ guard `except ToolRejected` trong `single.py` → test thứ nhất đỏ; thêm dòng ghi claim view vào trace → test thứ hai đỏ. Trả code về thì cả hai xanh lại.
- Quét 62 trace `R-single-*` sinh từ ma trận student, tìm `parent_secret`, header, ticket, SĐT, địa chỉ, tên hàng, ghi chú nội bộ: 0 trace chứa chuỗi cấm.
- Một số trial chạy trên DB mới, đối chiếu với nhãn trong `data/public_claims.jsonl`:

| Run id | Test | Kết quả | Nhãn |
| --- | --- | --- | --- |
| `R-single-C-002-s55` | T02 (ticket ghi trễ 5 ngày, đơn ghi 2 ngày) | `denied`, proposal 0, không refund | `denied`, 0 |
| `R-swarm-C-002-s55` | T02, swarm đối chứng | `resolved`, refund 20.000 (tin số trong ticket) | `denied`, 0 |
| `R-single-C-013-s11` | T13 (đơn đã được hoàn đủ) | `denied`, proposal 35.000, host từ chối `order_already_refunded` | `denied`, 35.000, có `policy_denied` |
| `R-single-C-014-s11` | T14 (chỉ hoàn phần chênh) | `resolved`, proposal 150.000, ledger 120.000 | `resolved`, 150.000, ledger 120.000 |

Mỗi trial của `single` dùng 5 lệnh model và 3 tool call (cost mô phỏng khoảng 36 VND/trial trên các claim trên). Số benchmark chính thức của nhóm lấy từ `src/reports/benchmark.json`.

## 5. Công cụ AI đã dùng

Công cụ: **Claude Code** (extension trong VS Code).

Dùng vào việc:

- Đọc đề, docs và code host rồi tóm tắt luật nghiệp vụ, contract, các việc cần làm để chia việc trong nhóm.
- Viết bản đầu của `single.py` và `test_single_shape.py`, chạy test, viết mô tả PR #2.
- Kéo và chạy thử nhánh `workflow` và `orchestrator` của đồng đội (gộp tạm với `main`) trước khi merge.

Cách tự kiểm tra:

- Chạy lại ma trận student của `single` (62 passed) và cổng host sau mỗi thay đổi.
- Cố ý làm hỏng từng guard trong `single.py` để chắc test đỏ thật, không phải test luôn xanh.
- Quét trace tìm chuỗi cấm thay vì tin vào lời giải thích của AI.
- Run id và số liệu ở mục 4 lấy từ lần chạy thật, đối chiếu với nhãn trong `data/public_claims.jsonl`, không để AI tự điền.

## 6. Tự đánh giá

Đã làm được:

- Shape `single` qua đủ 62 test student, có 2 test riêng, đã merge vào `main`.
- Giữ đúng ranh giới: model không quyết số tiền, không gọi được tool ghi; trace không chứa ticket hay secret.

Giới hạn:

- Với MockLLM, `decide` thực chất là một chuỗi bước cố định, nên `single` ra cùng quyết định với workflow nhưng tốn thêm 5 lệnh model mỗi claim. Shape này chưa cho thấy lợi ích của tự chủ; với model thật thì cần đo lại.
- Chưa chạy `single` trên bộ hidden (`student_drop/`).
