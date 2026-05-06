# Design Template

## Problem

Xây dựng một hệ thống Multi-Agent Research Assistant có khả năng nhận câu hỏi phức tạp từ người dùng, tự động tìm kiếm trên mạng, phân tích thông tin và viết ra câu trả lời chi tiết kèm theo dẫn chứng cụ thể.

## Why multi-agent?

Single-agent (chỉ dùng 1 model LLM làm tất cả từ đầu đến cuối) thường dễ mắc lỗi "hallucination" (bịa thông tin), bị quá tải context khi đọc nhiều nguồn, và không có bước tự kiểm tra (self-reflection). Sử dụng kiến trúc Multi-Agent giúp chia nhỏ công việc ra: một con chuyên tìm kiếm (Researcher), một con chuyên phân tích độ tin cậy (Analyst), một con chuyên viết bài (Writer) và một con bắt lỗi (Critic). Điều này đảm bảo chất lượng, độ chính xác cao hơn và dễ debug hơn.

## Agent roles

| Agent | Responsibility | Input | Output | Failure mode |
|---|---|---|---|---|
| Supervisor | Điều phối các agent, quyết định xem ai làm bước tiếp theo dựa trên trạng thái hiện tại. | `ResearchState` | Cập nhật `route_history` | Kẹt trong vòng lặp vô hạn (loop) -> Fix: Giới hạn max iterations. |
| Researcher | Tìm kiếm thông tin trên web và tổng hợp thành ghi chú nghiên cứu. | Câu hỏi từ User và feedback từ Critic | `sources`, `research_notes` | Không tìm ra thông tin -> Fix: Retry với query khác. |
| Analyst | Trích xuất các ý chính, so sánh đối chiếu và tìm điểm yếu của dữ liệu. | `research_notes` | `analysis_notes` | Nhận diện sai luận điểm do nội dung quá dài. |
| Writer | Tổng hợp thông tin để viết ra câu trả lời cuối cùng, kèm dẫn chứng. | `research_notes`, `analysis_notes` | `final_answer` | Không dẫn link nguồn (citation) -> Fix: Prompt Critic bắt bẻ lỗi này. |
| Critic | Đọc lại câu trả lời và bắt lỗi (fact-check, citation, hallucination). | `final_answer` | `critic_feedback` (hoặc 'PASS') | Bắt bẻ những chi tiết nhỏ nhặt quá mức, gây lặp lại. |

## Shared state

Các field trong `ResearchState` và lý do:
- `request`: Lưu lại câu hỏi ban đầu để các node không bị quên.
- `iteration` & `route_history`: Để Supervisor biết đồ thị đang chạy đến đâu và chặn vòng lặp vô hạn.
- `sources`: Lưu trữ tài liệu gốc từ Web.
- `research_notes`: Ghi chú do Researcher tạo ra.
- `analysis_notes`: Ghi chú phân tích do Analyst tạo ra.
- `critic_feedback`: Phản hồi lỗi từ Critic để các Agent khác đọc và sửa chữa.
- `final_answer`: Kết quả hiển thị cuối cùng.

## Routing policy

Luồng chạy được xây dựng bằng LangGraph:
`START` -> `Supervisor` 
Từ `Supervisor` sử dụng Conditional Edges dựa trên LLM để trỏ tới 1 trong 4 agent: `Researcher`, `Analyst`, `Writer`, `Critic` hoặc kết thúc ở `END`. Sau khi các worker xử lý xong, mũi tên sẽ trỏ ngược về lại `Supervisor` để quyết định tiếp.

## Guardrails

- Max iterations: `6` (Lấy từ biến môi trường để chống vòng lặp vô hạn).
- Timeout: `60s` (Config mặc định).
- Retry: Nếu LLM lỗi thì trả về `ResearchState` với list `errors` và tính là Error rate = 1.0.
- Fallback: Nếu route do LLM trả về không hợp lệ, Supervisor ép chuyển thành `done`.
- Validation: CriticAgent làm nhiệm vụ validate nội dung cuối cùng.

## Benchmark plan

- **Query**: "Research GraphRAG state-of-the-art and write a 500-word summary"
- **Metric**: Latency (giây), Cost (USD, dự đoán bằng số lượng token x giá $0.15/1M input & $0.60/1M output), Quality Score (1-10, đo bằng Gemini), Error Rate.
- **Expected Outcome**: Multi-Agent sẽ chậm hơn và tốn tiền hơn Single-Agent, nhưng Quality Score sẽ cao hơn hẳn và có dẫn chứng đáng tin cậy hơn.
