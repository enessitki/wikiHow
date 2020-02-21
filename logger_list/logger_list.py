import subprocess


class LoggerList:
    def __init__(self, temp_dir=""):
        # args
        self.tempDir = temp_dir
        self.maxCacheSize = 5

        # sys vars
        self.cache = []
        self.currentFileCache = []
        self.currentFileIndex = 0
        self.maxFileIndex = 0
        self.globalMaxIndex = -1

    def append(self, val):
        if len(self.cache) >= self.maxCacheSize:
            self.create_file()
            self.cache.clear()

        self.cache.append(val)
        self.globalMaxIndex += 1

    def create_file(self):
        f = open(str(self.maxFileIndex), "w")
        f.write(str(self.cache)[1:-1].replace(" ", ""))
        f.close()
        self.maxFileIndex += 1

    def load_file(self, file_id):
        if self.maxFileIndex < file_id:
            raise Exception("File not created")
        else:
            f = open(str(file_id))
            data = f.read()
            self.currentFileCache = [float(x) for x in data.split(",")]
            self.currentFileIndex = file_id

    def __getitem__(self, item):
        if self.globalMaxIndex < item:
            raise Exception("Index out of range.")

        file_id = int(item / self.maxCacheSize)
        loc_idx = item % self.maxCacheSize

        if file_id == self.maxFileIndex:
            return self.cache[loc_idx]
        elif file_id == self.currentFileIndex:
            return self.currentFileCache[loc_idx]
        else:
            self.load_file(file_id)
            return self.currentFileCache[loc_idx]

    def __iter__(self):
        return [12, 13, 15].__iter__()

    def __len__(self):
        return self.globalMaxIndex + 1

    def __setitem__(self, key, value):
        if self.globalMaxIndex < key:
            raise Exception("Index out of range.")

        file_id = int(key / self.maxCacheSize)
        loc_idx = key % self.maxCacheSize

        if file_id == self.maxFileIndex:
            self.cache[loc_idx] = value

        elif file_id == self.currentFileIndex:
            raise Exception("Operation not supported.")
        else:
            self.load_file(file_id)
            raise Exception("Operation not supported.")

    def clean_temp(self):
        subprocess.call("rm -r " + self.tempDir + "/*", shell=True)


my_list = LoggerList()
#
# print(my_list[100])
#
for n in range(11):
    my_list.append(n*7.5)

print(my_list[10])
print(my_list[7])
print(my_list[2])
print(my_list[0])

