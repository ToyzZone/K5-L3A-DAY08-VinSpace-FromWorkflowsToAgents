# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: single
- Commit hash: 751d094
- Run id dẫn chứng: R-single-C-001-s11 (và 69 trial còn lại của single trong src/reports/benchmark.json)
- Pass rate / pass^5 / seed min-max / variance: 1.000 / 1.000 / 1.0-1.0 / 0
- Cost per success (mô phỏng, VND): 33.41
- Crash safety: 20/20 (src/reports/crash.json)
- Secret leak / approval bypass: 0 / 0 (70/70 trial single qua tiêu chí chấm, gồm quét chuỗi cấm và khớp ledger; test_handoff_secret, test_authorization, test_order_cap_and_approval_binding xanh)

Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

Trên cùng 14 claim public, cùng 5 seed (11,22,33,44,55), cùng MockLLM và bảng giá, ba shape của nhóm đều đạt pass rate và pass^5 bằng 1.000, variance 0. Khác biệt nằm ở cost per success (mô phỏng): single 33.41, workflow 34.29, swarm 49.57, orchestrator 57.15 VND. Single rẻ nhất, và nhóm cũng thấy single ít công sức triển khai và bảo trì nhất (một vòng quyết định, không cần handoff). Chênh lệch với workflow chỉ khoảng 2.6%, nên lý do chọn single nghiêng về độ đơn giản hơn là hiệu năng. Single mất lợi thế nếu hidden có nhiều claim cần rẽ nhánh mà vòng ReAct đơn không giữ ổn định qua seed.

## Có đáng đổi lấy multi-agent không

Không. Orchestrator có pass bằng single (1.000) nhưng cost cao hơn khoảng 71% (57.15 so với 33.41). Swarm kém hơn cả pass (0.986), pass^5 (0.929) lẫn variance (0.000816) và đắt hơn 48%. Quyết định đảo lại nếu trên hidden single có pass rate dưới 0.75 hoặc pass^5 thấp rõ rệt mà orchestrator giữ được, hoặc nếu hidden có thêm loại claim cần tách quyền đọc/ghi giữa các agent.

## Trace và bằng chứng

Nhóm dùng `lab8.trace.Trace` có sẵn, nên mọi nhánh return (kể cả `needs_info`, `escalated`, `failed`) đều ghi file JSON có `run_id` khớp và `events` là list.

**Shape `single` ghi các event:** `react_step` (chỉ tên tool), `order` (chỉ các trường trong allowlist `ORDER_FIELDS`), `quote` (kết quả `compute_compensation`), `crash` (điểm crash khi có `InjectedCrash`) và `decision` (`status`, `proposal_amount`, `reason`). `workflow` ghi `claim_lookup` (chỉ cờ `found`), `order_lookup` (chỉ cờ `visible`), `quote` (chỉ `proposal_amount`), `refund_requested` và `decision`. `orchestrator` ghi `claim_view`, `handoff` (đã sanitize bằng allowlist, không ghi parent context), `investigator`, `quote`, `refund_outcome`, `crash` và `decision`.

**Cố ý không ghi:** claim row nguyên, `parent_secret`, header thô, nội dung ticket, SĐT, địa chỉ, tên hàng, ghi chú nội bộ. Lý do: grader quét trace và mọi file `<run_id>*` cùng thư mục để tìm secret và PII, nên trace là ranh giới bảo mật chứ không phải log debug. Ticket là dữ liệu người dùng, có thể chứa chuỗi bất kỳ. Vì vậy `react_step` chỉ ghi tên tool, không ghi kết quả tool. Shape đọc hồ sơ qua `get_claim_view` thay vì `SELECT *` để dữ liệu nhạy cảm không vào luồng xử lý.

**Bằng chứng không lộ secret:** trace nằm trong `traces/`, đúng chỗ scanner quét, và không có file debug nào khác ngoài trace. Số đo: 70/70 trial `single` trên bộ public qua tiêu chí chấm (gồm quét chuỗi cấm trong trace, mọi file `<run_id>*` và kết quả). Tự kiểm hidden: 0 `leak_suspect` và 0 trace sai contract trên 600 trial (`src/reports/hidden_selfcheck.json`). Test: `test_handoff_secret.py`, `test_trace_contract.py`, `test_orchestrator_shape.py`. `CANARY_SECRET_*` chỉ xuất hiện trong `data/public_claims.jsonl` (đầu vào), không xuất hiện trong `reports/` hay `traces/`.

## Giới hạn

Pass rate chỉ đo được trên bộ public 14 claim. Nhóm đã chạy tự kiểm trên `student_drop/` (40 claim không nhãn × 5 seed × 3 shape, `src/reports/hidden_selfcheck.json`): 0 trial lỗi, 0 `leak_suspect`, 0 trace sai contract, ba shape cho cùng quyết định ở 200/200 trial; cost mô phỏng single 6929.1, workflow 7050.0, orchestrator 11943.3 VND (cùng thứ hạng như bộ public). Bộ này không có nhãn nên không có pass rate; điểm hidden chính thức do grader của giảng viên chấm. Pass 1.000 trên public không đảm bảo qua ngưỡng 0.75 trên hidden. MockLLM không phải model sản xuất. Latency để `unavailable`. Không sửa JSON cho đủ 0.75.
