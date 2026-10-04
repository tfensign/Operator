const { contextBridge, ipcRenderer } = require('electron');

// Expose safe APIs to renderer process
contextBridge.exposeInMainWorld('api', {
  call: (method, endpoint, data) => {
    return ipcRenderer.invoke('api-call', method, endpoint, data);
  }
});
