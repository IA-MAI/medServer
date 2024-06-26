import os
import requests
from pathlib import Path

def send_file_to_server(file_path, serverUrl, processID="0"):
    print(f'Sending file to server: {file_path}')
    print("please wait ....")
    files = {'file': open(file_path, 'rb')}
    data = {'process_id': processID}  # Add this line to include the process ID

    try:
        response = requests.post(serverUrl, files=files, data=data)  # Include data in the request
        response.raise_for_status()
        
        parent_directory, old_fnm = os.path.split(file_path)   
        extensions = old_fnm.split('.')
        fnm = extensions[0]
        extensions = extensions[1:]
        fnm = fnm+"_result"+''.join(['.'+x for x in extensions])
        result_file_path = os.path.join(parent_directory, fnm)

        with open(result_file_path, 'wb') as f:
            f.write(response.content)
        
        print(f'Result file saved to {result_file_path}')

    except requests.exceptions.RequestException as e:
        print(f'An error occurred: {e}')

if __name__ == "__main__":
    serverHTTP = "http"
    serverIP   = "192.168.178.124"
    serverPort = "5001"    
    serverUrl  = serverHTTP + "://"+ serverIP + ":" + serverPort + "/upload"
    file_path = os.path.join(os.path.expanduser('~'),"Downloads","ISLES24","isles24_batch_1","raw_data","sub-stroke0003","ses-02","sub-stroke0003_ses-02_dwi.nii.gz")
    processID = "0"
    send_file_to_server(file_path, serverUrl, processID)  # Pass processID here