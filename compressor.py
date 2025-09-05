# -*- coding: utf-8 -*-
import os
import argparse
from PIL import Image
from fpdf import FPDF
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

def create_pdf_from_paths(output_filename, image_paths):
    """
    Tạo một tệp PDF từ một danh sách các đường dẫn hình ảnh.
    """
    if not image_paths:
        print(f"[!] Không có hình ảnh nào được cung cấp để tạo {output_filename}.")
        return

    print(f"[*] Đang tạo PDF nén: {output_filename}")
    
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

def compress_single_image(args):
    """Nén một hình ảnh duy nhất."""
    image_path, temp_compressed_dir, index, quality = args
    try:
        img = Image.open(image_path).convert("RGB")
        compressed_path = os.path.join(temp_compressed_dir, f"page_{index:04d}.jpg")
        img.save(compressed_path, "JPEG", quality=quality, optimize=True)
        return compressed_path
    except Exception as e:
        # Lỗi sẽ được xử lý bởi vòng lặp gọi hàm này, trả về None
        return None

def compress_images(image_paths, quality, num_threads):
    """
    Nén một danh sách hình ảnh đồng thời và trả về đường dẫn đến các hình ảnh đã nén.
    """
    if not image_paths:
        return []

    temp_compressed_dir = os.path.join(os.path.dirname(image_paths[0]), "compressed")
    if not os.path.exists(temp_compressed_dir):
        os.makedirs(temp_compressed_dir)
    
    tasks = [(path, temp_compressed_dir, i + 1, quality) for i, path in enumerate(image_paths)]
    
    compressed_paths = []
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(compress_single_image, task) for task in tasks]
        for future in tqdm(as_completed(futures), total=len(tasks), desc="Đang nén hình ảnh"):
            result = future.result()
            if result:
                compressed_paths.append(result)

    compressed_paths.sort()
    return compressed_paths

def cleanup(paths_to_delete):
    """
    Xóa các tệp và thư mục tạm.
    """
    dirs_to_delete = set()
    if not paths_to_delete:
        return
        
    print("[*] Đang dọn dẹp các tệp nén tạm thời...")
    for path in paths_to_delete:
        try:
            dirs_to_delete.add(os.path.dirname(path))
            os.remove(path)
        except OSError as e:
            print(f"[!] Lỗi khi xóa tệp {path}: {e}")
            
    for directory in sorted(list(dirs_to_delete), reverse=True):
        try:
            if not os.listdir(directory):
                os.rmdir(directory)
        except OSError as e:
             print(f"[!] Không thể xóa thư mục {directory}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Nén hình ảnh và tạo file PDF.")
    parser.add_argument("input_dir", help="Thư mục chứa hình ảnh gốc.")
    parser.add_argument("output_filename", help="Tên file PDF nén đầu ra.")
    parser.add_argument("--quality", type=int, default=50, help="Chất lượng nén (1-95, mặc định: 50).")
    parser.add_argument("--threads", type=int, default=10, help="Số luồng để sử dụng (mặc định: 10).")
    args = parser.parse_args()

    if not os.path.isdir(args.input_dir):
        print(f"[!] Thư mục đầu vào không tồn tại: {args.input_dir}")
        return

    original_image_paths = sorted([os.path.join(args.input_dir, f) for f in os.listdir(args.input_dir) if f.lower().endswith(('.webp', '.jpg', '.jpeg', '.png'))])

    if not original_image_paths:
        print(f"[!] Không tìm thấy hình ảnh nào trong thư mục: {args.input_dir}")
        return

    compressed_image_paths = compress_images(original_image_paths, args.quality, args.threads)

    if compressed_image_paths:
        create_pdf_from_paths(args.output_filename, compressed_image_paths)
        cleanup(compressed_image_paths)

if __name__ == "__main__":
    main()
