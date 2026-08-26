# Checklist test Swagger - Event Management API

Mở `http://127.0.0.1:8000/docs`. Dùng ba tài khoản chưa tồn tại: Owner, Member và Outsider. Đăng nhập từng tài khoản, lưu `OWNER_TOKEN`, `MEMBER_TOKEN`, `OUTSIDER_TOKEN` và nhập `Bearer <access_token>` bằng nút **Authorize**. Lưu các ID được tạo trong quá trình test.

## 1. Auth và token

| [ ] | Case | Kết quả mong đợi |
| --- | --- | --- |
| [ ] | `GET /health` | `200`, body có `status: "ok"`. |
| [ ] | `POST /auth/register` với email/password/full_name hợp lệ | `201`. |
| [ ] | Đăng ký lại email trên | `409`. |
| [ ] | Đăng ký email sai hoặc password dài hơn 72 ký tự | `422`. |
| [ ] | `POST /auth/login` đúng email/password | `200`, có access và refresh token. |
| [ ] | Login sai mật khẩu | `401`. |
| [ ] | `POST /auth/refresh` với refresh token hợp lệ | `200`, nhận token mới. |
| [ ] | Refresh token không hợp lệ/dùng access token | `401`; body thiếu trường bắt buộc là `422`. |
| [ ] | `GET /users/me` với token hợp lệ | `200`, đúng user hiện tại. |
| [ ] | `GET /users/me` thiếu hoặc sai token | `401`. |

## 2. Event CRUD, search, phân quyền

| [ ] | Case | Kết quả mong đợi |
| --- | --- | --- |
| [ ] | Owner: `POST /events` body `{ "name": "Swagger Event", "description": "Test" }` | `201`; lưu `event_id`. |
| [ ] | Owner: `GET /events` | `200`, có event vừa tạo. |
| [ ] | Owner: `GET /events?search=Swagger` | `200`, có event vừa tạo. |
| [ ] | Owner: `GET /events?search=khong-co` | `200`, danh sách rỗng. |
| [ ] | Owner: `GET /events/{event_id}` | `200`. |
| [ ] | Outsider: `GET /events/{event_id}` | `403`. |
| [ ] | Owner: `GET /events/999999` | `404`. |
| [ ] | Owner: tạo event có `name` 1 ký tự | `422`. |
| [ ] | Owner: `PATCH /events/{event_id}` đổi name hợp lệ | `200`, name được cập nhật. |
| [ ] | Member/Outsider: `PATCH /events/{event_id}` | `403`. |
| [ ] | Owner: cập nhật name 1 ký tự | `422`. |

## 3. Xác nhận owner được tạo trong `event_staff`

| [ ] | Case | Kết quả mong đợi |
| --- | --- | --- |
| [ ] | Ngay sau khi tạo event, Owner gọi `GET /events/{event_id}/members` | `200`; có bản ghi `user_id` là ID Owner và `role: "OWNER"`. |
| [ ] | Kiểm tra lại số bản ghi Owner của event mới tạo | Chỉ có một Owner. |
| [ ] | Owner gọi `DELETE /events/{event_id}/members/{owner_id}` | `400`; không được xóa owner cuối cùng. |

## 4. Thành viên event

| [ ] | Case | Kết quả mong đợi |
| --- | --- | --- |
| [ ] | Owner: `POST /events/{event_id}/members` với `{ "user_id": member_id }` | `201`, role là `MEMBER`. |
| [ ] | Member: `GET /events/{event_id}/members` | `200`, thấy Owner và Member. |
| [ ] | Owner thêm lại cùng Member | `409`. |
| [ ] | Owner thêm chính owner_id | `409`. |
| [ ] | Owner thêm user_id không tồn tại | `404`. |
| [ ] | Member hoặc Outsider thêm thành viên | `403`. |
| [ ] | Owner xóa Member | `200`; Member gọi `GET /events/{event_id}` nhận `403`. |
| [ ] | Owner thêm lại Member để tiếp tục test task | `201`. |

## 5. Task, comment, attachment

| [ ] | Case | Kết quả mong đợi |
| --- | --- | --- |
| [ ] | Owner: `POST /events/{event_id}/event-tasks` với title hợp lệ, `assignee_id=member_id`, `status=TODO`, `priority=HIGH` | `201`; lưu `task_id`. |
| [ ] | Member tạo task | `201`. |
| [ ] | Tạo task giao cho Outsider | `422`. |
| [ ] | Tạo task với status/priority không hợp lệ | `422`. |
| [ ] | Member: `GET /events/{event_id}/event-tasks?status=TODO&priority=HIGH&page=1&page_size=3` | `200`; chỉ có task phù hợp. |
| [ ] | Danh sách task có `page=0` | `422`. |
| [ ] | Outsider: `GET /event-tasks/{task_id}` | `403`. |
| [ ] | Member được giao: `PATCH /event-tasks/{task_id}` đổi `status=IN_PROGRESS` | `200`. |
| [ ] | Member không được giao: đổi title task | `403`. |
| [ ] | Owner đổi title/priority task | `200`. |
| [ ] | Cập nhật status/priority không hợp lệ | `422`. |
| [ ] | Member: `POST /event-tasks/{task_id}/comments` với content hợp lệ | `201`; `GET .../comments` trả comment đó. |
| [ ] | Comment rỗng | `422`. |
| [ ] | Member: `POST /event-tasks/{task_id}/attachments`, chọn file nhỏ ở field `file` | `201`. |
| [ ] | Upload không gửi field `file` | `422`. |
| [ ] | Member xóa task | `403`; Owner xóa task | `200`; sau đó GET task là `404`. |

## 6. Activity log và xóa dữ liệu cuối luồng

| [ ] | Case | Kết quả mong đợi |
| --- | --- | --- |
| [ ] | Owner/Member: `GET /events/{event_id}/activity-logs` | `200`; có tối thiểu `EVENT_CREATED`, `EVENT_MEMBER_ADDED`, `TASK_CREATED`. |
| [ ] | Outsider: `GET /events/{event_id}/activity-logs` | `403`. |
| [ ] | Member: `DELETE /events/{event_id}` | `403`. |
| [ ] | Owner: `DELETE /events/{event_id}` | `200`. |
| [ ] | Owner: `GET /events/{event_id}` sau khi xóa | `404`. |

> Chỉ xóa event sau cùng, vì activity log và các dữ liệu liên quan sẽ không còn để kiểm tra.
