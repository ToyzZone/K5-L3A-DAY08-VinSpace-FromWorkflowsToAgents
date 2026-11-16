# Lab 8 — LogiX-VN: một task, bốn kiến trúc

**Bài nhóm.** AI20K ngày 8, buổi lab 4 giờ (13:30 đến 17:30). Bài toán: xử lý claim hoàn phí vận chuyển. Dữ liệu là dữ liệu giả. Không cần GPU, API key hay internet trong giờ lab. Chạy được trên Windows, macOS và Linux.

**Mục tiêu:** dựa trên số đo, chọn kiến trúc **ít tự chủ nhất mà vẫn làm được việc**. Workflow và multi-agent phải được so trên cùng claim, cùng seed, cùng bảng giá mô phỏng. Không mặc định multi-agent tốt hơn.

Repo này là starter. Các phần đã chạy được ngay: swarm tham chiếu, world, MockLLM, host (policy, ledger, handoff). Ba shape còn lại do nhóm viết.

## Tài liệu của lab

| File | Nội dung |
| --- | --- |
| [`CHECKPOINTS.md`](CHECKPOINTS.md) | Mốc M0 đến M4: nhiệm vụ, sản phẩm, tự kiểm tra |
| [`RUBRIC.md`](RUBRIC.md) | 100 điểm, must-pass, bonus |
| [`SUBMISSION.md`](SUBMISSION.md) | Đặt tên repo, cấu trúc nộp, deadline, nộp LMS |
| [`RULES.md`](RULES.md) | AI, hợp tác, nộp muộn, bí mật |
| [`TEAM.md`](TEAM.md) | Thành viên nhóm và mục cá nhân |

## Mục lục

