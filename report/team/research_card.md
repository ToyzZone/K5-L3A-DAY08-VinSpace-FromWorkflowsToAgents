# Research card

File này nằm cố định ở `report/team/research_card.md`; `python -m lab8.check_submission` đọc cột "Nhóm điền" bằng máy.

Phần này nối tiếp phần mini research ở buổi lý thuyết (slide 62–63). Chọn **một** câu R1–R4, điền 6 dòng, rồi biến nó thành **một ablation** chạy được trong lab: giữ nguyên model (MockLLM), tool, seed, corpus và giá, chỉ thay đổi một biến.

| Câu | Nguồn (thư viện tham khảo, slide 68–69) | Câu hỏi gợi ý cho lab |
| --- | --- | --- |
| R1 · Scaling | Google Research 2026, *Towards a Science of Scaling Agent Systems* | Task claims chủ yếu tuần tự hay song song được? Dự đoán thêm investigator sẽ làm pass rate và cost/success thay đổi thế nào. |
| R2 · Failure taxonomy | MAST, NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?* | Các trial fail của swarm (seed 55) thuộc nhóm nào: lỗi giao việc, lệch mục tiêu, hay lỗi kiểm chứng? |
| R3 · Architecture choices | AgentArch, AACL 2026 | Nếu đổi topology mà giữ nguyên mọi thứ khác, biến nào phải cố định để kết luận còn đúng? |
| R4 · Evaluation confounders | EMNLP 2026, *Rethinking Evaluation of MAS Efficiency* | Làm sao chứng minh chênh lệch giữa A/B/C/D là do topology, không phải do prompt, tool hay seed? |

## Phiếu của nhóm

Điền vào cột cuối. Không xóa hai cột đầu.

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R4 · Evaluation confounders |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | EMNLP 2026, *Rethinking Evaluation of MAS Efficiency* (thư viện tham khảo của lớp, slide 44, 59). Không có URL trong repo đề bài nên nhóm không ghi URL. Loại bằng chứng: paper đánh giá, nhóm chưa đọc toàn văn |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Kết luận về hiệu năng của hệ multi-agent có thể đến từ cách đo, không chỉ từ topology (theo mô tả trong docs/bonus_topics.md, B7) |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Nhóm chỉ dựa vào mô tả của lớp, chưa kiểm model và dataset của paper. Ở đây áp dụng cho MockLLM, 14 claim public, bảng giá mô phỏng, nên không suy ra cho model sản xuất |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Khoảng chênh pass rate của swarm so với 3 shape còn lại (0.986 so với 1.000) là do seed, không do topology. Đổi bộ seed từ 11,22,33,44,55 sang 12,23,34,46,57 (không seed nào chia hết cho 5) thì swarm lên 1.000, pass^5 lên 1.000, variance về 0. Thứ hạng cost/success giữ nguyên |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Cố định: MockLLM, tools, corpus 14 claim, bảng giá, evaluator, `as_of` 2026-11-15, 4 shape. Biến duy nhất đổi: bộ seed |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Lỗi dự kiến: swarm sai ở C-002 khi seed chia hết cho 5 (resolved thay vì denied). Đo bằng pass rate, pass^5, seed variance, cost/success |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 12,23,34,46,57 --out reports/ablation_seeds.json` (chạy trong `src/`)
- Run id / file report: `src/reports/ablation_seeds.json`, so với `src/reports/benchmark.json`. Kiểm bằng `src/tests/test_reports_artifacts.py`
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu: **Đúng.** Swarm: pass 0.986, pass^5 0.929, variance 0.000816 (seed gốc) thành 1.000, 1.000, 0 (seed mới), cost/success 49.57 thành 48.72. Workflow, single, orchestrator không đổi (1.000 / 1.000 / 0; cost 34.29, 33.41, 57.15). Thứ hạng cost giữ nguyên: single < workflow < swarm < orchestrator. Kết luận: chênh lệch pass của swarm đến từ seed, không phải topology. Chỉ so cost mới phân biệt được các shape trên bộ public
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`.

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).
