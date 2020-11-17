from src import SettingsTools as st
from src.FileOperator import YAMLFile

droid = st.AgrodroidBU()
droid_channel = droid.channel
bu = YAMLFile().read_from_the_file()


def unpacking_all_you_needs():
    files_names = droid.ftp.listdir(directory_path)


class PackageCreator:
    def __init__(self, *args):
        pass
