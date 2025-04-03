# sketches of Spain

A **minimal tool** for manually fetching patents and annotating them with a streamlined workflow.

## **Patent Highlighter**

A **Chrome/Firefox extension** that allows users to highlight and save annotations on patent documents, backed by a Python-based patent retrieval and storage system.

---

## **Features**

- **Fetch Patent Data:** Retrieve patent information from the **Lens.org API**.
- **Local Storage:** Store patent metadata in a **SQLite database**.
- **Browser Integration:** Highlight text within patents and save annotations.
- **Simple Setup:** Works as a **browser extension** with a **Python backend**.

### **Upcoming Features**

- **ML-Powered Patent Correlation:** Discover related patents automatically based on your highlights.
- **Export Tools:** Export your saved annotations in various formats.
- **Collaborative Annotations:** Share highlights with team members.

---

## **Installation & Setup**

### **1. Browser Extension Setup**

#### **Chrome**

1. Navigate to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top-right)
3. Click "Load unpacked" and select the repository folder
4. Note your extension ID for the next step

#### **Firefox**

1. Go to `about:debugging#/runtime/this-firefox`
2. Click "Load Temporary Add-on"
3. Select any file from the repository

### **2. Native Messaging Configuration**

To enable communication between the extension and the Python backend, create a native messaging host manifest file:

```json
{
  "name": "com.example.patents",
  "description": "Native messaging host for patent annotations",
  "path": "ABSOLUTE_PATH_TO/host.py",
  "type": "stdio",
  "allowed_origins": [
    "chrome-extension://YOUR_EXTENSION_ID/"
  ]
}
```

Save this file to:

#### **Chrome**

- **Windows:** `%USERPROFILE%\AppData\Local\Google\Chrome\User Data\NativeMessagingHosts\com.example.patents.json`
- **macOS:** `~/Library/Application Support/Google/Chrome/NativeMessagingHosts/com.example.patents.json`
- **Linux:** `~/.config/google-chrome/NativeMessagingHosts/com.example.patents.json`

#### **Firefox**

- **Windows:** `%APPDATA%\Mozilla\NativeMessagingHosts\com.example.patents.json`
- **macOS:** `~/Library/Application Support/Mozilla/NativeMessagingHosts/com.example.patents.json`
- **Linux:** `~/.mozilla/native-messaging-hosts/com.example.patents.json`

---

## API Token Setup

Obtain an API token from Lens.org and set it as an environment variable:

```bash
# Linux/macOS
export LENS_API_KEY="your_secret_token_here"

# Windows
set LENS_API_KEY=your_secret_token_here
```

**IMPORTANT:** Never store your API token directly in your code or commit it to version control.

---

## **Dependencies**

All required libraries are included in the `package.json` file. To install the dependencies, simply run:

```bash
npm install
```

---

## **Troubleshooting**

If the extension doesn’t connect to the backend:

- **Ensure** `host.py` is running.
- **Verify** your extension ID is correctly set in the native messaging manifest.
- **Check file paths** to ensure they are absolute and correct for your system.

---

## **Credits**

- **Lens.org** for providing the patent data API.
- **GitHub Copilot** for development assistance.

## **License**

This project is licensed under [MIT License](LICENSE).

