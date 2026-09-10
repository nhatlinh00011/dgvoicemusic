# DG Music Splitter

Ứng dụng web local để tách vocal/nhạc cụ và chuyển audio thành MIDI, không cần API key hay dịch vụ AI trả phí.

## Tính năng
- Upload MP3/WAV/M4A/FLAC
- Tách 4 stem bằng Demucs:
  - Vocal
  - Drums
  - Bass
  - Other
- Tạo Instrumental bằng cách lấy phần `other + drums + bass`
- Chuyển audio sang MIDI bằng Spotify Basic Pitch
- Giao diện mobile-friendly
- Chạy local, file nhạc không phải gửi lên dịch vụ bên ngoài

## Yêu cầu
- Python 3.10 hoặc 3.11
- FFmpeg
- RAM càng nhiều càng tốt; GPU NVIDIA giúp Demucs chạy nhanh hơn

> Lưu ý: Demucs là mô hình AI khá nặng. Bản này chạy AI ở máy chạy Python, không phải trực tiếp trong trình duyệt iPhone.

## Cài đặt

### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Windows
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Cài FFmpeg và bảo đảm lệnh `ffmpeg` chạy được trong Terminal/CMD.

## Chạy
```bash
python app.py
```

Mở:
```text
http://127.0.0.1:8000
```

Nếu muốn truy cập từ iPhone cùng Wi-Fi, chạy:
```bash
python app.py
```
sau đó mở địa chỉ IP của máy tính:
```text
http://IP-MAY-TINH:8000
```

## Tách nhạc
Upload file → chọn `Tách Vocal/Nhạc cụ` → chờ xử lý → tải các stem.

## Tách giai điệu
Chọn `Tạo MIDI`. Basic Pitch hoạt động tốt nhất khi nguồn là một nhạc cụ/nguồn tương đối đơn; với cả bài hát hoàn chỉnh, MIDI có thể chứa nhiều nốt và cần chỉnh sửa lại.

## GitHub
Có thể tạo repository mới rồi upload toàn bộ thư mục này. Không đưa API key vào source vì app này không cần API key.

## Giấy phép
Mã nguồn của dự án mẫu này do bạn sử dụng tùy ý. Hãy đọc giấy phép của các mô hình/thư viện Demucs và Basic Pitch trước khi phân phối sản phẩm thương mại.
