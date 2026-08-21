import platform
import os


def get_system_info():
    info = {
        "Operating System": platform.system(),
        "OS Version": platform.version(),
        "Machine": platform.machine(),
        "Processor": platform.processor(),
        "CPU Cores": os.cpu_count()
    }

    return info


if __name__ == "__main__":

    print("MANU System Information")
    print("========================")

    system_info = get_system_info()

    for key, value in system_info.items():
        print(f"{key}: {value}")