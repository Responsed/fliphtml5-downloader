# -*- coding: utf-8 -*-
import requests
import json
import os
import re
import time
import subprocess
import sys
from fpdf import FPDF
from PIL import Image
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_config_data(book_url):
    """
    Tải và phân tích tệp config.js để lấy siêu dữ liệu sách và thông tin trang.
    """
    if book_url.endswith('/'):
        book_url = book_url[:-1]
    config_url = f"{book_url}/javascript/config.js"
    
    print(f"[*] Đang lấy cấu hình từ: {config_url}")
    try:
        response = requests.get(config_url)
        response.raise_for_status()
        # Ép kiểu mã hóa UTF-8 để xử lý chính xác tiếng Việt
        response.encoding = 'utf-8'
    except requests.exceptions.RequestException as e:
        print(f"[!] Lỗi khi lấy tệp cấu hình: {e}")
        return None

    match = re.search(r'var htmlConfig = ({.*?});', response.text, re.DOTALL)
    if not match:
        print("[!] Không tìm thấy JSON htmlConfig trong script.")
        return None
        
    json_str = match.group(1)
    
    try:
        data = json.loads(json_str)
        return data
    except json.JSONDecodeError:
        print("[!] Không thể phân tích dữ liệu JSON từ cấu hình.")
        return None

def download_single_image(args):
    """Tải một hình ảnh duy nhất và trả về đường dẫn nếu thành công."""
    image_url, output_path = args
    try:
        response = requests.get(image_url, stream=True, timeout=30)
        response.raise_for_status()
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return output_path
    except requests.exceptions.RequestException as e:
        # Lỗi sẽ được xử lý bởi vòng lặp gọi hàm này, trả về None
        return None

def download_images(book_url, config_data, num_threads):
    """
    Tải tất cả hình ảnh của sách một cách đồng thời sử dụng đa luồng.
    """
    if book_url.endswith('/'):
        book_url = book_url[:-1]
    base_image_url = f"{book_url}/files/large/"
    
    try:
        title = config_data.get('meta', {}).get('title', 'downloaded_book')
        safe_title = re.sub(r'[\\/*?:"<>|]', "", title)
        pages = config_data.get('fliphtml5_pages', [])
        if not pages:
            print("[!] Không tìm thấy trang nào trong dữ liệu cấu hình.")
            return None, None
    except AttributeError:
        print("[!] Định dạng dữ liệu cấu hình không hợp lệ.")
        return None, None

    output_dir = os.path.join(os.getcwd(), safe_title)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    print(f"[*] Đang lưu hình ảnh vào: {output_dir}")

    tasks = []
    for i, page in enumerate(pages):
        image_filename_raw = page.get('n', [None])[0]
        if not image_filename_raw:
            print(f"\n[!] Cảnh báo: Không có tên tệp hình ảnh cho trang {i+1}")
            continue

        # Chỉ lấy tên tệp, loại bỏ bất kỳ đường dẫn tương đối nào có thể có
        image_filename = os.path.basename(image_filename_raw)

        timestamp = int(time.time())
        image_url = f"{base_image_url}{image_filename}?{timestamp}&{timestamp}"
        output_path = os.path.join(output_dir, f"page_{i+1:04d}.webp")
        tasks.append((image_url, output_path))

    image_paths = []
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(download_single_image, task) for task in tasks]
        for future in tqdm(as_completed(futures), total=len(tasks), desc="Đang tải hình ảnh"):
            result = future.result()
            if result:
                image_paths.append(result)
    
    image_paths.sort()
    return safe_title, image_paths

