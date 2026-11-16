# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm: VinSpace
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`): `751d094`

## 2. Mục tiêu và cách tiếp cận

Bài toán: xử lý yêu cầu bồi thường vận chuyển (claims) với hoàn tiền an toàn. Tiền do code tính (`compute_compensation`), không do model chọn. Chữ trong ticket là dữ liệu người dùng. Mọi lần ghi tiền đi qua cửa của host (`durability.issue_refund`: approval, trần theo đơn, idempotency, rồi mới ghi ledger).

Nhóm 4 người, chia theo gợi ý trong `TEAM.md`:

| Người | Phần việc |
| --- | --- |
| Hồ Quốc Toản | Shape A `workflow` |
| Nguyễn Minh Thông | Shape B `single` |
| Bùi Gia Huy | Shape C `orchestrator` |
| Đỗ Cao Cường | Ledger (crash, idempotency) và Evaluation (benchmark, ADR, research card) |

Swarm (Shape D) là bản tham chiếu có sẵn, dùng làm mốc so sánh. Thứ tự: ba shape được viết song song (CP2, CP3), sau đó chạy crash suite (CP4) rồi benchmark 4 shape cùng điều kiện (CP5).

## 3. Giải pháp

Ranh giới chung của cả ba shape: model (MockLLM) chỉ được chọn tool đọc hoặc soạn câu trả lời. Code của shape tính quote và là nơi duy nhất gọi `issue_refund`, với **quote đầy đủ**. Host tự trừ phần đã hoàn trước đó trên cùng đơn (T13, T14), nên shape không tự trừ để tránh trừ hai lần. Shape không bắt `InjectedCrash`, để retry sau crash đi qua ledger.

| Shape | Đọc gì | Quyết định ra sao | Model calls trung bình |
| --- | --- | --- | --- |
| `workflow` (A) | Hồ sơ qua `get_claim_view`, rồi `lookup_order` | Chuỗi bước cố định: thiếu `order_id` thì `needs_info`, đơn không thấy thì `escalated`, quote bằng 0 thì `denied`, còn lại gọi `issue_refund` | 0.00 |
| `single` (B) | Tool chỉ đọc qua `lab8.runtime.run_react`, tối đa 8 bước | Vòng ReAct chọn tool; sau vòng lặp, code tính quote và gọi `issue_refund` | 4.79 |
| `orchestrator` (C) | Điều phối dựng `handoff.v1` bằng `make_handoff`; investigator chạy 3 tool chỉ đọc (`lookup_order`, `lookup_policy`, `lookup_refund_history`) | Orchestrator tính quote từ order view của investigator rồi gọi `issue_refund`. Investigator không có tool ghi | 1.93 |

**Sanitize handoff.** Handoff chỉ lấy trường nằm trong allowlist (`ALLOWED_FIELDS`) và tool chỉ đọc. Không đưa `parent_secret`, header thô hay toàn bộ claim row vào `facts`. Tóm tắt bằng LLM không được tính là redaction.

**Trace.** Mọi nhánh return, kể cả `needs_info` và `escalated`, đều ghi trace theo contract v1 (`run_id` khớp, `events` là list). Ví dụ event: `decision`, `quote`, `order`, `handoff` (bản đã sanitize), `crash`, `refund_outcome`, `react_step` (chỉ ghi tên tool). Trace cố ý không ghi claim row, order row thô, ticket, SĐT, địa chỉ, tên hàng hay ghi chú nội bộ. Order chỉ ghi các trường trong allowlist.

## 4. Kết quả

Nguồn: `src/reports/benchmark.json` (14 claim × 5 seed `11,22,33,44,55` = 70 trial mỗi shape, MockLLM, `as_of` 2026-11-15, mỗi trial một SQLite mới). Cost là VND mô phỏng, không phải hóa đơn API. Latency là `unavailable`.

| Shape | Pass rate | Pass^5 | Seed min–max | Variance | Cost/success (VND) | Mean / p95 steps |
| --- | --- | --- | --- | --- | --- | --- |
| workflow | 1.000 | 1.000 | 1.000–1.000 | 0 | 34.29 | 4.43 / 5.0 |
| single | 1.000 | 1.000 | 1.000–1.000 | 0 | 33.41 | 5.50 / 6.0 |
| orchestrator | 1.000 | 1.000 | 1.000–1.000 | 0 | 57.15 | 4.71 / 5.0 |
| swarm (tham chiếu) | 0.986 | 0.929 | 0.929–1.000 | 0.000816 | 49.57 | 2.80 / 3.0 |

**Crash safety:** 20/20 (`src/reports/crash.json`). Sau resume còn đúng một dòng `refund_ledger` và một audit `refund_committed`. T11 và T12 xanh trên cả 4 shape. Bộ test student: 248 passed.

**Ablation (R4,** `src/reports/ablation_seeds.json`**):** đổi bộ seed sang `12,23,34,46,57` (không seed nào chia hết cho 5), giữ nguyên mọi thứ khác. Swarm lên pass 1.000, pass^5 1.000, variance 0. Ba shape của nhóm không đổi. Thứ hạng cost giữ nguyên. Vậy chênh lệch pass của swarm trên bộ public đến từ seed 55 (ticket ghi 5 ngày, order ghi 2 ngày ở C-002), không phải từ topology. Trên bộ public, chỉ cost phân biệt được các shape.

**Tự kiểm trên** `student_drop/`**:** chưa làm (thư mục chưa có trong repo).

Quyết định kiến trúc và lý do: xem `report/team/decision_adr.md`. Phiếu nghiên cứu và ablation: xem `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

