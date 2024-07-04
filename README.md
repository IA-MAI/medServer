# medServer
A simple python tool to process data remotly and get the result back 

![](https://raw.githubusercontent.com/IA-MAI/medServer/main/res/MedServer.png)

### Installation

You need Python and Flask: 

                pip install flask


#### In the client machine:                 
 
 modify the paths, the host, and the port then run:
 python3 iaClient.py


#### In the server machine:                 

modify the paths, the host, and the port then run:
 python3 iaServer.py



### Adding a new functionality: 

Simply modify the file iaProcessData.py by adding a new function, adding a new elif with the new processID then call the new function. 

### TODOs:

- Support multiple users in the server
- Add more processes
- Add progressbar
- Server should send the file name as well
- Fix the webapp to save the file correctly
- Test using real domain




