# Bot Shop Discord

Bot tạo trang chủ shop và hệ thống nút tương tác theo yêu cầu.

## Thiết lập

1. Cài dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Thiết lập biến môi trường:
   - `DISCORD_TOKEN`: token bot Discord.
   - `HOME_CHANNEL_ID`: ID kênh nơi embed Trang chủ sẽ xuất hiện duy nhất.
3. Chạy bot:
   ```bash
   python bot.py
   ```

## Hành vi

- Khi bot khởi động, embed **Trang chủ** sẽ được tạo ở kênh `HOME_CHANNEL_ID` nếu chưa có.
- Nhấn **Cày Thuê** sẽ mở 4 nút: Sea event, Farm, Item, Race.
- Chọn danh mục sẽ hiển thị embed danh sách sản phẩm kèm menu chọn (dropdown).
- Các embed hiển thị cho người nhấn là dạng ephemeral.

## Lệnh

- `/tao-trang-chu`: tạo lại trang chủ (chỉ admin).
