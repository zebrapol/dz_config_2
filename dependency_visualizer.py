import os
import subprocess
import json
from xml.etree import ElementTree as ET



def install_package_from_link(link, working_dir):
    if os.path.exists(working_dir):
        subprocess.run(["rmdir", "/s", "/q", working_dir], check=True, shell=True)
    subprocess.run(["git", "clone", link, working_dir], check=True)
    try:
        subprocess.run(["powershell", "-Command", "npm install"], cwd=working_dir, check=True)
    except FileNotFoundError:
        raise EnvironmentError("npm не установлен или не добавлен в PATH.")
    subprocess.run(["D:/pablo/npm.cmd", "install"], cwd=working_dir, check=True)
    print(f"Пакет из {link} установлен в {working_dir}")



def load_package_json(package_json_path):
    with open(package_json_path, "r", encoding="utf-8") as file:
        return json.load(file)



def fetch_dependencies(package_json):
    return package_json.get("dependencies", {})


def build_dependency_graph(package_name, lock_file_path):

    if not os.path.exists(lock_file_path):
        raise FileNotFoundError(f"Не найден файл {lock_file_path}. Убедитесь, что зависимости установлены.")
    with open(lock_file_path, "r", encoding="utf-8") as file:
        lock_data = json.load(file)


    packages = lock_data.get("packages", {})
    if not packages:
        raise ValueError("Блок 'packages' отсутствует в package-lock.json. Проверьте структуру файла.")


    root_package = packages.get(f"node_modules/{package_name}")
    if not root_package:
        raise ValueError(f"Пакет {package_name} не найден в блоке 'packages' в package-lock.json.")


    def get_dependencies(dep_name, package_info):
        dep_graph = {dep_name: []}
        if "dependencies" in package_info:
            for sub_dep, version in package_info["dependencies"].items():
                dep_graph[dep_name].append(sub_dep)
                # Рекурсивно обходим вложенные зависимости
                sub_dep_info = packages.get(f"node_modules/{sub_dep}", {})
                dep_graph.update(get_dependencies(sub_dep, sub_dep_info))
        return dep_graph


    graph = get_dependencies(package_name, root_package)
    return graph



def generate_mermaid(graph):
    lines = ["graph TD"]
    for parent, children in graph.items():
        for child in children:
            lines.append(f"    {parent} --> {child}")
    return "\n".join(lines)



def save_mermaid_to_file(content, output_file):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)  # Создаем папки, если их нет
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(content)
    print(f"Mermaid-код сохранен в файл {output_file}")



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
    working_dir = "D:/dz_config_2/temp_package"

    #install_package_from_link(package_link, working_dir)


    package_json_path = os.path.join(working_dir, "package.json")
    lock_file_path = os.path.join(working_dir, "package-lock.json")


    package_json = load_package_json(package_json_path)
    dependencies = fetch_dependencies(package_json)

    print(f"Зависимости пакета {package_name}: {dependencies}")


    graph = build_dependency_graph(package_name, lock_file_path)
    print(f"Граф зависимостей для {package_name}: {graph}")


    mermaid_content = generate_mermaid(graph)
    print(f"Mermaid-код:\n{mermaid_content}")


    save_mermaid_to_file(mermaid_content, output_file)
