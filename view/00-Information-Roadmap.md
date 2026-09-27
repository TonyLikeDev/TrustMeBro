---
title: RoadmapFlow Comprehensive Information Roadmap & System Map
type: information-roadmap
tags:
  - information-architecture
  - sequence-diagram
  - system-mapping
  - data-flow
  - multi-session
  - hackathon
created: 2026-09-27
parent: "[[README]]"
---

# 🧭 00. Cấu Trúc Lộ Trình Thông Tin & Bản Đồ Hệ Thống Toàn Diện

> [!important] Tuyên Ngôn Kiến Trúc Thông Tin (Information Architecture)
> Một hệ thống AI-assisted đa phiên không thể hoạt động tin cậy nếu thiếu **Lộ trình thông tin (Information Roadmap)**. Lộ trình này xác lập ranh giới quyền hạn dữ liệu (data boundaries), cơ chế chuyển giao giữa các phiên làm việc (multi-session handoff) và cách thức chuyển đổi từ yêu cầu sơ khởi thành các bằng chứng nghiệm thu (artifacts) có thể đo lường định lượng.

---

## 🔁 1. Sequence Diagram: Luồng Vận Hành Toàn Diện (End-to-End Execution)

Biểu đồ trình tự mô tả tương tác khép kín giữa **Developer**, **AI Agent (Bob/Claude)**, **Hook & Rules Engine**, **Deterministic Core CLI**, **Hệ thống tệp (3-Tier State)** và **Bộ công cụ kiểm định (Verification Suite)**.

```mermaid
sequenceDiagram
    autonumber
    actor Dev as 👤 Developer
    participant Agent as 🤖 AI Agent (Bob / Claude)
    participant Hook as 🪝 Hook & Rules (.bob/rules)
    participant CLI as ⚙️ Deterministic Engine (Python stdlib)
    participant State as 📁 3-Tier State (Files on Disk)
    participant Test as 🧪 Verification Suite

    %% GIAI ĐOẠN 1: BẢN ĐỒ & HẠ TẦNG
    rect rgb(240, 248, 255)
    note over Dev,State: GIAI ĐOẠN 1: LẬP BẢN ĐỒ & KHỞI TẠO HẠ TẦNG 3-TIER
    Dev->>Agent: Yêu cầu phân tích codebase (/layout-init)
    Agent->>CLI: Quét cấu trúc src/ & components
    CLI-->>State: Ghi LAYOUT.md (Bản đồ codebase, ≤600 tok)
    Dev->>Agent: Yêu cầu dựng khung 3-Tier (/roadmap-scaffold)
    Agent->>CLI: python3 src/scaffold.py init .
    CLI-->>State: Dựng .bob/context/, src/db, src/logic, src/ui, .gitignore
    end

    %% GIAI ĐOẠN 2: LẬP KẾ HOẠCH
    rect rgb(255, 250, 240)
    note over Dev,State: GIAI ĐOẠN 2: TIÊU HÓA TÀI LIỆU & LẬP MASTER PLAN
    Dev->>Agent: Cung cấp yêu cầu & planning/ docs (/roadmap-planner)
    Agent->>State: Đọc planning/PROBLEM_STATEMENT.md & BOB_USAGE_PLAN.md
    Agent->>Agent: Giải quyết xung đột tài liệu vào Decisions Log
    Agent-->>State: Ghi PLAN.md (Master Plan đóng băng)
    Agent-->>State: Ghi ROADMAP.md (Status Board khởi tạo)
    Agent->>CLI: python3 src/roadmap.py progress ROADMAP.md
    CLI-->>State: Cập nhật ASCII Progress Bar ban đầu
    end

    %% GIAI ĐOẠN 3: PHIÊN LÀM VIỆC & ĐIỀU HƯỚNG
    rect rgb(245, 255, 245)
    note over Dev,State: GIAI ĐOẠN 3: PHIÊN LÀM VIỆC NGỮ CẢNH HẸP (SESSION START)
    Dev->>Agent: Bắt đầu phiên làm việc mới (Session Start)
    Hook->>CLI: Kích hoạt SessionStart Hook
    CLI->>State: Đọc ROADMAP.md tìm Active Phase
    CLI-->>State: Trích xuất .bob/context/current-phase.md (192 tokens)
    Hook->>Agent: Nạp Tier 1 (architecture.md) + Tier 2 (current-phase.md)
    Note over Agent: Tổng context nạp vào < 850 tokens (Tiết kiệm >91%)
    end

    %% GIAI ĐOẠN 4: THỰC THI & KIỂM THỬ
    rect rgb(255, 245, 255)
    note over Dev,Test: GIAI ĐOẠN 4: THỰC THI CÓ KỶ LUẬT (DEV-WORKFLOW)
    Agent->>Agent: Áp dụng quy tắc "Plan-Before-Act" (rules-agent/)
    Agent->>State: Viết code vào src/db/, src/logic/
    Agent->>Test: python3 src/test_tools.py -v
    Test-->>Agent: 7/7 Unit Tests PASSED (0.02s)
    Agent->>Test: python3 src/tests/test_plugin.py
    Test-->>Agent: Lifecycle Tests PASSED (ok)
    end

    %% GIAI ĐOẠN 5: ĐỒNG BỘ & ĐÓNG GIAI ĐOẠN
    rect rgb(240, 255, 255)
    note over Dev,State: GIAI ĐOẠN 5: ĐỒNG BỘ TRẠNG THÁI & ĐÓNG PHASE
    Agent->>State: Tích [x] kèm đường dẫn bằng chứng trong ROADMAP.md
    Agent->>CLI: python3 src/roadmap.py progress ROADMAP.md
    CLI-->>State: Tính lại tỷ lệ % tiến độ & cập nhật Change Log
    Agent->>CLI: python3 src/roadmap.py validate ROADMAP.md
    CLI-->>Agent: Binary Exit Criteria: ALL PASSED
    Note over State: Phase đóng thành công -> Navigator sẵn sàng cho Phase tiếp theo
    end

    %% GIAI ĐOẠN 6: AUDIT & BENCHMARK
    rect rgb(255, 255, 240)
    note over Dev,State: GIAI ĐOẠN 6: AUDIT CHUẨN MỰC & ĐO LƯỜNG THỰC NGHIỆM
    Dev->>CLI: python3 src/scaffold.py audit .
    CLI-->>Dev: 100% COMPLIANT (0 failures)
    Dev->>CLI: python3 src/benchmark.py --json-out things/benchmark_results.json
    CLI-->>State: Xuất docs/BENCHMARK_REPORT.md (Tiết kiệm 91.13% token/session)
    end
```

