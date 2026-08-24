# Event Management API

Backend FastAPI quản lý sự kiện, dùng MySQL, JWT và phân quyền chủ sự kiện/thành viên/quản trị viên. Mọi nội dung phản hồi do API trả về đều bằng tiếng Việt.

## Cài đặt

1. Tạo database bằng MySQL Workbench:

```sql
CREATE DATABASE event_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. Tạo môi trường và cài thư viện:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

3. Sửa `DATABASE_URL` và `SECRET_KEY` trong `.env`, sau đó chạy:

```powershell
uvicorn app.main:app --reload
```

Mở Swagger tại `http://127.0.0.1:8000/docs`. Bảng MySQL được tạo tự động khi ứng dụng khởi động.

## Health check và lỗi

- `GET /health` trả về `{"status": "ok"}` khi API đang sẵn sàng nhận yêu cầu.
- Mọi lỗi API đều có cùng cấu trúc: `{"success": false, "error": {"code": "NOT_FOUND", "message": "..."}}`.
- Lỗi dữ liệu đầu vào (`422`) có thêm `error.details` để chỉ ra các trường không hợp lệ. Các lỗi cơ bản gồm `BAD_REQUEST` (400), `FORBIDDEN` (403) và `NOT_FOUND` (404).
- Giới hạn mặc định là 100 yêu cầu mỗi 60 giây cho mỗi địa chỉ IP. Cấu hình bằng `RATE_LIMIT_REQUESTS` và `RATE_LIMIT_WINDOW_SECONDS`; khi vượt ngưỡng API trả `429 RATE_LIMITED` kèm header `Retry-After`.

## API chính

- `POST /auth/register`, `POST /auth/login`, `POST /auth/refresh`
- `GET /users/me`, `GET /users` (Admin)
- CRUD `/events`, quản lý `/events/{event_id}/members`
- CRUD công việc qua `/events/{event_id}/event-tasks` và `/event-tasks/{task_id}`
- `GET /event-tasks/{task_id}/comments` lấy các bình luận của công việc.
- `GET /events/{event_id}/activity-logs` xem lịch sử hoạt động của sự kiện.
- Bonus: bình luận và tải tệp đính kèm cho công việc.

Token đăng nhập được gửi theo dạng `Authorization: Bearer <access_token>`.
