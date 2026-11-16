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

Trace của nhóm ghi những event nào? Field nào cố ý **không** ghi, và vì sao? Nếu trace nằm ngoài chỗ scanner quét được, đội security chứng minh thế nào là hệ thống không lộ secret?

## Giới hạn

Số liệu trên bộ public 14 claim, chưa chạy hidden. Pass 1.000 trên public không đảm bảo qua ngưỡng 0.75 trên hidden. MockLLM không phải model sản xuất. Latency để `unavailable`. Không sửa JSON cho đủ 0.75.
