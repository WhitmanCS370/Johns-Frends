from pathlib import Path
import shutil
import unittest
from src.sqlite_init import create_db
from src.commands import *
from src.dummy_cache import DummyCache
from src.sqlite_init import *
from src.sqlite_storage import Sqlite
from src.storage_commander import StorageCommander


def addAllSounds(base_dir, commander):
    for path in Path(base_dir).iterdir():
        commander.addSound(path)


class BasicTests(unittest.TestCase):
    # copy the test_sounds directory so that way we can modify it without worry
    def setUp(self):
        self.base_dir = Path("test", "temp_test_sounds")
        shutil.copytree(Path("test", "test_sounds"), self.base_dir)
        self.db_name = Path("test", "test_audio_archive.db")
        create_db(str(self.db_name))
        storage = StorageCommander(
            DummyCache(), Sqlite(str(self.db_name)), str(self.base_dir)
        )
        self.commander = Commander(storage)

    def tearDown(self):
        Path(self.db_name).unlink()
        shutil.rmtree(self.base_dir)

    def test_addSoundInDirSameName(self):
        self.commander.addSound(Path(self.base_dir, "coffee.wav"))
        sound = self.commander.storage.getByName("coffee")
        # the new sound should be in the database
        self.assertEqual(sound.name, "coffee")
        self.assertTrue(sound.file_path.exists())

    def test_addSoundInDirNewName(self):
        self.commander.addSound(Path(self.base_dir, "coffee.wav"), "new_sound")
        sound = self.commander.storage.getByName("new_sound")
        # the new sound should be in the database
        self.assertEqual(sound.name, "new_sound")
        # the file should be renamed
        self.assertTrue(Path(self.base_dir, "new_sound.wav").exists())
        # the old file should not be there
        self.assertFalse(Path(self.base_dir, "coffee.wav").exists())

    def test_addSoundOtherDirSameName(self):
        old_path = Path("test_sound.wav")
        shutil.move(Path(self.base_dir, "coffee.wav"), old_path)
        self.commander.addSound(old_path)
        sound = self.commander.storage.getByName("test_sound")
        # the new sound should be in the database
        self.assertEqual(sound.name, "test_sound")
        # the file should be renamed
        self.assertTrue(Path(self.base_dir, old_path).exists())
        # the old file should be there too
        self.assertTrue(old_path.exists())
        old_path.unlink()

    def test_addSoundOtherDirNewName(self):
        old_path = Path("test_sound.wav")
        shutil.move(Path(self.base_dir, "coffee.wav"), old_path)
        self.commander.addSound(old_path, "new_sound")
        sound = self.commander.storage.getByName("new_sound")
        # the new sound should be in the database
        self.assertEqual(sound.name, "new_sound")
        # the file should be renamed
        self.assertTrue(Path(self.base_dir, "new_sound.wav").exists())
        # the old file should be there too
        self.assertTrue(old_path.exists())
        old_path.unlink()

    def test_addSoundAlreadyExists(self):
        path = Path(self.base_dir, "coffee.wav")
        # we should be able to add this the first time but not the second
        self.assertTrue(self.commander.addSound(path))
        with self.assertRaises(NameExists):
            self.commander.addSound(path)

    def test_removeSoundSuccess(self):
        path = Path(self.base_dir, "coffee.wav")
        self.commander.addSound(path)
        self.assertTrue(self.commander.removeSound("coffee"))
        self.assertFalse(path.exists())

    def test_removeSoundFail(self):
        # can't remove a sound if it doesn't exist
        with self.assertRaises(NameMissing):
            self.commander.removeSound("coffee")

    def test_addTag(self):
        addAllSounds(self.base_dir, self.commander)
        self.commander.addTag("coffee", "example tag")
        self.commander.addTag("coffee-slurp-2", "example tag")
        audios = self.commander.storage.getByTags(["example tag"])
        names = {audio.name for audio in audios}
        self.assertSetEqual(names, {"coffee", "coffee-slurp-2"})

    def test_removeTag(self):
        addAllSounds(self.base_dir, self.commander)
        self.commander.addTag("coffee", "example tag")
        self.commander.removeTag("coffee", "example tag")
        audios = self.commander.storage.getByTags("example tag")
        self.assertEqual(len(audios), 0)

    def test_renameSuccess(self):
        addAllSounds(self.base_dir, self.commander)
        self.assertTrue(self.commander.rename("coffee", "new_name"))
        sound = self.commander.storage.getByName("new_name")
        self.assertEqual(Path(sound.file_path).stem, "new_name")
        self.assertEqual(sound.name, "new_name")
        self.assertTrue(Path(self.base_dir, "new_name.wav").exists())
        self.assertFalse(Path(self.base_dir, "coffee.wav").exists())

    def test_renameBadOldName(self):
        addAllSounds(self.base_dir, self.commander)
        with self.assertRaises(NameMissing):
            self.commander.rename("this_isn't_a_name", "new_name")

    def test_renameBadNewName(self):
        addAllSounds(self.base_dir, self.commander)
        with self.assertRaises(NameExists):
            self.commander.rename("coffee", "coffee-slurp-2")

    def test_getSounds(self):
        addAllSounds(self.base_dir, self.commander)
        sounds = {sound.name for sound in self.commander.getSounds()}
        self.assertSetEqual(
            sounds,
            {
                "coffee",
                "coffee-slurp-2",
                "coffee-slurp-3",
                "coffee-slurp-4",
                "coffee-slurp-5",
                "coffee-slurp-6",
                "coffee-slurp-7",
                "coffee-slurp-8",
                "toaster",
                "toaster-2",
            },
        )

    def test_clean(self):
        addAllSounds(self.base_dir, self.commander)
        # remove coffee.wav and toaster.wav and make sure that clean removes them
        Path(self.base_dir, "coffee.wav").unlink()
        Path(self.base_dir, "toaster.wav").unlink()
        removed_sounds = {sound.name for sound in self.commander.clean()}
        self.assertSetEqual(removed_sounds, {"coffee", "toaster"})


if __name__ == "__main__":
    unittest.main()
