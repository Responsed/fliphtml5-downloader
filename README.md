Bản tiếng Việt | English Version

# FlipHTML5 PDF Downloader (English)

A command-line tool written in Python to download digital books from FlipHTML5 and save them as PDF files. This tool supports multi-threaded downloading for increased speed and offers options to create either original quality PDFs or compressed, smaller-sized PDFs.

Features
Download from FlipHTML5: Easily download any book by providing its URL.

Multi-threaded Downloading: Significantly speeds up the image downloading process by using multiple concurrent threads.

Flexible PDF Output Options:

Create a PDF with original image quality.

Create a second, compressed PDF with customizable quality to reduce file size.

Option to create only one of the two types or both.

User-Friendly Interface: The command-line interface intuitively guides the user through each step.

Vietnamese Language Support: Correctly handles and saves filenames containing Vietnamese characters.

Automatic Cleanup: Temporary image files are automatically deleted after the PDF creation process is complete.

Requirements
Python 3.6 or higher

Libraries listed in the requirements.txt file.

Installation Guide
Clone the source code:

git clone [https://github.com/Responsed/fliphtml5-downloader.git](https://github.com/Responsed/fliphtml5-downloader.git)
cd fliphtml5-downloader

(Recommended) Create and activate a virtual environment:

Using venv:

python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

Or using conda:

conda create --name flipdownloader python=3.8
conda activate flipdownloader

Install the required libraries:

pip install -r requirements.txt

How to Use
Run the main script from your terminal or command prompt:

python downloader.py

Follow the on-screen prompts:

Enter the URL of the FlipHTML5 book you want to download.

Select the type of PDF you want to create (original only, compressed only, or both).

Enter the number of threads for concurrent downloading.

If you choose to create a compressed file, enter the compression quality (from 1 to 95).

The program will start the download process and create the PDF(s) in the same directory as the script.

Project Structure
downloader.py: The main script that handles the user interface, fetches book information, downloads images, and creates the original quality PDF.

compressor.py: A helper script responsible for compressing images and creating the compressed PDF file.

requirements.txt: Contains the list of necessary Python libraries for the project.


# FlipHTML5 PDF Downloader (Tiếng Việt)

Một công cụ dòng lệnh (command-line) được viết bằng Python để tải xuống các cuốn sách kỹ thuật số từ FlipHTML5 và lưu chúng dưới dạng tệp PDF. Công cụ này hỗ trợ tải đa luồng để tăng tốc độ và cung cấp các tùy chọn để tạo PDF chất lượng gốc hoặc PDF đã được nén dung lượng.

Tính năng nổi bật
Tải sách từ FlipHTML5: Dễ dàng tải xuống bất kỳ cuốn sách nào chỉ bằng cách cung cấp URL.

Tải đa luồng: Tăng tốc đáng kể quá trình tải hình ảnh bằng cách sử dụng nhiều luồng đồng thời.

Tùy chọn đầu ra PDF linh hoạt:

Tạo tệp PDF với chất lượng hình ảnh gốc.

Tạo một tệp PDF thứ hai đã được nén với chất lượng tùy chỉnh để giảm dung lượng.

Tùy chọn chỉ tạo một trong hai loại tệp hoặc cả hai.

Giao diện thân thiện: Giao diện dòng lệnh hướng dẫn người dùng qua từng bước một cách trực quan.

Hỗ trợ Tiếng Việt: Xử lý và lưu tên tệp có chứa ký tự tiếng Việt một cách chính xác.

Tự động dọn dẹp: Các tệp hình ảnh tạm thời sẽ được tự động xóa sau khi quá trình tạo PDF hoàn tất.

Yêu cầu
Python 3.6 trở lên

Các thư viện được liệt kê trong tệp requirements.txt.

Hướng dẫn Cài đặt
Tải mã nguồn về máy:

git clone [https://github.com/Responsed/fliphtml5-downloader.git](https://github.com/Responsed/fliphtml5-downloader.git)
cd fliphtml5-downloader

(Khuyến khích) Tạo và kích hoạt môi trường ảo:

Sử dụng venv:

python -m venv venv
# Trên Windows
venv\Scripts\activate
# Trên macOS/Linux
source venv/bin/activate

Hoặc sử dụng conda:

conda create --name flipdownloader python=3.8
conda activate flipdownloader

Cài đặt các thư viện cần thiết:

pip install -r requirements.txt

Cách sử dụng
Chạy script chính từ terminal hoặc command prompt:

python downloader.py

Làm theo các hướng dẫn trên màn hình:

Nhập URL của sách FlipHTML5 bạn muốn tải.

Chọn loại PDF bạn muốn tạo (chỉ file gốc, chỉ file nén, hoặc cả hai).

Nhập số luồng để tải xuống đồng thời.

Nếu bạn chọn tạo file nén, nhập chất lượng nén (từ 1 đến 95).

Chương trình sẽ bắt đầu quá trình tải xuống và tạo (các) tệp PDF trong cùng thư mục chứa script.

Cấu trúc dự án
downloader.py: Script chính, xử lý giao diện người dùng, lấy thông tin sách, tải hình ảnh và tạo PDF chất lượng gốc.

compressor.py: Script phụ, chịu trách nhiệm nén hình ảnh và tạo tệp PDF đã nén.

requirements.txt: Chứa danh sách các thư viện Python cần thiết cho dự án.
