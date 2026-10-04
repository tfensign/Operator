const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let isDev = false;
try {
  isDev = require('electron-is-dev');
} catch (e) {
  isDev = process.env.NODE_ENV === 'development';
}

let mainWindow;
let pythonProcess;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true
    }
  });

  const startUrl = isDev
    ? 'http://localhost:3000'
    : `file://${path.join(__dirname, '../build/index.html')}`;

  mainWindow.loadURL(startUrl);

  if (isDev) {
    mainWindow.webContents.openDevTools();
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

function startPythonBackend() {
  const pythonScript = path.join(__dirname, '../backend/app.py');

  // Determine Python executable
  const pythonExe = process.platform === 'win32' ? 'python' : 'python3';

  pythonProcess = spawn(pythonExe, ['-m', 'uvicorn', 'app:app', '--port', '3001', '--host', '127.0.0.1'], {
    cwd: path.join(__dirname, '../backend'),
    stdio: 'pipe'
  });

  pythonProcess.stdout.on('data', (data) => {
    console.log(`Python stdout: ${data}`);
  });

  pythonProcess.stderr.on('data', (data) => {
    console.log(`Python stderr: ${data}`);
  });

  pythonProcess.on('error', (error) => {
    console.error(`Python process error: ${error}`);
  });

  pythonProcess.on('close', (code) => {
    console.log(`Python process exited with code ${code}`);
  });
}

app.on('ready', () => {
  startPythonBackend();

  // Wait a bit for Python to start, then create window
  setTimeout(() => {
    createWindow();
  }, 2000);
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }

  // Kill Python process
  if (pythonProcess) {
    pythonProcess.kill();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});

// IPC handlers for backend communication
ipcMain.handle('api-call', async (event, method, endpoint, data) => {
  const axios = require('axios');
  try {
    const response = await axios({
      method,
      url: `http://localhost:3001${endpoint}`,
      data
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || error.message;
  }
});