def create_pdf_from_paths(output_filename, image_paths):
    """
    Tạo một tệp PDF từ một danh sách các đường dẫn hình ảnh.
    """
    if not image_paths:
        print(f"[!] Không có hình ảnh nào được cung cấp để tạo {output_filename}.")
        return

    print(f"[*] Đang tạo PDF: {output_filename}")
    
    try:
        with Image.open(image_paths[0]) as img:
            width, height = img.size
    except Exception as e:
        print(f"[!] Không thể đọc hình ảnh đầu tiên để xác định kích thước PDF: {e}")
        return

    width_pt = width * 72 / 96
    height_pt = height * 72 / 96
    pdf = FPDF(unit="pt", format=(width_pt, height_pt))

    for image_path in tqdm(image_paths, desc=f"Đang ghép {os.path.basename(output_filename)}"):
        pdf.add_page()
        pdf.image(image_path, 0, 0, w=width_pt, h=height_pt)
    
    try:
        pdf.output(output_filename)
        print(f"[+] Đã tạo thành công {output_filename}")
    except Exception as e:
        print(f"[!] Lỗi khi lưu PDF {output_filename}: {e}")

def cleanup(paths_to_delete):
    """
    Xóa các tệp và thư mục tạm.
    """
    if not paths_to_delete:
        return
        
    print("[*] Đang dọn dẹp các tệp hình ảnh gốc...")
    image_dir = os.path.dirname(paths_to_delete[0])
    for path in paths_to_delete:
        try:
            os.remove(path)
        except OSError as e:
            print(f"[!] Lỗi khi xóa tệp {path}: {e}")
            
    try:
        if not os.listdir(image_dir):
            os.rmdir(image_dir)
    except OSError as e:
         print(f"[!] Không thể xóa thư mục {image_dir}: {e}")

def main():
    """
    Hàm chính để chạy trình tải xuống.
    """
    book_url = input("Nhập URL sách từ FlipHTML5 (ví dụ: https://online.fliphtml5.com/zxpbf/efzq/): ")
    if not book_url:
        print("[!] URL không được để trống.")
        return

    try:
        print("\nChọn loại PDF bạn muốn tạo:")
        print("1. Cả file gốc và file nén")
        print("2. Chỉ file gốc")
        print("3. Chỉ file nén")
        choice = input("Lựa chọn của bạn (1/2/3, mặc định: 1): ") or "1"

        if choice not in ['1', '2', '3']:
            print("[!] Lựa chọn không hợp lệ. Vui lòng chọn 1, 2, hoặc 3.")
            return

        num_threads = int(input("Nhập số luồng tải xuống (mặc định: 10): ") or 10)
        
        quality = 50
        if choice in ['1', '3']:
            quality = int(input("Nhập chất lượng nén cho PDF (1-95, mặc định: 50): ") or 50)

    except ValueError:
        print("[!] Số luồng và chất lượng phải là số nguyên.")
        return

    config_data = get_config_data(book_url)
    if config_data:
        book_title, original_image_paths = download_images(book_url, config_data, num_threads)
        
        if original_image_paths:
            create_original = choice in ['1', '2']
            create_compressed = choice in ['1', '3']

            # 1. Tạo PDF chất lượng gốc nếu được chọn
            if create_original:
                create_pdf_from_paths(f"{book_title}.pdf", original_image_paths)
            
            # 2. Gọi script nén PDF nếu được chọn
            if create_compressed:
                image_dir = os.path.dirname(original_image_paths[0])
                compressor_script_path = os.path.join(os.path.dirname(__file__), 'compressor.py')
                
                if os.path.exists(compressor_script_path):
                    print("\n[*] Đang gọi script nén PDF...")
                    command = [
                        sys.executable,
                        compressor_script_path,
                        image_dir,
                        f"{book_title}_compressed.pdf",
                        "--quality", str(quality),
                        "--threads", str(num_threads)
                    ]
                    try:
                        subprocess.run(command, check=True)
                    except subprocess.CalledProcessError as e:
                        print(f"[!] Script nén đã thất bại với lỗi: {e}")
                    except FileNotFoundError:
                        print(f"[!] Không tìm thấy script nén tại: {compressor_script_path}")
                else:
                    print(f"[!] Cảnh báo: Không tìm thấy 'compressor.py'. Bỏ qua việc tạo PDF nén.")

            # 3. Dọn dẹp các hình ảnh gốc
            cleanup(original_image_paths)

if __name__ == "__main__":
    main()

