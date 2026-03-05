import re
import ast
import logging
from pathlib import Path
from datetime import datetime
from jinja2 import Environment, FileSystemLoader


class AnalystAutoFlow:
    def __init__(self, source_dir: str, target_dir: str, log_file: str):
        # 1. Определяем пути
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)

        # 2. Проверяем источник
        if not self.source_dir.exists():
            raise FileNotFoundError(f"Папка с исходниками не найдена: {self.source_dir}")

        # 3. Создаем папку для DAG-ов (аналог mkdir -p)
        self.target_dir.mkdir(parents=True, exist_ok=True)

        # 4. Настраиваем логирование
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        logging.info("AnalystAutoFlow инициализирован успешно.")

        # Вычисляем абсолютный путь к папке, где лежит сам скрипт generator.py
        current_dir = Path(__file__).parent

        # Говорим Jinja2 искать шаблоны именно в этой папке
        self.env = Environment(loader=FileSystemLoader(current_dir))

    def extract_metadata(self, file_path: Path) -> dict:
        content = file_path.read_text(encoding='utf-8')
        metadata = {}

        patterns = {
            'dag_id': r'dag_id:\s*(.+)',
            'schedule': r'schedule:\s*(.+)',
            'owner': r'owner:\s*(.+)'
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, content)
            if match:
                metadata[key] = match.group(1).strip()

        return metadata

    def generate(self):
        all_files = [
            f for f in self.source_dir.rglob('*')
            if f.suffix in ['.py', '.sql']
        ]

        dags_folders = {}
        for file_path in all_files:
            folder_name = file_path.parent.name
            if folder_name not in dags_folders:
                dags_folders[folder_name] = []
            dags_folders[folder_name].append(file_path)

        for folder_name, files in dags_folders.items():
            self._process_dag_folder(folder_name, files)

    def _process_dag_folder(self, folder_name, files):
        files.sort(key=lambda x: x.name)
        main_metadata = self.extract_metadata(files[0])
        dag_id = main_metadata.get('dag_id', folder_name)

        tasks = []
        for f in files:
            task_info = {
                'id': f"task_{f.stem}",
                'type': 'python' if f.suffix == '.py' else 'sql',
                'file_name': f.name
            }
            tasks.append(task_info)

        self._render_and_save(dag_id, main_metadata, tasks)

    def _render_and_save(self, dag_id, metadata, tasks):
        task_chain = " >> ".join([t['id'] for t in tasks])
        now = datetime.now()

        context = {
            'target_id': dag_id,
            'target_schedule': metadata.get('schedule', '@daily'),
            'target_owner': metadata.get('owner', 'admin'),
            'tasks': tasks,
            'task_chain': task_chain,
            'start_date': f"datetime({now.year}, {now.month}, {now.day})"
        }

        template = self.env.get_template('dag_template.j2')
        generated_code = template.render(context)

        try:
            ast.parse(generated_code)
        except SyntaxError as e:
            logging.error(f"Ошибка синтаксиса в DAG {dag_id}: {e}")
            print(f"❌ Ошибка в {dag_id}, проверьте лог.")
            return
        else:
            self._write_to_file(dag_id, generated_code)

    def _write_to_file(self, dag_id: str, code: str):
        file_path = self.target_dir / f"gen_{dag_id}.py"
        file_path.write_text(code, encoding='utf-8')
        logging.info(f"DAG {dag_id} успешно создан: {file_path}")
        print(f"✅ DAG {dag_id} готов!")


# === Блок запуска ===
if __name__ == "__main__":
    # Указываем здесь свои папки
    SOURCE_DIR = 'projects'
    TARGET_DIR = 'airflow/dags'
    LOG_FILE = 'generation.log'

    # Чтобы скрипт не упал при первом запуске, если папки projects еще нет. Создаем её.
    Path(SOURCE_DIR).mkdir(exist_ok=True)

    flow = AnalystAutoFlow(SOURCE_DIR, TARGET_DIR, LOG_FILE)
    flow.generate()
