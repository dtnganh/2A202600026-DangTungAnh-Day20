# Benchmark Report

**Note:** Quality Score was evaluated manually by submitting the final answers to Gemini Pro.

| Run | Latency (s) | Cost (USD) | Quality | Notes |
|---|---:|---:|---:|---|
| baseline | ~ 5.00 | ~ 0.0004 | 4.0/10 | Baseline viết chung chung, không có trích dẫn. |
| multi-agent | ~ 162.00 | ~ 0.0050 | 9.0/10 | Multi-agent phân tích chi tiết, dẫn chứng chính xác, bám sát SOTA 2024. |

## Traces
- LangSmith Trace Link: *(Đã xem trên web)*

## Failure Modes & Fixes
- **Lỗi nhỏ:** Đặc vụ Supervisor tự ý trả về `"done"` thay vì `"critic"` sau khi `writer` chạy xong, khiến bước Critic bị bỏ qua. 
- **Cách khắc phục:** Trong đồ thị LangGraph (`workflow.py`), nối cứng cạnh (hard-code edge) từ `writer` sang `critic` để ép buộc việc kiểm tra chéo luôn được thực hiện.

---

## Chi tiết đánh giá từ Giám khảo Gemini (LLM-as-a-judge)

### Đánh giá Bài 1 (Baseline)
- **Độ sâu và tính cập nhật (Information Quality & Depth):** Bài viết này mắc một lỗi rất phổ biến của các mô hình ngôn ngữ thế hệ cũ: tính chung chung (generic). Tác giả chỉ đang giải thích khái niệm ghép giữa "Graph" và "RAG" theo cách suy diễn logic chứ không hề nắm bắt được "state-of-the-art" hiện tại. Bài viết hoàn toàn bỏ lỡ công trình đột phá của Microsoft Research về GraphRAG ra mắt vào đầu năm 2024.
- **Độ tin cậy (Citations):** Hoàn toàn không có trích dẫn hay danh mục tài liệu tham khảo nào. Trong nghiên cứu học thuật, một bài tổng quan không có trích dẫn là vô giá trị.
- **Cấu trúc và văn phong (Structure & Tone):** Cấu trúc bài viết mạch lạc. Văn phong khá chuẩn mực nhưng vì nội dung trống rỗng, văn phong này giống như bài viết blog cơ bản.

### Đánh giá Bài 2 (Multi-Agent)
- **Độ sâu và tính cập nhật (Information Quality & Depth):** Rất xuất sắc. Bài viết đã bám sát được đúng "state-of-the-art" hiện tại khi nhắc đến nghiên cứu cốt lõi của Microsoft Research (2024). Tác giả đã đưa ra được ví dụ thực chứng cụ thể (dataset VIINA), nêu bật được ưu điểm vượt trội của GraphRAG.
- **Độ tin cậy (Citations):** Thực hiện rất tốt. Có trích dẫn trong văn bản (in-text citations) và danh sách tham khảo (References) ở cuối bài.
- **Cấu trúc và văn phong (Structure & Tone):** Cấu trúc chặt chẽ, luận điểm rõ ràng. Tác giả sử dụng các thuật ngữ chuyên ngành cực kỳ chuẩn xác ("provenance", "grounded in the dataset").