- **Lọc test sai shape.** `python -m pytest -q -m student -o addopts= -k single` báo `120 failed`. Nguyên nhân: `-k single` khớp cả tên test `test_public_single_run_cases`, nên chạy luôn workflow và orchestrator khi hai shape này còn là stub. Xử lý: đếm fail theo hậu tố `-single]`, `-workflow]`, `-orchestrator]`; shape `single` có 0 fail. Lọc đúng shape bằng `-k "-single]"`.
- **Chọn seed ablation sai.** Lần đầu dùng seed `12,23,34,45,56`, kết quả swarm không đổi (0.986). Nguyên nhân: 45 chia hết cho 5, vẫn kích hoạt điểm yếu của swarm. Xử lý: đổi `45` thành `46` và `56` thành `57`, chạy lại: swarm 1.000. Test `test_seed_ablation_removes_swarm_seed_55_failure` kiểm kết quả này.
- `crash_test` **không nhận tham số shape.** Nó kiểm lớp host (ledger), nên 20/20 không chứng minh từng shape truyền `crash_at` đúng. Bằng chứng cho từng shape là T11 và T12 xanh.
- **Ghi report trên nhánh** `main`**.** Nhóm tách nhánh `cuong/ledger-eval-reports` trước khi commit report.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong `TEAM.md` (bảng đóng góp) và báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện

MockLLM không phải model sản xuất; latency là `unavailable`; cost là mô phỏng.

- Số liệu là trên bộ public 14 claim. Pass 1.000 không đảm bảo qua ngưỡng 0.75 trên 40 hidden claim × 5 seed. Nhóm chưa chạy hidden.
- Ba shape của nhóm ngang nhau về pass, nên chọn `single` dựa vào cost (33.41, thấp nhất) và công sức triển khai. Chênh lệch với workflow chỉ khoảng 2.6%.
- Kết luận đổi nếu trên hidden `single` dưới 0.75 hoặc pass^5 thấp rõ rệt mà orchestrator giữ được, hoặc nếu có loại claim cần tách quyền đọc/ghi giữa các agent.
- Ablation chỉ đổi một biến (seed). Chưa kiểm các biến nhiễu khác (prompt, tool).

## 8. Tài liệu tham khảo

- `docs/business_rules.md`, `docs/contracts.md`, `docs/architecture.md`, `docs/metrics.md` của repo đề bài.
- EMNLP 2026, *Rethinking Evaluation of MAS Efficiency* (nguồn của research card R4, theo thư viện tham khảo của lớp; nhóm chưa đọc toàn văn).
