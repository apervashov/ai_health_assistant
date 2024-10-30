import fitz  # PyMuPDF
import os

def pdf_to_txt(pdf_path, output_dir):
    # Открываем PDF и извлекаем текст
    with fitz.open(pdf_path) as doc:
        text = ""
        for page in doc:
            text += page.get_text()

    # Формируем имя txt файла
    txt_filename = os.path.basename(pdf_path).replace(".pdf", ".txt")
    txt_path = os.path.join(output_dir, txt_filename)
    
    # Сохраняем текст в txt формате
    with open(txt_path, 'w', encoding='utf-8') as txt_file:
        txt_file.write(text)
    print(f"Processed {pdf_path} -> {txt_path}")

def process_all_pdfs(input_dir, output_dir):
    # Проверка и создание директории для txt файлов, если нужно
    os.makedirs(output_dir, exist_ok=True)
    
    # Проходим по каждому файлу в папке
    for filename in os.listdir(input_dir):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(input_dir, filename)
            pdf_to_txt(pdf_path, output_dir)

# Задайте директории для входных PDF и выходных txt файлов
input_directory = "dataset"
output_directory = "datasetTXT"

# Запуск обработки
process_all_pdfs(input_directory, output_directory)
