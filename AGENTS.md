# CLAUDE.md

## Tổng quan
CameraSICK-Integrated là thử nghiệm điều khiển camera công nghiệp qua thư viện **IC Imaging Control 4** (`imagingcontrol4`, The Imaging Source): liệt kê thiết bị, mở camera, cấu hình (Mono8, 640x480, ROI, exposure), chụp ảnh đơn bằng `SnapSink`, ghi video MP4/H264 và hiển thị live qua `QueueSink` + OpenCV.

## Cấu trúc
- `SICKCamera/Code.ipynb` — notebook chính, chạy tuần tự từng cell (init `ic4.Library`, enum thiết bị/interface, mở `Grabber`, set property, snap ảnh, ghi clip, live listener).
- `SICKCamera/test.bmp`, `test2.bmp`, `clip.mp4` — ảnh/video mẫu notebook xuất ra.
- `imagingcontrol4/` — bản sao (vendored) thư viện Python `imagingcontrol4` của The Imaging Source (kèm binding PySide6). **Không sửa**; nâng cấp bằng `pip install -U imagingcontrol4` thay vì sửa tay. Giấy phép thuộc nhà cung cấp.
- `ic4-examples` — gitlink (submodule) rỗng, không có `.gitmodules` nên không clone được nội dung; tham chiếu tới repo ví dụ của The Imaging Source.

## Môi trường
Python 3.11 (các file `.pyc` cũ là cpython-311), Windows, driver/GenTL của camera đã cài, camera kết nối thật. Cần: `imagingcontrol4`, `opencv-python`, `numpy`, (tùy chọn) `PySide6`.

## Quy tắc khi làm việc
- Notebook điều khiển phần cứng thật: không tự chạy cell mở camera/ghi file khi chưa được yêu cầu.
- Không commit `__pycache__/`, `*.pyc`, file `.dll` runtime, dữ liệu ảnh/video lớn.
- Cell cuối dùng `cv2` nhưng notebook chưa `import cv2` — thêm import khi chỉnh sửa.
- Không đưa serial/IP thiết bị thật vào mã hoặc commit.
