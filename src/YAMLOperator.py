import src.FileOperation


class YAMLFile:

    def __init__(self, YAML_path, dict_name='default', input_dict=None):
        self.file = src.FileOperation.EditingFile(YAML_path)
        self.__name__ = dict_name
        self.get_me_dict(input_dict)

    def get_me_dict(self, input_dict):
        if input_dict is None:
            self.__dict__.update(self.parse_file())
        else:
            self.__dict__.update(input_dict)

    def parse_file(self):
        file_content = self.file.read_of_the_file()
        if len(file_content) <= 1:
            print('Файл пуст, не могу ничего загрузить отсюда!')
            return {}
        else:
            content_range = self.find_content_range_by_name(file_content)
            if len(content_range) > 0:
                return self.dict_forming(file_content, content_range)
            else:
                print('Искомые данные не найдены')
                return self.dict_forming(file_content, (0, len(file_content)))

    def find_content_range_by_name(self, content):
        content_range = list()
        begin_range = content.find(f'{self.__name__}:')
        if begin_range != -1:
            content_range.append(begin_range)
            end_range = content.find('\n\n', begin_range)
            content_range.append(end_range) \
                if end_range != -1 \
                else content_range.append(len(content))
        return tuple(content_range)

    def dict_forming(self, content, content_range):
        d = {}
        content = content[content_range[0]: content_range[1]].split('\n')
        for i in range(1, len(content)):
            parts = content[i].split(': ')
            d[f'{parts[0].strip()}'] = int(parts[1].strip("'")) \
                if parts[1].strip("'").isdigit()\
                else parts[1].strip("'")
        return d

    def config_to_text(self):
        output = f"{self.__dict__['__name__']}:\n"
        for key, value in self.__dict__.items():
            if key not in ('file', '__name__'):
                output = output + f"  {key}: {value}\n" \
                    if (isinstance(value, int))\
                    else output + f"  {key}: '{value}'\n"
        return output

    def write_config_in_the_file(self):
        old_conf = YAMLFile(self.file.path, self.__name__).config_to_text()
        new_conf = self.config_to_text()
        self.file.edit_file(new_conf, old_conf)
