class DummyCache:
    def __init__(self):
        pass

    def addSound(self, file_path, name=None, author=None):
        return True

    def removeByName(self, name):
        return True

    def getByName(self, name):
        return

    def getByTags(self, tags):
        return

    def rename(self, old_name, new_name):
        return

    def addTag(self, name, tag):
        return

    def removeTag(self, name, tag):
        return

    def cache(self, _):
        return
