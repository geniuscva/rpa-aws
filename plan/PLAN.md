# Agentic OS — Jarvis trên macOS với thư viện Agent Skills riêng

## 1. Mục tiêu và phạm vi

Xây MVP cá nhân dùng thật: giao việc bằng chat tiếng Việt/Anh, dùng **Kiro CLI** để suy luận và điều khiển **browser riêng, Finder, TextEdit**. Agent có thể khám phá và nạp Agent Skills; Dashboard hiển thị toàn bộ thư viện skills của ứng dụng.

Đã kiểm chứng Kiro CLI **2.25.0** trên máy: handshake ACP thành công, hỗ trợ tải session và nhận ảnh. Đăng nhập/quota cần kiểm tra bằng prompt thật khi triển khai.

Ba workflow nghiệm thu:

- Research web, tổng hợp có nguồn và lưu Markdown.
- Tìm file trong folder đã cấp quyền, mở hoặc reveal trong Finder.
- Soạn tài liệu UTF-8 và mở bằng TextEdit.

Chat làm trước; voice, wake word, email/calendar, app khác và chạy nền khi app đã thoát làm sau.

## 2. Kiến trúc

**React UI → Desktop host → Kiro qua ACP → MCP gateway → Skills / Browser / File / macOS executors**

- **Stack:** pnpm workspace; Electron + React + TypeScript + Vite; SQLite; Playwright; Swift helper.
- **Kiro:** adapter JSON-RPC qua stdio, engine V2, executable tuyệt đối và custom agent `agenticos`. Kiro quản lý agent loop; ứng dụng quản lý tác vụ, quyền, skills và evidence. ACP kết nối client với agent, MCP kết nối agent với công cụ. [Kiro ACP](https://kiro.dev/docs/acp/).
- **Quyền công cụ:** custom agent chỉ truy cập MCP của Agentic OS; không bật built-in shell/file tools, hooks hoặc subagents. Không sửa cấu hình Kiro toàn cục.
- **Browser:** Chromium riêng có cửa sổ quan sát, profile riêng; người dùng đăng nhập thủ công. Playwright thực hiện điều hướng và thao tác theo DOM. [Playwright](https://playwright.dev/docs/browser-contexts).
- **Native:** Swift helper với adapter Finder/TextEdit, target theo Accessibility element; không cung cấp click tọa độ hay AppleScript tùy ý.
- **Electron:** renderer sandbox, context isolation, IPC có schema và kiểm tra sender; renderer không truy cập trực tiếp filesystem/process. [Electron security](https://www.electronjs.org/docs/latest/tutorial/security).
- **Lưu trữ:** SQLite cho conversation, task, event, approval, artifact, memory và skill registry. Dữ liệu nằm trong `~/Library/Application Support/AgenticOS`.

Interface nội bộ: `AgentBackend`, `ToolGateway`, `TaskStore`, `MemoryStore`, `SkillRegistry`. Không xây thêm agent loop bằng LangGraph trong MVP.

## 3. Agent Skills và Dashboard

**Nguồn duy nhất là thư viện riêng của Agentic OS**, theo lựa chọn của bạn. Không tự quét thư viện Kiro, Codex hoặc `.agents`.

### Thư viện

- Import từ folder local chứa `SKILL.md`, sao chép cả `references/`, `assets/`, `scripts/` vào thư viện ứng dụng.
- Kiểm tra YAML frontmatter có `name`, `description`; lưu ID nội bộ, nguồn import, content hash, thời điểm import và trạng thái bật/tắt.
- Chặn symlink/path traversal thoát khỏi package. Tên trùng không tự ghi đè; UI cho chọn thay thế hoặc giữ cả hai bằng ID riêng.
- Skill mới import mặc định tắt; người dùng xem nội dung rồi bật.
- MVP hỗ trợ instructions, references và assets. Script được giữ trong package nhưng chưa được thực thi; Dashboard hiển thị giới hạn này.

### Khám phá và nạp

Kiro mô tả skills theo cơ chế khám phá metadata rồi nạp hướng dẫn khi cần. [Kiro Agent Skills](https://kiro.dev/docs/skills/).

Agentic OS triển khai cơ chế này qua MCP riêng để Dashboard và agent dùng cùng một registry:

- Khi bắt đầu lượt, chỉ đưa metadata của skills đang bật vào ngữ cảnh.
- Agent chọn skill phù hợp rồi gọi `skills.load(skillId)` để nạp `SKILL.md`.
- `skills.readResource(skillId, relativePath)` đọc reference/asset trong package khi cần.
- Người dùng chọn skill từ Dashboard hoặc gõ `/skill` để app giải quyết đúng ID và nạp hướng dẫn trước khi gửi prompt qua ACP; không phụ thuộc slash command riêng của terminal Kiro.
- Mỗi tác vụ lưu skill ID và hash phiên bản đã nạp. UI chỉ báo “Đã nạp” khi có sự kiện load thành công.
- Tắt hoặc thay thế skill áp dụng cho lượt mới; tác vụ hiện tại giữ snapshot đã nạp. Xóa skill không tự xóa artifact đã tạo.
- Skill không được nâng quyền công cụ. Yêu cầu shell, connector hoặc capability chưa hỗ trợ được báo rõ, không tự cài hay cấp quyền.

### Dashboard

- Tổng quan: tác vụ đang chạy, đang chờ duyệt, gần đây và số skills đang bật.
- Trang **Skills**: danh sách tên, mô tả, nguồn, trạng thái, khả năng tương thích; tìm kiếm và lọc.
- Chi tiết skill: xem `SKILL.md`, tài nguyên đi kèm, hash, lịch sử sử dụng.
- Thao tác: import folder, bật/tắt, dùng trong chat, thay thế package và xóa khỏi thư viện.
- Chat hiển thị skills đã nạp, tiến độ, approval, kết quả và nút dừng.
- Có cửa sổ chính, menu bar và phím tắt mở nhanh; giao diện tối, ưu tiên nội dung và trạng thái.

## 4. Tự chủ và phục hồi

- Tự đọc trong folder/domain đã cấp; tự tạo file mới trong workspace.
- Gửi, submit, upload, xóa, ghi đè, thay đổi tài khoản hoặc action chưa xác định được tác động cần preview và approval.
- Approval gắn đúng action/arguments; gateway kiểm tra lại ngay trước thực thi. Native chỉ cho phép Finder/TextEdit và action đã định nghĩa.
- Web/file/skill là nội dung không được dùng để thay đổi policy.
- Trạng thái task: `queued`, `running`, `awaiting_approval`, `interrupted`, `completed`, `failed`, `cancelled`.
- Sau crash, kiểm tra trạng thái trang/file trước khi tiếp tục; không tự retry thao tác ghi có kết quả chưa rõ.
- Cancel gửi ACP cancellation, chặn action mới và kết thúc process do app quản lý khi hết timeout.
- Thiếu CLI, đăng nhập/quota, mạng hoặc quyền macOS có thông báo phục hồi. Không tự nâng cấp Kiro.
- Mặc định một tác vụ điều khiển đang chạy, tối đa 30 tool calls mỗi lượt; không lưu raw screenshot hay credential trong log.

## 5. Triển khai và nghiệm thu

1. **Foundation:** cấu trúc repo, research có nguồn, Electron shell, SQLite migrations và onboarding Kiro.
2. **ACP:** chat streaming, session load, permissions, cancel và kiểm tra prompt thật.
3. **Skills:** registry, import, Dashboard, MCP loader và lựa chọn skill trong chat.
4. **Executors:** browser, file, Finder/TextEdit, approval và artifact viewer.
5. **Reliability & packaging:** memory, crash recovery, đóng gói `.app`/`.dmg` cho Apple Silicon.

Kiểm thử bằng Vitest, Playwright và kiểm tra native trên máy:

- Ba workflow chạy xuyên suốt bằng Kiro, có evidence xác nhận.
- Import skill hợp lệ, lỗi frontmatter, tên trùng, path traversal và thiếu capability.
- Agent tự chọn skill; người dùng chọn skill trực tiếp; tài nguyên chỉ được nạp khi cần.
- Skill tắt không xuất hiện trong catalog; phiên bản được ghi đúng trong task history.
- Skill yêu cầu vượt quyền bị chặn; script không tự chạy.
- Restart/chờ duyệt không lặp thao tác ghi; từ chối approval không gây thay đổi.
- Cancel, lỗi CLI/JSON-RPC và thiếu quyền không làm treo UI.
- Xóa memory loại nội dung khỏi retrieval; log không chứa credential.

**Mặc định:** một người dùng, một máy, model theo cấu hình Kiro; thư viện skills riêng, import local trong MVP. Kiro sử dụng dịch vụ cloud; không cần API key OpenAI/Anthropic riêng. Voice và marketplace skills sẽ được bổ sung sau.
