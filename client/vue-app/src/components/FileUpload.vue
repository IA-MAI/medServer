<template>
    <div class="file-upload">
      <h1>File Upload and Processing</h1>
      <form @submit.prevent="uploadFile">
        <div>
          <label for="file">Choose file:</label>
          <input type="file" id="file" @change="handleFileChange" required />
        </div>
        <div>
          <label for="savePath">Save Path:</label>
          <input type="text" id="savePath" v-model="savePath" required />
        </div>
        <div>
          <button type="submit">Upload and Process</button>
        </div>
      </form>
      <div v-if="message" :class="{'error': isError}">
        {{ message }}
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  import fileSaver from 'file-saver';
  
  export default {
    data() {
      return {
        file: null,
        savePath: this.getDefaultSavePath(),
        message: '',
        isError: false,
      };
    },
    methods: {
      getDefaultSavePath() {
        const userAgent = window.navigator.userAgent;
        if (userAgent.includes('Windows')) {
          const usernameMatch = userAgent.match(/\\User\\([^\\]*)/);
          const username = usernameMatch ? usernameMatch[1] : 'username';
          return `C:\\Users\\${username}\\Downloads`;
        // // } else if (userAgent.includes('Mac')) {
        // //   const usernameMatch = userAgent.match(/\/Users\/([^\/]*)/);
        // //   const username = usernameMatch ? usernameMatch[1] : 'username';
        //   return `/Users/${username}/Downloads`;
        } else if (userAgent.includes('Linux')) {
        //   const usernameMatch = userAgent.match(/\/home\/([^\/]*)/);
        //   const username = usernameMatch ? usernameMatch[1] : 'username';
          return `/home/$USER/Downloads`;
        }
        return '';  // Default empty path for unsupported OS detection
      },
      handleFileChange(event) {
        this.file = event.target.files[0];
      },
      async uploadFile() {
        if (!this.file || !this.savePath) {
          this.message = 'File and save path are required!';
          this.isError = true;
          return;
        }
  
        const formData = new FormData();
        formData.append('file', this.file);
        formData.append('savePath', this.savePath);
  
        try {
          const response = await axios.post('http://192.168.178.124:5001/upload', formData, {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
            responseType: 'blob',
          });
  
          // Console output to check response
          console.log('Response:', response);
  
          if (response.data) {
            const blob = new Blob([response.data]);
            const contentDisposition = response.headers['content-disposition'];
            let filename = 'result_file';
            if (contentDisposition && contentDisposition.indexOf('filename=') !== -1) {
              const matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(contentDisposition);
              if (matches != null && matches[1]) { 
                filename = matches[1].replace(/['"]/g, '').trim();
              }
            }
  
            console.log(`Saving file as: ${filename}`);
            fileSaver.saveAs(blob, filename);
  
            this.message = `File processed and downloaded successfully as ${filename}!`;
            this.isError = false;
          } else {
            this.message = 'No data received from the server';
            this.isError = true;
          }
        } catch (error) {
          console.log('Error:', error);
          this.message = `Error: ${error.response ? error.response.data : error.message}`;
          this.isError = true;
        }
      },
    },
  };
  </script>
  
  <style>
  .file-upload {
    max-width: 400px;
    margin: 0 auto;
  }
  .error {
    color: red;
  }
  </style>
  