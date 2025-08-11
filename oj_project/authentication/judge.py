import subprocess, uuid, os

def evaluate_code(code, language, input_data):
    folder = './temp'
    if not os.path.exists(folder):
        os.makedirs(folder)

    filename = f"temp_{uuid.uuid4().hex}"
    ext_map = {'python': '.py', 'cpp': '.cpp', 'java': '.java'}
    filepath = os.path.join(folder, filename + ext_map[language])

    try:
        # Write code to file
        with open(filepath, 'w') as f:
            f.write(code)

        if language == 'python':
            cmd = ['python3', filepath]

        elif language == 'cpp':
            exe_path = os.path.join(folder, filename + '_exe')
            subprocess.run(['g++', filepath, '-o', exe_path], check=True)
            cmd = [exe_path]

        elif language == 'java':
            java_filename = 'Main.java'
            java_classname = 'Main'
            java_filepath = os.path.join(folder, java_filename)

            # Overwrite file with correct name
            with open(java_filepath, 'w') as f:
                f.write(code)

            subprocess.run(['javac', java_filepath], check=True)
            cmd = ['java', '-cp', folder, java_classname]

        result = subprocess.run(
            cmd,
            input=input_data.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=2
        )
        return result.stdout.decode(), result.stderr.decode()

    except subprocess.CalledProcessError as ce:
        return '', f'Compilation Error: {ce}'
    except subprocess.TimeoutExpired:
        return '', 'Time Limit Exceeded'
    except Exception as e:
        return '', str(e)
    finally:
        try: os.remove(filepath)
        except: pass
        if language == 'cpp':
            try: os.remove(exe_path)
            except: pass
        if language == 'java':
            try:
                os.remove(os.path.join(folder, 'Main.class'))
                os.remove(os.path.join(folder, 'Main.java'))
            except: pass
import subprocess, uuid, os

def evaluate_code(code, language, input_data):
    folder = './temp'
    if not os.path.exists(folder):
        os.makedirs(folder)

    filename = f"temp_{uuid.uuid4().hex}"
    ext_map = {'python': '.py', 'cpp': '.cpp', 'java': '.java'}
    filepath = os.path.join(folder, filename + ext_map[language])

    try:
        # Write code to file
        with open(filepath, 'w') as f:
            f.write(code)

        if language == 'python':
            cmd = ['python3', filepath]

        elif language == 'cpp':
            exe_path = os.path.join(folder, filename + '_exe')
            subprocess.run(['g++', filepath, '-o', exe_path], check=True)
            cmd = [exe_path]

        elif language == 'java':
            java_filename = 'Main.java'
            java_classname = 'Main'
            java_filepath = os.path.join(folder, java_filename)

            # Overwrite file with correct name
            with open(java_filepath, 'w') as f:
                f.write(code)

            subprocess.run(['javac', java_filepath], check=True)
            cmd = ['java', '-cp', folder, java_classname]

        result = subprocess.run(
            cmd,
            input=input_data.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=2
        )
        return result.stdout.decode(), result.stderr.decode()

    except subprocess.CalledProcessError as ce:
        return '', f'Compilation Error: {ce}'
    except subprocess.TimeoutExpired:
        return '', 'Time Limit Exceeded'
    except Exception as e:
        return '', str(e)
    finally:
        try: os.remove(filepath)
        except: pass
        if language == 'cpp':
            try: os.remove(exe_path)
            except: pass
        if language == 'java':
            try:
                os.remove(os.path.join(folder, 'Main.class'))
                os.remove(os.path.join(folder, 'Main.java'))
            except: pass
