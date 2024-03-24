import subprocess
import sys

gui_controller_path = "gui/gui_login_view.py"
cli_controller_path = "cli/cli_controller.py"


def exec_file(launch_type):
    python_exe_path = sys.executable

    if launch_type == "gui":
        script = gui_controller_path
    elif launch_type == "cli":
        script = cli_controller_path
    else:
        print("Unknown type: " + launch_type)
        sys.exit(1)

    komenda = [python_exe_path, script]

    print(f"Invoked command: {komenda}")
    subprocess.run(komenda)


if __name__ == "__main__":
    exec_file(input("Which type you want to launch? (cli/gui): "))
