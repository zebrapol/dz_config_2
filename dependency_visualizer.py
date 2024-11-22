import os
import shutil
import json
from xml.etree import ElementTree as ET


def recreate_temp_folder(folder_path):
    if os.path.exists(folder_path):
        def remove_readonly(func, path, excinfo):
            os.chmod(path, 0o777)
            func(path)
        shutil.rmtree(folder_path, onerror=remove_readonly)
    os.makedirs(folder_path, exist_ok=True)


def fetch_repository(link, working_dir):
    recreate_temp_folder(working_dir)
    os.system(f"git clone {link} {working_dir}")
    print(f"Репозиторий {link} клонирован в {working_dir}")


def load_package_json(package_json_path):
    with open(package_json_path, "r", encoding="utf-8") as file:
        return json.load(file)


def build_dependency_graph(package_json):
    """Строит граф зависимостей, включая транзитивные связи."""
    def get_dependencies_recursive(package_name, dependencies, graph, visited):
        if package_name in visited:
            return
        visited.add(package_name)
        graph.setdefault(package_name, [])

        for dep_name, _ in dependencies.items():
            if dep_name not in graph[package_name]:
                graph[package_name].append(dep_name)

            sub_package_json_path = os.path.join(
                working_dir, "node_modules", dep_name, "package.json"
            )

            if os.path.exists(sub_package_json_path):
                sub_package_json = load_package_json(sub_package_json_path)
                sub_dependencies = sub_package_json.get("dependencies", {})
                get_dependencies_recursive(dep_name, sub_dependencies, graph, visited)

    graph = {}
    visited = set()

    root_dependencies = package_json.get("dependencies", {})
    get_dependencies_recursive("express", root_dependencies, graph, visited)

    return graph


def generate_mermaid(graph):
    lines = ["graph TD"]
    for parent, children in graph.items():
        for child in children:
            lines.append(f"    {parent} --> {child}")
    return "\n".join(lines)


def save_mermaid_to_file(content, output_file):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(content)
    print(f"Mermaid-код сохранён в файл {output_file}")


def read_config(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    visualizer_path = root.find("visualizerPath").text
    package_name = root.find("packageName").text
    output_file = root.find("outputFile").text

    return visualizer_path, package_name, output_file


if __name__ == "__main__":
    config_path = "config.xml"
    visualizer_path, package_name, output_file = read_config(config_path)

    package_link = "https://github.com/expressjs/express.git"
    working_dir = "D:/dz_config_2/temp_package_express"

    fetch_repository(package_link, working_dir)

    package_json_path = os.path.join(working_dir, "package.json")
    package_json = load_package_json(package_json_path)

    graph = build_dependency_graph(package_json)
    print(f"Граф зависимостей для {package_name}: {graph}")

    mermaid_content = generate_mermaid(graph)
    print(f"Mermaid-код:\n{mermaid_content}")
    save_mermaid_to_file(mermaid_content, output_file)
