from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi
import os
import shutil
from sha1py import sha1

UPLOAD_DIR = './files'

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def hash_file_with_sha1py(self, filepath):
        # Calculate hash using the sha1 function from sha1py.py
        with open(filepath, 'rb') as file:
            message = file.read()
        return sha1(message)

    def save_hash_to_file(self, filename, file_hash):
        # Save the hash value along with the original filename to a text file
        hash_filename = f'{filename}sha1.txt'
        with open(os.path.join(UPLOAD_DIR, hash_filename), 'w') as f:
            f.write(f'Original Filename: {filename}\n')
            f.write(f'File Hash: {file_hash}\n')
            
    def do_POST(self):
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST'}
        )
        message = form.getvalue('message')
        file_item = form['file'] if 'file' in form else None

        if file_item is not None and file_item.file:
            # Save the file to the upload directory
            filename = os.path.join(UPLOAD_DIR, file_item.filename)
            with open(filename, 'wb') as f:
                f.write(file_item.file.read())

            # Calculate the hash of the uploaded file
            file_hash = self.hash_file_with_sha1py(filename)

            # Save the hash to a text file
            self.save_hash_to_file(file_item.filename, file_hash)

            message = file_item.filename

        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.send_header('Access-Control-Allow-Origin', '*')  # Allow requests from any origin
        self.end_headers()

        self.wfile.write(message.encode())
        
    def do_GET(self):
        if self.path == '/files':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.send_header('Access-Control-Allow-Origin', '*')  # Allow requests from any origin
            self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
            self.send_header("Access-Control-Max-Age", "86400")
            self.end_headers()

            files_list = os.listdir(UPLOAD_DIR)
            files_html = ''.join(f'<li><a href="/download/{file}">{file}</a></li>' for file in files_list)
            response_content = f'''
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Files List</title>
                </head>
                <body>
                    <h1>List of Files</h1>
                    <ul>{files_html}</ul>
                </body>
                </html>
            '''
            self.wfile.write(response_content.encode())

        elif self.path.startswith('/download/'):
            # Serve the requested file for download
            filename = self.path[len('/download/'):]
            filepath = os.path.join(UPLOAD_DIR, filename)
            if os.path.isfile(filepath):
                with open(filepath, 'rb') as file:
                    content = file.read()
                self.send_response(200)
                self.send_header('Content-type', 'application/octet-stream')
                self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
                self.send_header('Access-Control-Allow-Origin', '*')  # Allow requests from any origin
                self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
                self.send_header("Access-Control-Max-Age", "86400")
                self.end_headers()
                self.wfile.write(content)     
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'File not found')
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not found')

            
def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8001):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    # Create the upload directory if it does not exist
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
    run()