---

## 🔀 2. Sequence Diagram: Chuyển Giao Phiên Không Tràn Token (Multi-Session Handoff)

Biểu đồ này chứng minh cơ chế **cắt đứt sự tích tụ token** giữa các phiên làm việc — giải quyết triệt để vấn đề "Quality Cliff" (>100k tokens) của AI.

```mermaid
sequenceDiagram
    autonumber
    participant S1 as 🟢 Session 01 (Phase 1)
    participant Disk as 💾 Disk State (.bob/context & ROADMAP)
    participant S2 as 🔵 Session 02 (Phase 2)
    participant Archive as 📦 Tier 3 Storage (PLAN.md & History)

    Note over S1,Disk: PHIÊN 01 LÀM VIỆC VÀ HOÀN THÀNH PHASE 1
    S1->>Disk: Tích [x] toàn bộ task của Phase 1
    S1->>Disk: Kiểm tra Exit Criteria: PASSED
    S1->>Disk: Cập nhật ROADMAP.md (Phase 1: 100% complete)
    S1->>Archive: Toàn bộ chi tiết code/log Phase 1 chuyển thành Tier 3
    Note over S1: Đóng Session 01 — Xóa sạch Context Memory

    Note over Disk,S2: BẮT ĐẦU PHIÊN 02 — BẢO VỆ CONTEXT TUYỆT ĐỐI
    S2->>Disk: Kích hoạt /roadmap-navigator
    Disk->>Disk: Nhận diện Phase 1 đã [x] -> Bỏ qua không nạp
    Disk->>Disk: Đọc Phase 2 (Active Phase) -> Trích xuất open tasks
    Disk-->>S2: Chỉ nạp .bob/context/current-phase.md (192 tokens)
    Disk-->>S2: Chỉ nạp .bob/context/architecture.md (625 tokens)
    Note over S2: Session 02 bắt đầu với CHỈ ~817 tokens!<br/>(Thay vì 9,124+ tokens nếu mang theo Phase 1)
```

