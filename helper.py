import os
from PIL import Image

def add_logo_to_images(image_dir, logo_path, output_size=(700, 700), logo_size=(130, 130), margin=30):
    # 1. Kiểm tra đường dẫn logo
    if not os.path.exists(logo_path):
        print(f"Lỗi: Không tìm thấy file logo tại {logo_path}")
        return

    # 2. Tạo thư mục lưu kết quả để tránh ghi đè ảnh gốc
    output_dir = os.path.join(image_dir, "output_images")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 3. Mở và xử lý Logo
    try:
        logo = Image.open(logo_path).convert("RGBA")
        # Resize logo về 100x100 (giữ tỉ lệ hoặc ép size tùy nhu cầu, ở đây dùng thumbnail để giữ tỉ lệ đẹp nhất)
        logo.thumbnail(logo_size, Image.Resampling.LANCZOS)
    except Exception as e:
        print(f"Lỗi khi mở logo: {e}")
        return

    print("Đang bắt đầu xử lý ảnh...")

    # 4. Duyệt qua tất cả các file trong thư mục
    count = 0
    for filename in os.listdir(image_dir):
        # Chỉ xử lý các file ảnh phổ biến
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.webp')):
            img_path = os.path.join(image_dir, filename)
            
            try:
                # Mở ảnh gốc
                img = Image.open(img_path)
                
                # Resize ảnh nền về 700x700
                img = img.resize(output_size, Image.Resampling.LANCZOS)
                
                # Chuyển ảnh nền sang RGBA để xử lý transparency nếu cần
                img = img.convert("RGBA")

                # Tính toán vị trí chèn logo (Góc dưới bên trái)
                # X = margin
                # Y = Chiều cao ảnh - Chiều cao logo - margin
                pos_x = margin
                pos_y = output_size[1] - logo.height - margin
                
                # Chèn logo (tham số thứ 3 là mask để giữ độ trong suốt của logo)
                img.paste(logo, (pos_x, pos_y), logo)

                # Lưu ảnh
                # Nếu ảnh gốc là JPG thì phải chuyển về RGB trước khi lưu, PNG thì giữ RGBA
                save_path = os.path.join(output_dir, filename)
                
                if filename.lower().endswith(('.jpg', '.jpeg')):
                    img = img.convert("RGB")
                    img.save(save_path, "JPEG", quality=95)
                else:
                    img.save(save_path, "PNG")

                count += 1
                print(f"Đã xử lý: {filename}")

            except Exception as e:
                print(f"Không thể xử lý file {filename}: {e}")

    print("---")
    print(f"Hoàn tất! Đã xử lý {count} ảnh.")
    print(f"Ảnh mới được lưu tại: {output_dir}")

# --- CẤU HÌNH ĐƯỜNG DẪN ---
# Lưu ý: Thêm chữ r trước chuỗi để tránh lỗi ký tự đặc biệt trong đường dẫn Windows

SOURCE_FOLDER = r"D:\Acer\Code\Flower-Store\media\flowers"
LOGO_FILE = r"D:\Acer\Code\Flower-Store\shop_flower\static\logo.jpg"

# Chạy hàm
add_logo_to_images(SOURCE_FOLDER, LOGO_FILE)