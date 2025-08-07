import argparse
import datetime
import logging
import os
import re
import zipfile

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

def extract_zip_files(zip_file, extract_to='.'):
    """Извлекает все .txt файлы из архива в указанную папку"""
    with zipfile.ZipFile(zip_file, 'r') as archive:
        for file in archive.namelist():
            if file.endswith('.txt'):
                archive.extract(file, path=extract_to)
                logging.info(f"Извлечён: {file}")

def process_txt_files(folder, new_folder, dry_run=False, cleanup=False):
    """Обрабатывает все .txt файлы в папке и сохраняет результат"""
    if not os.path.exists(new_folder):
        os.makedirs(new_folder)
        logging.info(f"Создана выходная папка: {new_folder}")

    txt_files = [f for f in os.listdir(folder) if f.endswith('.txt')]
    if not txt_files:
        logging.warning("В папке нет .txt файлов для обработки.")
        return

    for file in txt_files:
        input_path = os.path.join(folder, file)
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Преобразования
        content = re.sub(r'Poker Hand #HD', 'PokerStars Hand #20', content, flags=re.MULTILINE)
        content = re.sub(r'Poker Hand #RC', 'PokerStars Hand #30', content, flags=re.MULTILINE)
        content = re.sub(r' won ', ' collected ', content, flags=re.MULTILINE)
        content = re.sub(r' and collected ', ' and won ', content, flags=re.MULTILINE)
        content = re.sub(r'\n\n', '\n', content, flags=re.MULTILINE)
        content = re.sub(r'Dealt to (?!Hero\b)[^ ]+ \n', '', content, flags=re.MULTILINE)

        if dry_run:
            logging.info(f"[Dry run] Предпросмотр файла {file}:\n{content[:500]}\n...")
        else:
            output_path = os.path.join(new_folder, file)
            with open(output_path, 'w', encoding='utf-8') as f_new:
                f_new.write(content)
            logging.info(f"Сохранён: {output_path}")

        if cleanup:
            os.remove(input_path)
            logging.info(f"Удалён исходный файл: {input_path}")

def main():
    parser = argparse.ArgumentParser(description='Конвертация hand history файлов из Pokerok в формат PokerStars для Hand2Note')
    parser.add_argument('-if', '--input_folder', default='./', help='Путь к входной папке с ZIP файлами')
    parser.add_argument('-of', '--output_folder', default=None, help='Путь к выходной папке. Если не указана — используется текущая дата (YY.MM.DD)')
    parser.add_argument('--cleanup', action='store_true', help='Удалять исходные .txt файлы после обработки')
    parser.add_argument('--dry-run', action='store_true', help='Показать, что будет сделано, но без сохранения результатов')

    args = parser.parse_args()
    input_folder = args.input_folder
    output_folder = args.output_folder

    if not output_folder:
        today = datetime.datetime.today()
        output_folder = os.path.join(input_folder, today.strftime('%y.%m.%d'))

    zip_files = [f for f in os.listdir(input_folder) if f.endswith('.zip')]
    if not zip_files:
        logging.warning("ZIP-файлы не найдены в указанной папке.")
    else:
        for file in zip_files:
            extract_zip_files(os.path.join(input_folder, file), extract_to=input_folder)

    process_txt_files(input_folder, output_folder, dry_run=args.dry_run, cleanup=args.cleanup)

if __name__ == '__main__':
    main()