---

## 🗺️ 3. Bản Đồ Ánh Xạ Thông Tin Toàn Bộ Hệ Thống (Master Information Mapping)

Dưới đây là bảng ánh xạ toàn diện (Traceability Matrix) cho từng tập tin và thư mục trong `/home/pro/hackathon`:

```mermaid
graph LR
    subgraph IN ["1. Đầu Vào (Inputs)"]
        P1["planning/PROBLEM_STATEMENT.md"]
        P2["planning/BOB_USAGE_PLAN.md"]
        P3["planning/JUDGING_STRATEGY.md"]
        P4["planning/SUBMISSION_CHECKLIST.md"]
    end

    subgraph ENGINE ["2. Động Cơ Xử Lý (Engine)"]
        E1["src/roadmap.py (Progress & Snapshot)"]
        E2["src/scaffold.py (Structure & Audit)"]
        E3["src/benchmark.py (Token Simulation)"]
    end

    subgraph STATE ["3. Trạng Thái Ngữ Cảnh (3-Tier State)"]
        T1["Tier 1: architecture.md & LAYOUT.md"]
        T2["Tier 2: current-phase.md (192 tok)"]
        T3["Tier 3: PLAN.md & ROADMAP.md"]
    end

    subgraph RULES ["4. Kỹ Năng & Quy Tắc (Agent Rules)"]
        R1[".bob/skills/ (9 skills)"]
        R2[".bob/rules-*/ (plan-before-act)"]
        R3["src/hooks/roadmap_hook.py"]
    end

    subgraph PROOF ["5. Bằng Chứng & Sản Phẩm (Deliverables)"]
        D1["docs/BENCHMARK_REPORT.md"]
        D2["things/benchmark_results.json"]
        D3["slides/ (Presentation Deck)"]
        D4["bob_sessions/ (Screenshots)"]
        D5["media/ (3-min Video Demo)"]
    end

    IN --> |Tổng hợp| T3
    ENGINE --> |Vận hành| STATE
    STATE --> |Giới hạn ngữ cảnh| RULES
    RULES --> |Thực thi tạo tác| PROOF
    ENGINE --> |Đo lường kiểm chứng| D1
```

---

### Bảng Ánh Xạ Chi Tiết Từng Tập Tin (File-by-File Traceability Matrix)