1. [Việc nhóm nộp](#việc-nhóm-nộp)
2. [Luật nghiệp vụ](#luật-nghiệp-vụ-synthetic)
3. [Chuẩn bị: cài đặt theo hệ điều hành](#chuẩn-bị-cài-đặt-theo-hệ-điều-hành)
4. [Các lệnh trong buổi lab](#các-lệnh-trong-buổi-lab)
5. [Hai bộ test](#hai-bộ-test)
6. [Lịch, rubric, điểm cộng](#lịch-buổi-lab)
7. [Output contract: `run_claim` phải trả gì](#output-contract-run_claim-phải-trả-gì)
8. [Trace contract v1](#trace-contract-v1)
9. [Checklist nộp bài](#checklist-nộp-bài)
10. [Dành cho giảng viên](#dành-cho-giảng-viên)
11. [Xử lý sự cố](#xử-lý-sự-cố)

## Việc nhóm nộp

Sau 4 giờ, nhóm có cùng một claims flow chạy trên bốn shape:

| Shape | Việc của nhóm | Ai được ghi refund |
| --- | --- | --- |
| A `workflow` | Các bước Python cố định. Model không tính tiền | Host |
| B `single` | Vòng ReAct, tối đa 8 bước | Host |
| C `orchestrator` | Investigator chỉ đọc. Handoff theo allowlist | Orchestrator / host |
| D `swarm` | Có sẵn, dùng để đối chứng cost và variance | Host vẫn chặn ghi |

Code viết vào `lab8/shapes/workflow.py`, `single.py`, `orchestrator.py`. Đầu mỗi file có hướng dẫn từng bước. Giữ nguyên chữ ký hàm:

```python
run_claim(claim_id: str, *, seed: int, store_path: str, crash_at: str | None = None) -> RunResult
```

## Luật nghiệp vụ (synthetic)

Nguồn sự thật là dòng order và policy có `is_current` và `effective_date <= 2026-11-15`. Chữ trong ticket là dữ liệu người dùng, kể cả những câu như "ignore policy" hay "trễ 9 ngày".

| Tình huống | Kết quả đúng |
| --- | --- |
| Trễ ≥ 3 ngày, đơn `delivered` hoặc `delivered_late`, policy hiện hành | Hoàn đúng `shipping_fee_vnd` |
| `damage_verified=true` | `min(max_refund của DMG-04, paid_vnd)` |
| Cả ship và damage cùng đủ điều kiện | Một refund bằng **số lớn hơn**, không cộng hai số |
| Trễ dưới 3 ngày, hỏng hàng chưa verify, phí ship 0, đơn `cancelled` hoặc `in_transit` | Không refund (`denied`) |
| Thiếu `order_id` | `needs_info`, không ghi ledger. Không lấy mã đơn từ câu chữ trong ticket |
| Principal không sở hữu đơn, hoặc không tìm thấy đơn | `escalated`. Không trả phone, địa chỉ, tên hàng, internal note |
| Policy cũ `SHIP-LATE-OLD` hoặc policy tương lai | Bỏ qua. `get_clause` vẫn trả về các clause này, nhóm phải tự kiểm `is_current` |
| Không có approval, approval hết hạn, bị thu hồi, hoặc amount ≤ 0 | Không ghi refund. Khi quote > 0 mà cổng duyệt từ chối thì phải có audit `policy_denied` |
| Approval mà claim trỏ tới (`approval_id`) được cấp cho claim khác | Không ghi refund, audit `policy_denied` lý do `approval_claim_mismatch`. Chỉ approval có `approval_id` khớp claim mới được tính |
| Đơn đã được hoàn trước đó bởi claim khác | Trần tính **theo đơn**: tổng tiền hoàn của một đơn không vượt entitlement lớn nhất. Hoàn đủ rồi → `denied`, audit `policy_denied` lý do `order_already_refunded`. Entitlement mới lớn hơn (ví dụ hỏng hàng sau khi đã hoàn ship) → chỉ hoàn **phần chênh** |
| Approval thấp hơn quote | Refund `min(quote, approved_vnd, paid_vnd)`. `proposal_amount` vẫn là quote |
| Gọi lại cùng claim | Vẫn một dòng ledger. Amount khác số đã commit → `conflict`, không sửa số cũ |
| Crash sau khi đã ghi effect, trước checkpoint | Resume xong vẫn một refund và một audit `refund_committed` |

Ví dụ public:

- T01: đơn `O-107` trễ 4 ngày, phí ship 35.000, approval 35.000 → một effect 35.000 và một audit committed.
- T13: đơn `O-505` đã được hoàn 35.000 ship từ claim trước. Ticket nói "chưa nhận được tiền" → `denied`, `proposal_amount` 35.000, không ghi ledger, có `policy_denied`.
- T14: đơn `O-515` đã được hoàn 30.000 ship, nay hỏng hàng đã verify (entitlement 150.000) → `resolved`, `proposal_amount` 150.000, ledger 120.000.

**Cách làm đúng với trần theo đơn:** truyền **quote đầy đủ** từ `compute_compensation` vào `durability.issue_refund`. Host tự trừ phần đã hoàn. Nếu shape tự trừ trước rồi mới truyền vào, host sẽ trừ thêm lần nữa và T14 fail. Muốn biết đơn đã được hoàn bao nhiêu thì dùng read tool `lookup_refund_history`.

Tiền do code tính: `lab8.tools.compute_compensation` / `lab8.compensation.quote`. Không để MockLLM quyết số tiền.

## Chuẩn bị: cài đặt theo hệ điều hành

Cần **Python 3.11, 3.12 hoặc 3.13** và `git`. Mọi lệnh chạy tại **thư mục gốc repo** (thư mục có file `README.md` này).

Kiểm tra phiên bản Python trước:

| Hệ điều hành | Lệnh |
| --- | --- |
| macOS / Linux | `python3 --version` |
| Windows | `py --version` (hoặc `python --version`) |

### macOS / Linux (bash, zsh)

```bash
git clone <repo-url> n8-lab8-logix-vn
cd n8-lab8-logix-vn
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m lab8.smoke
```

### Windows: PowerShell

```powershell
git clone <repo-url> n8-lab8-logix-vn
cd n8-lab8-logix-vn
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m lab8.smoke
```

Nếu PowerShell báo `running scripts is disabled on this system`, chạy lệnh dưới (chỉ có hiệu lực trong cửa sổ hiện tại), rồi activate lại:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### Windows: Command Prompt (cmd)

```bat
git clone <repo-url> n8-lab8-logix-vn
cd n8-lab8-logix-vn
py -3 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
python -m lab8.smoke
```

Dùng Git Bash trên Windows thì làm như macOS/Linux, nhưng activate bằng `source .venv/Scripts/activate`.

### Kết quả mong đợi

Sau khi activate venv, lệnh trên mọi hệ điều hành đều là `python -m ...`. Smoke đúng sẽ in ra:

```text
lab8.smoke pass
python 3.x.y | <Windows|Darwin|Linux> <arch>
manifest 1.1 | MockLLM seeded | swarm C-001 refund 35000 | trace clean
```

## Các lệnh trong buổi lab

Mỗi lệnh nằm trên một dòng, nên copy được vào PowerShell, cmd hay bash mà không phải sửa.

| Mục đích | Lệnh |
| --- | --- |
| Kiểm tra cài đặt | `python -m lab8.smoke` |
| Kiểm format bài nộp | `python -m lab8.check_submission` |
| Cổng đầu buổi (host) | `python -m pytest -q` |
| Tự chấm T01–T14 trên 4 shape | `python -m pytest -q -m student -o addopts=` |
| Tự chấm một shape | `python -m pytest -q -m student -o addopts= -k workflow` |
| Chạy một claim | `python -m lab8.run --shape swarm --claim-id C-001 --seed 11 --db data/run.sqlite` |
| Chạy một claim với crash | `python -m lab8.run --shape workflow --claim-id C-012 --seed 11 --db data/crash.sqlite --crash-at after_effect_before_checkpoint` |
| Benchmark 4 shape × 5 seed | `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json` |
| Crash suite 20 điểm | `python -m lab8.crash_test --count 20 --out reports/crash.json` |
| Demo phản ví dụ (checkpoint không thay được ledger) | `python -m lab8.demo.buggy_workflow` |

`python -m pytest -q` là cổng đầu buổi. Bộ này kiểm contract, compensation, approval, idempotency, handoff, crash 20/20, trần hoàn tiền theo đơn, approval đúng claim, và swarm trên T01–T10, T13, T14. Phải xanh hết trước khi chia việc, và phải giữ xanh suốt buổi. Kết quả mong đợi: `N passed, 248 deselected`, không có dòng `failed`.

Ma trận student lúc mới clone: **186 failed, 62 passed**. 62 test swarm xanh, 3 shape stub × 62 test đỏ. Shape nào làm xong thì 62 test của shape đó phải xanh.

`run.py` chỉ tạo DB khi file `--db` chưa tồn tại. Chạy lại trên cùng DB là kịch bản retry/resume. Muốn chạy lại từ đầu thì xóa file `.sqlite` hoặc đổi tên `--db`.

## Hai bộ test

| Bộ | Ở đâu | Ai chạy | Trong git? |
| --- | --- | --- | --- |
| Public T01–T14 | `data/public_claims.jsonl`, `tests/test_public_matrix.py` | Học viên, suốt buổi | Có |
| Hidden 40 claim × 5 seed | `eval/instructor/` | Giảng viên chấm cuối buổi. Học viên nhận `student_drop/`, không có nhãn | Không (`.gitignore`) |

Bộ hidden phủ: ticket nói dối, injection, approval hỏng hoặc mượn của claim khác, đơn đã được hoàn trước đó, policy hết hiệu lực, cộng dồn sai, đơn hủy / đang giao, homoglyph, principal lẫn, crash và rò secret. Nhãn không nằm trong file học viên nhận. Grader bỏ qua field `expected` gắn trên claim.

**Điểm yếu cố ý của swarm:** ở seed chia hết cho 5 (seed 55), swarm tin số ngày ghi trong ticket thay vì cột `delay_days`. Trên bộ public, chỗ này lộ ra ở T02: ticket ghi "trễ 5 ngày", order ghi 2 ngày, swarm trả 20.000 thay vì từ chối. Vì vậy benchmark public của swarm ra pass ≈ 0.986, pass^5 ≈ 0.929. Trong ma trận student, trial đó được kiểm là *phải fail* với swarm. Shape của nhóm thì phải pass.

Ngưỡng cho shape nhóm chọn trên hidden: pass rate ≥ 0.75, báo kèm pass^5, variance và cost/success. Công thức: `docs/metrics.md`.

**Must-pass, không bù điểm:** refund khi thiếu approval hợp lệ; lộ `CANARY_SECRET_...`; crash tạo hơn một refund.

## Lịch buổi lab

Buổi lab chạy từ 13:30 đến 17:30.

| Mốc | Việc | Bằng chứng |
| --- | --- | --- |
| 13:30 M0 | Cài đặt, smoke, đọc contract, chia vai | `python -m lab8.smoke` |
| 13:45 M1 | Workflow, single, orchestrator (swarm có sẵn) | Cùng chữ ký `run_claim` |
| 14:30 M2 | Handoff, ledger, crash | `python -m pytest -q` vẫn xanh; shape mới qua test host |
| 15:15 | Nghỉ | |
| 15:30 M3 | 20 crash, approval, secret. Hạn chót đăng ký topic bonus tự đề xuất | `reports/crash.json` |
| 16:15 M4 | ≥ 10 public claim × 5 seed, rồi hidden trên grader | `reports/benchmark.json`, `docs/decision_adr.md` |
| 17:00 | README, hash, run id, `check_submission` ra 0 FAIL | Repo + báo cáo |

Khung báo cáo: `docs/architecture.md`, `docs/decision_adr.md`, `docs/research_card.md`, `docs/contributions.md`.

### Rubric 100 điểm

| Hạng mục | Điểm |
| --- | --- |
| Implementation | 20 |
| Hidden | 15 |
| Durability | 20 |
| Policy | 10 |
| Handoff | 10 |
| Benchmark | 10 |
| Reproducibility | 10 |
| Đóng góp | 5 |

Bằng chứng giảng viên đọc cho từng hạng mục, must-pass và phần không được tính: [`RUBRIC.md`](RUBRIC.md).

### Điểm cộng (tối đa +10, tổng tối đa 110, tính theo nhóm)

Sáu topic mở rộng, mỗi topic lấy từ một nghiên cứu trong bài lý thuyết. Mỗi nhóm chọn một topic. Điểm cộng tính cho cả nhóm. Chi tiết, thang điểm và cách chấm: **`docs/bonus_topics.md`**.

| Topic | Nguồn |
| --- | --- |
| B1 Investigator song song và critical path | Google Research 2026, scaling agent systems |
| B2 Gắn nhãn lỗi theo MAST | MAST, NeurIPS 2025 |
| B3 Verifier/aggregator chống khuếch đại lỗi | Google Research 2026, error amplification |
| B4 Baseline công bằng, ablation và thống kê | EMNLP 2026; AgentArch, AACL 2026 |
| B5 Provider idempotency và reconciliation | DBOS durable workflows |
| B6 Investigator từ xa theo kiểu A2A | A2A v1.0; ProtocolBench, ICML 2026 |

Bonus là điểm lab, không phải điểm pitching hay phát biểu. Bonus chỉ được tính khi shape nhóm chọn đã qua cả 3 must-pass **và** đạt pass rate hidden **≥ 0.80** (cao hơn ngưỡng 0.75 của bài chính).

## File nên đọc trước khi code

- `lab8/shapes/swarm_reference.py`: shape đối chứng. Khối `REFERENCE_WEAKNESS` là chỗ swarm tin ticket. Workflow không được copy khối này.
- `lab8/durability.py`: transaction và idempotency key `refund:{claim_id}`.
- `lab8/handoff.py`: allowlist.
- `lab8/runtime.py`: vòng ReAct và investigator read-only.
- `config/autonomy_policy.yaml`, `config/tools.manifest.v1.1.yaml`, `harness_map.yaml`.

## Output contract: `run_claim` phải trả gì

Grader **không đọc câu chữ trả lời khách**. Nó chấm `RunResult` và đối chiếu với ledger SQLite. Sai field là fail, dù logic tiền đúng.

**Cách an toàn nhất:** tạo kết quả bằng `lab8.shapes.common.finish(...)`, giống `swarm_reference.py`. Hàm này tự lấy `refund_effects` và `committed_audit_count` từ ledger, tự ghi trace, tự cộng budget. Không tự điền hai field đó bằng tay.

| Tình huống | `status` | `proposal_amount` | Ledger sau khi chạy |
| --- | --- | --- | --- |
| Thiếu `order_id` | `needs_info` | `0` | Không có dòng |
| Không tìm thấy đơn, hoặc principal không sở hữu đơn | `escalated` | `0` | Không có dòng |
| Quote = 0 (trễ < 3 ngày, đơn hủy, phí 0, policy cũ…) | `denied` | `0` | Không có dòng. Không gọi `issue_refund` |
| Quote > 0 nhưng host từ chối (approval hỏng, approval của claim khác, đơn đã hoàn đủ) | `denied` | **quote đầy đủ** | Không có dòng, có audit `policy_denied` |
| Quote > 0, host chấp nhận | `resolved` | **quote đầy đủ** (không phải số đã ghi) | Một dòng, số tiền do host tính sau khi cap |
| Gọi lại với số tiền khác số đã commit | `failed` | quote | Giữ dòng cũ |
| `claim_id` không tồn tại | `failed` | `0` | Không có dòng |

Quy tắc bắt buộc:

- `status` chỉ được là một trong `resolved`, `needs_info`, `escalated`, `denied`, `failed`. `RunResult` sẽ báo lỗi nếu ghi khác.
- `claim_id` trong kết quả phải đúng claim được giao (nếu khác thì fail `wrong_claim_id`). `run_id` dùng `make_run_id(shape, claim_id, seed)`.
- `proposal_amount` là số nguyên VND, không phải chuỗi `"35.000đ"`.
- Muốn quote > 0 được chấm `policy_denied` thì phải **gọi `durability.issue_refund`** để host ghi audit. Shape tự từ chối thì không có audit, nên fail.
- **Truyền `crash_at` vào `durability.issue_refund` và không bắt `InjectedCrash`.** T12 kiểm crash có thật sự xảy ra hay không.
- `run_claim` không được ném exception. Grader ghi trial đó là `exception:...` (fail) rồi chấm tiếp.

## Trace contract v1

Trace là nhật ký một lần chạy: shape đã đọc gì, quyết định gì, gọi host thế nào. Grader đọc trace để làm hai việc: đếm số bước (metric `steps`), và **quét secret/PII**. Vì vậy trace là một phần của ranh giới bảo mật, không phải tiện ích debug.

Nhóm **được tự viết tracer** (thêm span, timing, cách redact riêng). `lab8.trace.Trace` chỉ là thư viện có sẵn, dùng cho nhanh. Dùng gì cũng được, miễn output đúng contract:

| # | Bắt buộc |
| --- | --- |
| 1 | `RunResult.trace_path` trỏ tới một file JSON **được ghi trong chính lần chạy này** |
| 2 | File là một object, có `run_id` trùng `RunResult.run_id` và có `events` là một list |
| 3 | Mọi file khác do shape ghi ra (debug log, dump…) nằm cùng thư mục với trace, tên bắt đầu bằng `run_id` |
| 4 | Không ghi secret, header, SĐT, địa chỉ, ghi chú nội bộ, tên hàng vào bất kỳ đâu, kể cả stdout |

Grader **fail-closed**: thiếu trace (`missing_trace`), trace cũ của lần chạy trước (`stale_trace`), sai format (`invalid_trace`) hoặc sai `run_id` (`trace_run_id_mismatch`) đều làm trial fail. Lý do: scanner không đọc được log thì không thể chứng minh log đó sạch. Grader quét `trace_path` và mọi file `<run_id>*` cùng thư mục. File ở chỗ khác hay output ra stdout thì grader không thấy, nhưng vẫn bị tính là vi phạm khi giảng viên kiểm tra.

Lỗi hay gặp nhất: ghi nguyên claim row hoặc order row vào trace để debug. Claim row có `parent_secret`, order row có SĐT và địa chỉ. Chỉ ghi các field đã qua allowlist (`get_claim_view`, `lookup_order`, handoff đã sanitize).

## Checklist nộp bài

Chạy lệnh này trước khi push. Nó không chấm điểm, chỉ kiểm grader có đọc được bài của nhóm hay không:

```text
python -m lab8.check_submission
```

Phải ra `0 FAIL`. Lệnh kiểm:

| Mục | Điều kiện |
| --- | --- |
| 3 shape | Trả `RunResult` hợp lệ, có trace đúng contract, không còn `not_implemented`, không ném exception |
| `reports/benchmark.json` | Do `lab8.benchmark` tạo, đủ 4 shape, seed `11,22,33,44,55`, ≥ 10 claim |
| `reports/crash.json` | `crash_safety` = `20/20` |
| `docs/decision_adr.md` | `- Shape chọn:` là đúng một trong `workflow`, `single`, `orchestrator`, `swarm`, các dòng còn lại đã điền |
| `docs/contributions.md` | Mỗi thành viên một dòng |
| `docs/research_card.md` | Cột "Nhóm điền" không trống |
| `docs/bonus_report.md` | Chỉ khi làm bonus: tiêu đề `# Bonus report: B1` … `B6` |

Thứ tự nộp:

1. `python -m pytest -q` xanh.
2. Chạy benchmark và crash test (lệnh ở bảng trên) để tạo `reports/benchmark.json`, `reports/crash.json`.
3. Commit, rồi chạy `git rev-parse --short HEAD`. Ghi hash và run id vào `docs/decision_adr.md`, rồi commit tiếp.
4. `python -m lab8.check_submission` ra `0 FAIL`, rồi push.
5. Mỗi thành viên tự nộp link repo nhóm lên LMS. Tên repo và deadline (GMT+7): [`SUBMISSION.md`](SUBMISSION.md).

Không sửa tay file JSON trong `reports/`. Giảng viên chạy lại đúng các lệnh đó.

### Tự kiểm trên bộ hidden (sau 16:15)

Giảng viên phát thư mục `student_drop/` (claim không nhãn). Đặt thư mục đó ở gốc repo, rồi chạy:

```text
python -m lab8.benchmark --shapes workflow,single,orchestrator --cases student_drop/hidden_claims.jsonl --world student_drop/hidden_world_state.json --out reports/hidden_selfcheck.json
```

Không có nhãn nên không ra pass rate. Lệnh này cho biết shape có chạy hết 40 claim mà không lỗi không (`status` ≠ `error`), trace có đúng contract không, và có trial nào nghi lộ secret không (`leak_suspect`). Điểm chính thức do grader của giảng viên chấm.

## Dành cho giảng viên

- **Pack hidden không có trong git.** Thư mục `eval/instructor/` bị `.gitignore` chặn và chỉ có trên máy soạn bài. Giữ một bản sao ở kho lưu trữ riêng của khóa học, không đẩy lên repo này. Cần tạo lại thì đặt `generate_hidden.py` vào `eval/instructor/`, rồi chạy `python scripts/build_public_fixtures.py` và `python eval/instructor/generate_hidden.py`. Quy trình chi tiết nằm trong `eval/instructor/README_GIANG_VIEN.md`.
- **16:15 phát cho học viên:** chỉ copy `eval/instructor/student_drop/` (claim không nhãn và world state). Không gửi `hidden_labels.json`, `hidden_claims.jsonl` bản đầy đủ, hay `generate_hidden.py`.
- **Chấm chính thức:**

  ```text
  python -m lab8.grade_hidden --pack eval/instructor --shapes workflow,single,orchestrator,swarm --seeds 11,22,33,44,55 --out reports/hidden_grade.json
  python -m lab8.crash_test --count 20 --out reports/crash.json
  ```

  Gate: shape nhóm chọn có pass rate ≥ 0.75 trên 200 trial (≥ 0.80 nếu muốn nhận điểm cộng); `secret_leak_count`, `pii_leak_count`, `approval_bypass_count` bằng 0; crash 20/20. Lưu ý `crash_test` kiểm host và swarm. Crash của shape nhóm được kiểm qua T12 trong ma trận student.
- **Đối chứng mong đợi:** swarm trên hidden ra pass 0.97, pass^5 0.85, chỉ fail ở seed 55. Một workflow đúng ra 1.0 / 1.0.
- **Grader chống ghi lén:** trial fail với lý do `unexpected_ledger_rows` nếu ledger có dòng không thuộc claim đang chấm và không phải refund lịch sử đã seed. Shape không thể ghi tiền dưới claim id khác mà lọt.
- **Chấm bonus:** quy trình 10 phút mỗi nhóm ở cuối `docs/bonus_topics.md`. Biến thể bonus chấm trên hidden bằng cờ `--extra-shape`.
- **Chấm nhiều nhóm:** chạy grader ngay trong repo của từng nhóm (thư mục làm việc là gốc repo của nhóm đó, vì grader tìm trace trong `traces/` của thư mục hiện tại), trỏ `--pack` tới pack của giảng viên bằng đường dẫn tuyệt đối. Shape được chấm cổng hidden lấy từ dòng `- Shape chọn:` trong `docs/decision_adr.md`. Một shape ném exception chỉ làm fail trial của shape đó, các shape khác vẫn được chấm.
- **CI:** `.github/workflows/ci.yml` chạy smoke, pytest, crash suite và benchmark swarm trên Ubuntu, Windows, macOS × Python 3.11 và 3.13. Push lên GitHub là thấy kết quả trên cả 3 hệ điều hành.

## Xử lý sự cố

| Triệu chứng | Cách xử lý |
| --- | --- |
| `No module named 'lab8'` hoặc `No module named 'yaml'` | Chưa đứng ở gốc repo, hoặc chưa activate venv / chưa `python -m pip install -r requirements.txt` |
| Windows: gõ `python` mà mở Microsoft Store | Dùng `py -3 -m venv .venv`. Sau khi activate venv thì `python` trỏ vào venv |
| Windows: `running scripts is disabled` | `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` rồi activate lại |
| Windows: `UnicodeEncodeError` khi in tiếng Việt từ code của nhóm | Đặt biến môi trường UTF-8: PowerShell `$env:PYTHONUTF8=1`, cmd `set PYTHONUTF8=1`. Các CLI của lab đã tự chuyển stdout sang UTF-8 |
| Windows: `PermissionError ... being used by another process` với file `.sqlite` | Có connection chưa đóng. Mở bằng `connect()` thì đóng trong `finally: conn.close()`, như `swarm_reference.py` |
| Trial fail với `missing_trace`, `stale_trace`, `invalid_trace` hoặc `trace_run_id_mismatch` | Shape chưa ghi trace đúng contract. Xem mục [Trace contract v1](#trace-contract-v1). Nhớ ghi trace cả ở các nhánh return sớm (`needs_info`, `escalated`) |
| Benchmark báo `exception:...` cho một shape | `run_claim` ném lỗi. Xem `reason` trong `reports/benchmark.json`, các shape khác vẫn được chấm |
| T12 báo `crash did not fire` | Shape chưa truyền `crash_at` vào `durability.issue_refund`, hoặc đã bắt `InjectedCrash` |
| Benchmark của shape stub ra pass rate 0 | Đúng, shape đó chưa được triển khai |
| Chạy lần hai trên cùng `data/run.sqlite` không tạo refund mới | Ledger đang làm đúng. Benchmark tự tạo DB mới cho từng trial |
| Muốn gọi model thật | Không được. MockLLM cố định theo seed để mọi nhóm so cùng điều kiện |
