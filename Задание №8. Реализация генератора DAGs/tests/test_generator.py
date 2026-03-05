import pytest
from pathlib import Path
from generator import AnalystAutoFlow


def test_extract_metadata_success(tmp_path):
    """Тест: проверяем, что регулярные выражения правильно читают метаданные."""
    # 1. Arrange: Создаем временный файл-обманку
    test_file = tmp_path / "test_script.py"
    test_file.write_text(
        "# dag_id: test_dag_123\n"
        "# schedule: @hourly\n"
        "# owner: test_team\n"
        "print('hello world')",
        encoding="utf-8"
    )

    # 2. Act: Запускаем наш метод
    # Передаем tmp_path как фейковые директории (они нам тут не важны)
    flow = AnalystAutoFlow(tmp_path, tmp_path, tmp_path / "test.log")
    metadata = flow.extract_metadata(test_file)

    # 3. Assert: Проверяем результат
    assert metadata['dag_id'] == 'test_dag_123'
    assert metadata['schedule'] == '@hourly'
    assert metadata['owner'] == 'test_team'


def test_extract_metadata_empty(tmp_path):
    """Тест: проверяем, как система ведет себя, если аналитик забыл написать комментарии."""
    test_file = tmp_path / "empty_script.sql"
    test_file.write_text("SELECT * FROM table;", encoding="utf-8")

    flow = AnalystAutoFlow(tmp_path, tmp_path, tmp_path / "test.log")
    metadata = flow.extract_metadata(test_file)

    # Должен вернуться пустой словарь, так как метаданных нет
    assert metadata == {}


def test_full_generation_pipeline(tmp_path, monkeypatch):
    """Тест: проверяем полный цикл создания DAGа."""
    # Создаем фейковые исходную и целевую папки
    source = tmp_path / "projects"
    target = tmp_path / "dags"

    # Внутри source создаем папку проекта и кладем туда файл
    project_folder = source / "my_test_project"
    project_folder.mkdir(parents=True)
    (project_folder / "01_test.py").write_text("# dag_id: my_dag\nprint('ok')")

    # Инициализируем генератор
    flow = AnalystAutoFlow(source, target, tmp_path / "test.log")

    # Хитрость: чтобы Jinja нашла шаблон, укажем ей искать в реальной корневой папке проекта
    import jinja2
    flow.env = jinja2.Environment(loader=jinja2.FileSystemLoader('.'))

    # Запускаем генерацию
    flow.generate()

    # Проверяем, что в целевой папке появился нужный файл
    expected_file = target / "gen_my_dag.py"
    assert expected_file.exists(), "Файл DAGа не был создан!"

    # Проверяем, что внутрь подставились правильные значения
    content = expected_file.read_text(encoding="utf-8")
    assert "dag_id='my_dag'" in content
    assert "task_id='task_01_test'" in content
