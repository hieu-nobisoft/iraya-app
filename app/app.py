import atexit
import uuid
import os
import asyncio
import magic
from quart import Quart, request
from prisma import Prisma
from prisma.models import Upload

from azureConfig import get_client;

loop = asyncio.get_event_loop()

app = Quart(__name__)
app.config['MAX_CONTENT_LENGTH'] = 512 * 1000 * 1000
prisma = Prisma(auto_register=True)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.before_serving
async def startup_handler() -> None:
    await prisma.connect()

@app.after_serving
async def shutdown_handler() -> None:
    if prisma.is_connected():
       await prisma.disconnect()

@app.route("/upload", methods=['GET', 'POST'])
async def upload_file():
    if request.method == 'POST':
        files =await request.files
        if 'File' not in files:
            return "No files"
        file = files['File']
        if file.filename == '':
            return "No file selected"
        id = uuid.uuid4()
        args = request.args
        await file.save(str(id))
        upload = await Upload.prisma().create(
            data={
                "id":str(id),
            },
        )
        filetype =magic.from_buffer(open(str(id), "rb").read(2048))
        blob_service_client = get_client()
        container_client = blob_service_client.get_container_client(container=os.getenv("AZURE_STORAGE_CONTAINER"))

        with open(file=str(id), mode="rb") as data:
            blob_client = container_client.upload_blob(name=str(id), data=data, overwrite=True,metadata={'uploader':str(args.get("user")),'filename':file.filename,'filetype': filetype })
        os.remove(str(id))

    return "Success"

def main():

    app.run(debug=True, port=8080, host='0.0.0.0')