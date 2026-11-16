# Quy định Lab 8

## Dùng AI

- Được dùng trợ lý AI (Copilot, Cursor, Claude…) để viết code và tài liệu. Nhóm chịu trách nhiệm kiểm tra code, kết quả và số liệu.
- Shape không được gọi model thật. MockLLM cố định theo seed để mọi nhóm so cùng điều kiện.
- Không bịa số liệu. Mọi số trong ADR và báo cáo phải lấy từ file do script tạo.

## Hợp tác và sao chép

- Làm trong nhóm. Mỗi người có phần việc riêng, ghi trong `docs/contributions.md` và `TEAM.md`.
- Được trao đổi ý tưởng với nhóm khác, không chép code của nhóm khác. Dùng code hay ý tưởng từ nguồn ngoài thì ghi nguồn.
- Không chép khối `REFERENCE_WEAKNESS` của swarm vào shape của nhóm.
- Không sửa thước đo: `lab8/metrics.py`, `lab8/grade_hidden.py`, `lab8/durability.py`, `lab8/policy.py`, `config/*.yaml`, `data/*`.

## Nộp muộn

- Deadline theo [`SUBMISSION.md`](SUBMISSION.md): lab sáng 23h59 cùng ngày, lab chiều / tối 11h59 ngày hôm sau (GMT+7).
- Coach có thể gia hạn tối đa 48 giờ. Nộp trễ hạn ngoài phần gia hạn thì xử lý theo thông báo của giảng viên.

## API key và bí mật

- Lab không cần API key. Không commit `.env`, token hay mật khẩu.
- Không đưa `parent_secret`, SĐT, địa chỉ, ghi chú nội bộ, tên hàng vào trace, log hay stdout.
- Không đẩy pack hidden (`eval/instructor/`) hay nhãn hidden lên repo.
