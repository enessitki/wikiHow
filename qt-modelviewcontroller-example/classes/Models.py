class File:
    def __init__(self, file_name, full_path, extension):
        self.fileName = file_name
        self.fullPath = full_path
        self.extension = extension


class FilesModel:
    def __init__(self):
        self.files = []

    def create_file(self, file_name, full_path, extension):
        file = File(file_name, full_path, extension)
        self.files.append(file)
        return file

    def get_files(self):
        files_array = []
        for file in self.files:
            files_array.append((file.fileName, file.fullPath, file.extension))
        return files_array
        
    def add_file(self, file):
        self.files.append(file)

    def delete_file(self, file=None, index=None):
        if file is None and index is None:
            return False
        else:
            if index is not None:
                if index <= len(self.files):
                    self.files.pop(index)
                    return True
                else:
                    return False

            elif file is not None:
                if file in self.files:
                    try:
                        index = self.files.index(file)
                        self.files.pop(index)
                        return True
                    except:
                        return False

                else:
                    return False
            else:
                return False

    def clear(self):
        self.files = []
        return True

    def __len__(self):
        return len(self.files)
