---
description: Workflow tạo báo cáo tự động bằng cách "clone" phong cách từ website thương hiệu.
---

# /brand-report - Báo cáo Theo Phong cách Thương hiệu

Sử dụng workflow này khi bạn muốn tạo một báo cáo có thiết kế y hệt một công ty nào đó chỉ bằng cách cung cấp URL website của họ.

## Quy trình "One-Prompt" Tự động

Bạn chỉ cần cung cấp thông tin theo mẫu:
> "Chạy /brand-report cho dữ liệu trong file [tên_file] theo style của website [địa_chỉ_url]"

### Các bước AI sẽ thực hiện tự động:

1.  **Crawl Thương hiệu**: dùng một browser tool có sẵn (`chrome-devtools` MCP, `playwright` MCP, hoặc `ego-browser`) truy cập website để lấy:
    - Logo chính thức.
    - Bảng màu đặc trưng (màu Primary, Secondary).
    - Font chữ và phong cách thiết kế (Dark/Light mode).

2.  **Thiết kế Layout**: áp dụng thông tin trên vào một hệ thống thiết kế báo cáo đồng bộ — dùng skill `ui-ux-pro-max` nếu có, hoặc skill `brand`/`frontend-design`.

3.  **Xử lý Dữ liệu**: Đọc file text của bạn và chuyển đổi thành các block nội dung chuyên nghiệp (biểu đồ, bảng, callout).

4.  **Xuất bản PDF**: Dùng skill `minimax-pdf` (trong chính plugin này) để render kết quả cuối cùng ra file PDF chất lượng cao.

## Ví dụ thực tế

**Input**:
- File: `marketing_results_q1.txt`
- Website: `https://www.tesla.com`

**Kết quả**: AI sẽ tạo một báo cáo PDF với:
- Logo Tesla ở trang bìa.
- Tông màu đỏ/đen/trắng đặc trưng của Tesla.
- Font chữ hiện đại, tối giản.
- Các biểu đồ được render theo màu của thương hiệu.

## Skills / tools used

- This command orchestrates the steps above directly (no external orchestrator skill needed).
- `minimax-pdf` skill — PDF rendering (this plugin)
- A browser tool — crawl brand (chrome-devtools / playwright / ego-browser)
- `ui-ux-pro-max` (if available) or `brand` / `frontend-design` — design system
