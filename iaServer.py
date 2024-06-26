import os
import subprocess
import sys
from flask import Flask, request, send_file

#from iaProcessData import main as mainPorcessData
#     mainPorcessData(inputPath, outputPath, processID)
def kill_port(port):
    if sys.platform.startswith('linux') or sys.platform == 'darwin':
        command = f"fuser -k {port}/tcp"
    elif sys.platform == 'win32':
        command = f"netstat -ano | findstr :{port}"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.stdout:
            pid = result.stdout.split()[-1]
            command = f"taskkill /PID {pid} /F"
        else:
            return
    os.system(command)

def process(inputPath, outputPath, processID="0"):
    # assuming there are number of processes that can be run
    # all processes are saved in as eparate file
    #mainPorcessData(inputPath, outputPath, processID)
    scriptPath = os.path.join(os.path.expanduser("~"),"myGit","iaProcessData.py")
    try:
        result = subprocess.run(["python3", scriptPath, inputPath, outputPath, processID], capture_output=True, text=True, check=True)
        print("Command output:")
        print(result.stdout)
        print("process is complete!")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")
        print(f"Error output: {e.stderr}")


def main(port, host, tmpDirPath, processID):
    "Start server process"
    app = Flask(__name__)
    
    @app.route('/upload', methods=['POST'])
    def upload_file():
        if 'file' not in request.files:
            return "No file part", 400
        file = request.files['file']
        if file.filename == '':
            return "No selected file", 400

        # Get the process ID from the request
        processID = request.form.get('process_id', "0")  # Default to "0" if not provided

        filepath = os.path.join(tmpDirPath, file.filename)
        file.save(filepath)

        parent_directory, old_fnm = os.path.split(filepath)   
        extensions = old_fnm.split('.')
        fnm = extensions[0]
        extensions = extensions[1:]
        fnm = fnm+"_result"+''.join(['.'+x for x in extensions])
        processed_filepath = os.path.join(tmpDirPath, fnm)
        
        try:
            process(filepath, processed_filepath, processID)
            if os.path.exists(processed_filepath):
                return send_file(processed_filepath, as_attachment=True)
            else:
                return "Processing completed but output file not found", 500
        except Exception as e:
            return f"Error during processing: {str(e)}", 500

    app.run(debug=True, host=host, port=port)

if __name__ == '__main__':
    
    tmpDirPath = os.path.join(os.path.expanduser("~"),"myGit","tmpData")
    port = 5001  # Change the port as needed
    host = '192.168.178.124'  # Change the IP address as needed
    processID = "0"
    main(port,host,tmpDirPath,processID)