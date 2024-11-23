import os
import json
import shutil
from xml.etree import ElementTree as ET
import requests


def recreate_temp_folder(folder_path):

    if os.path.exists(folder_path):
        def remove_readonly(func, path, excinfo):
            os.chmod(path, 0o777)
            func(path)
        shutil.rmtree(folder_path, onerror=remove_readonly)
    os.makedirs(folder_path, exist_ok=True)




def load_package_json(package_json_path):

    with open(package_json_path, "r", encoding="utf-8") as file:
        return json.load(file)


def fetch_package_json_from_repo(package_name):

    url = f"https://registry.npmjs.org/{package_name}/latest"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    print(f"Не удалось загрузить package.json для {package_name}.")
    return None


def build_dependency_graph(package_name):

    def get_dependencies_recursive(package_name, dependencies, graph, visited):
        if package_name in visited:
            return
        visited.add(package_name)
        graph.setdefault(package_name, [])

        for dep_name, _ in dependencies.items():
            if dep_name not in graph[package_name]:
                graph[package_name].append(dep_name)


            sub_package_json = fetch_package_json_from_repo(dep_name)
            if sub_package_json:
                sub_dependencies = sub_package_json.get("dependencies", {})

                get_dependencies_recursive(dep_name, sub_dependencies, graph, visited)


    root_package_json = fetch_package_json_from_repo(package_name)
    if not root_package_json:
        raise ValueError(f"Не удалось загрузить package.json для {package_name}")

    graph = {}
    visited = set()
    root_dependencies = root_package_json.get("dependencies", {})
    get_dependencies_recursive(package_name, root_dependencies, graph, visited)
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
    # Чтение конфигурации
    config_path = "config.xml"
    visualizer_path, package_name, output_file = read_config(config_path)


    try:
        graph = build_dependency_graph(package_name)
        print(f"Граф зависимостей для {package_name}: {graph}")


        mermaid_content = generate_mermaid(graph)
        print(f"Mermaid-код:\n{mermaid_content}")


        save_mermaid_to_file(mermaid_content, output_file)

    except ValueError as e:
        print(f"Ошибка: {e}")
