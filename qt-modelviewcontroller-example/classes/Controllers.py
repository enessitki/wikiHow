class FilesController:
    def __init__(self, files_model, files_view):
        self.filesModel = files_model
        self.filesView = files_view
        self.filesView.scanButton.clicked.connect(self.update_view)
        self.filesView.deleteButton.clicked.connect(self.clear_view)

    def set_files(self, files_array):
        for file_name, full_path, extension in files_array:
            self.filesModel.create_file(file_name, full_path, extension)

    def clear_files(self):
        self.filesModel.clear()

    def clear_view(self):
        self.filesView.clear()

    def update_view(self):
        self.filesView.update_view(self.filesModel.get_files())