| Đường Dẫn Tệp Tin | Phân Tầng Thông Tin | Vai Trò & Trách Nhiệm | Nguồn Chân Lý (Authority) | Ngân Sách / Kích Thước | Tần Suất Truy Cập LLM |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **`planning/*.md`** | Tầng 1: Chiến lược | Yêu cầu hackathon, tiêu chí chấm thi, ý tưởng thô | Tác giả dự án | ~8,500 tok | Đọc 1 lần khi `/roadmap-planner` |
| **`src/roadmap.py`** | Tầng 2: Engine CLI | Lôgic toán tiến độ, trích xuất snapshot, validate | Codebase Engine | 310 dòng stdlib | Thực thi qua terminal (0 tok LLM) |
| **`src/scaffold.py`** | Tầng 2: Engine CLI | Dựng cây thư mục 3-Tier, audit chuẩn token | Codebase Engine | 365 dòng stdlib | Thực thi qua terminal (0 tok LLM) |
| **`src/benchmark.py`** | Tầng 2: Engine CLI | Giả lập 10 sessions, đo lường token thực tế | Codebase Engine | ~250 dòng stdlib | Chạy khi kết xuất báo cáo |
| **`LAYOUT.md`** | Tầng 3: Tier 1 Context | Bản đồ cấu trúc code, components, database, logic | Trạng thái mã nguồn | 75 dòng (~500 tok) | Luôn nạp đầu phiên làm việc |
| **`.bob/context/architecture.md`** | Tầng 3: Tier 1 Context | Quyết định kiến trúc bất biến, stack, quy tắc | Trạng thái kiến trúc | **625 tokens** | Luôn nạp đầu phiên làm việc |
| **`.bob/context/current-phase.md`** | Tầng 3: Tier 2 Context | Danh sách open tasks của giai đoạn hiện tại | Engine tự động sinh | **192 tokens** | Luôn nạp đầu phiên làm việc |
| **`PLAN.md`** | Tầng 3: Tier 3 Storage | Master Plan đóng băng, Decisions Log, rủi ro | Kế hoạch dự án | 120 dòng (Tier 3) | Chỉ truy vấn qua Subagent khi cần |
| **`ROADMAP.md`** | Tầng 3: Tier 3 Storage | Bảng tiến độ sống, checkbox `[x]`, Change Log | Tiến độ thực tế | 108 dòng (Tier 3) | Đọc/Ghi bởi CLI và Agent |
| **`.bob/rules-*/`** | Tầng 4: Kỷ luật Agent | Ràng buộc Agent: Plan-Before-Act, không gọi thừa | Kỷ luật hệ thống | ~150 tok/mode | Nạp theo mode (`ask`, `plan`, `agent`) |
| **`.bob/skills/`** | Tầng 4: Kỹ năng Agent | 9 kỹ năng chuyên biệt điều phối vòng đời | Tập lệnh AI | Theo từng lệnh | Chỉ nạp khi skill được gọi |
| **`docs/BENCHMARK_REPORT.md`** | Tầng 5: Bằng chứng | Báo cáo đo lường tiết kiệm 91.13% token | Benchmark Engine | Báo cáo hoàn chỉnh | Hồ sơ nộp giám khảo |
| **`things/benchmark_results.json`** | Tầng 5: Dữ liệu thô | Kết quả đo đạc token thô của 10 sessions | Benchmark Engine | Dữ liệu số đo JSON | Phục vụ kiểm toán độc lập |
| **`slides/`** | Tầng 5: Trình chiếu | Bộ Slide 6–10 trang nộp thi hackathon | Đội ngũ dự thi | File PDF/PPTX | Hồ sơ nộp lablab.ai |
| **`bob_sessions/`** | Tầng 5: Minh chứng | Ảnh chụp màn hình phiên làm việc Bob IDE thực | Phiên thực tế | File ảnh `.png` | Minh chứng bắt buộc của ban tổ chức |
| **`media/`** | Tầng 5: Video Demo | Kịch bản & Video quay demo màn hình 3 phút | Đội ngũ dự thi | File `.mp4` | Trọng số chấm thi cao nhất |

---

## 🎯 4. Lộ Trình Triển Khai Thực Tế (Execution Milestones)

```mermaid
timeline
    title Lộ Trình Triển Khai RoadmapFlow
    section Kỹ Thuật Đã Hoàn Thành
        Khởi tạo Bản đồ & Hạ tầng : layout-init : roadmap-scaffold : LAYOUT.md : 3-Tier Folder
        Đóng băng Kế hoạch : roadmap-planner : PLAN.md : ROADMAP.md : Decisions Log
        Kiểm Thử & Đồng Bộ : dev-workflow : roadmap-sync : 7/7 Unit Tests PASS : Plugin Tests PASS
        Đo Lường Thực Nghiệm : roadmap-benchmark : 91.13% single-session : 110k tokens saved
    section Hồ Sơ Nộp Thi (Đang Triển Khai)
        Văn bản Thuyết minh : PROBLEM_STATEMENT.md (≤500 words) : BOB_USAGE_PLAN.md (≤500 words)
        Bộ Slide Thuyết trình : slides/ (6-10 slides Problem, Architecture, Demo, Metrics)
        Minh chứng Thực nghiệm : bob_sessions/ (Ảnh chụp Agent mode sessions)
        Video Trình diễn : media/ (3-min MP4 video demo)
        Nộp bài lablab.ai : Hoàn tất form & URL trước deadline
```

---

## 🔗 Liên Kết Tới Các Ghi Chú Liên Quan
- Trở về mục lục chính: [[README|🧭 MOC]]
- Kiến trúc chi tiết: [[01-RoadmapFlow-Architecture|🏗️ 01. Kiến Trúc & Mô Hình 3-Tier]]
- Chi tiết thực thi 9 skills: [[02-Skills-Lifecycle-Review|⚡ 02. Đánh Giá Vòng Đời 9 Skills]]
- Số liệu thực nghiệm chi tiết: [[03-Empirical-Token-Benchmark|📊 03. Đo Lường Token Thực Nghiệm]]
- Ma trận kiểm thử & bằng chứng: [[04-Verification-Matrix|🛡️ 04. Ma Trận Xác Minh & Tuân Thủ]]
