# PDF Extractor

## Requirements
- need poppler for your target os, for windows go to the github project https://github.com/oschwartz10612/poppler-windows 

# Steps to setup Poppler

1. **Extract zip and put in C drive**
2. **Setting the Environment Variables**:

   - If you want to use Poppler's utilities (such as pdftotext, pdfimages, etc.) from the command line, you should add the binaries to your system's PATH.

   - Right-click on "**This PC"** or **"Computer"** (depends on your Windows version) and choose **Properties**.
   - Select Advanced system settings on the left.
   - In the System Properties window, click the Environment Variables button.
   - Under **"System Variables"**, find and select the **PATH** variable, then click the Edit button.
   - Add the path to the bin directory where you extracted the Poppler binaries. For example, if you extracted the files to `C:\poppler`, you would add `C:\poppler\bin`.
   - Click **OK** to close each window.

3. **Testing the Installation**:

To ensure that Poppler's utilities are working, open a Command Prompt or PowerShell and type:

        `pdftotext --version`
