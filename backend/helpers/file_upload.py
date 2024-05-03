from .firebase import upload_to_firebase_storage
from django.core.files.uploadedfile import InMemoryUploadedFile

def handle_file_upload(self, request, file_key, file_name):
        file = request.FILES.get(file_key)
        file_link = None

        if file:
            folder = f"user_files/{request.data['FirstName']}"
            file_content = file.read()

            if isinstance(file, InMemoryUploadedFile):
                file_link = upload_to_firebase_storage(folder, file_name, file_content, )
            else:
                local_file_path = file.temporary_file_path()
                file_link = upload_to_firebase_storage(folder, file_name, local_file_path, )

            # print(f"{file_name.capitalize()} Link Before Saving:", file_link)

        return file_link