import subprocess, uuid, os

def evaluate_code(code, language, input_data):
    filename = f"temp_{uuid.uuid4().hex}"
    ext_map = {'python': '.py', 'cpp': '.cpp', 'java': '.java'}
    folder = './temp'
    filepath = f"{folder}/{filename}{ext_map[language]}"

    if not os.path.exists(folder):
        os.makedirs(folder)

    with open(filepath, 'w') as f:
        f.write(code)

    try:
        if language == 'python':
            cmd = ['python', filepath]
        elif language == 'cpp':
            exe = f"{folder}/{filename}_exe"
            subprocess.run(['g++', filepath, '-o', exe], check=True)
            cmd = [exe]
        elif language == 'java':
                filename = 'Main'
                filepath = f'./temp/{filename}.java'
                
                # Write the code to file
                with open(filepath, 'w') as f:
                    f.write(code)
                
                # Compile the Java file
                subprocess.run(['javac', filepath], check=True)

                # Execute the compiled class
                cmd = ['java', '-cp', './temp', filename]



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
