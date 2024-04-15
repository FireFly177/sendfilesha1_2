from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi
import os
from sha1py import sha1

UPLOAD_DIR = './files'
file_hashes = {}  # Dictionary to store file hashes

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def hash_file_with_sha1py(self, filepath):
        # Calculate hash using the sha1 function from sha1py.py
        with open(filepath, 'rb') as file:
            message = file.read()
        return sha1(message)

    def do_POST(self):
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST'}
        )
        file_item = form['file'] if 'file' in form else None

        if file_item is not None and file_item.file:
            # Generate unique filename if file exists
            original_filename = file_item.filename
            filename = original_filename
            count = 0
            while os.path.exists(os.path.join(UPLOAD_DIR, filename)):
                count += 1
                filename = f"{os.path.splitext(original_filename)[0]}_{count}{os.path.splitext(original_filename)[1]}"

            # Save the file to the upload directory
            full_path = os.path.join(UPLOAD_DIR, filename)
            with open(full_path, 'wb') as f:
                f.write(file_item.file.read())

            # Calculate the hash of the uploaded file
            file_hash = self.hash_file_with_sha1py(full_path)
            file_hashes[filename] = file_hash  # Store hash in the dictionary

        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(filename.encode())

    def do_GET(self):
        if self.path == '/files':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            files_list = os.listdir(UPLOAD_DIR)
            files_html = ''.join(f'<li><a href="/download/{file}">{file}</a> - Hash: {file_hashes.get(file, "Not calculated")}</li>' for file in files_list)
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
            # Code for file downloading remains the same...
            # [code omitted for brevity]
            pass
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not found')

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
    run()
