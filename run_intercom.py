import os
import sys
import subprocess

# Añadir la raíz del proyecto al PYTHONPATH
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

if __name__ == "__main__":
    # Ejecuta streamlit apuntando a la ruta relativa correcta
    print(f"Iniciando Intercomunicador desde: {project_root}")
    
    # We need to pass the PYTHONPATH to the subprocess as well
    env = os.environ.copy()
    env["PYTHONPATH"] = project_root + os.pathsep + env.get("PYTHONPATH", "")
    
    app_path = os.path.join("src", "ui", "app.py")
    
    # Run streamlit using the current python executable to ensure module availability
    # Run from project_root so that relative paths work correctly
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", app_path], env=env, cwd=project_root, check=True)
    except KeyboardInterrupt:
        print("\nIntercomunicador detenido.")
