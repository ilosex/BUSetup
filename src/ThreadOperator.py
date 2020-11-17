import datetime
import sys
import threading
from queue import Queue


class Worker(threading.Thread):
    """
    Класс потока который будет брать задачи из очереди и выполнять их до успешного
    окончания или до исчерпания лимита попыток
    """

    def __init__(self, queue):
        # Обязательно инициализируем супер класс (класс родитель)
        super(Worker, self).__init__()
        # Устанавливаем поток в роли демона, это необходимо что бы по окончании выполнения
        # метода run() поток корректно завершил работу,а не остался висеть в ожидании
        self.setDaemon(True)
        # экземпляр класса содержит в себе очередь что бы при выполнении потока иметь к ней доступ
        self.queue = queue

    def run(self):
        """
        Основной код выполнения потока должен находиться здесь
        """
        while True:
            try:
                # фиксируем время начала работы потока
                FMT = '%H:%M:%S'
                start = datetime.datetime.now().strftime(FMT)
                # запрашиваем из очереди объект
                target = self.queue.get()
                print(f'{self.getName()} get target: {target}')

                # сообщаем о том что задача для полученного объекта из очереди выполнена
                # self.output.put(target, block=False)
                stop = datetime.datetime.now().strftime(FMT)
                timedelta = datetime.datetime.strptime(stop, FMT) - datetime.datetime.strptime(start, FMT)
                self.queue.task_done()
                print(f'Время исполнения задачи {target} составило {timedelta}')
            # После того как очередь опустеет будет сгенерировано исключение
            except Queue.empty(self.queue):
                sys.stderr.write(f'{self.getName()} get Queue.EMPTY exception\r\n')
                break
            # если при выполнении потока будет сгенерировано исключение об ошибке,
            # то оно будет обработано ниже
            except Exception as e:
                self.queue.task_done()
                # выводим на экран имя потока и инфо об ошибке
                sys.stderr.write(f'{self.getName(), e} get %s exception\r\n')
                # Предполагаем раз объект из очереди не был корреткно обработан,
                # то добавляем его в очередь
                self.queue.put(target, block=False)


class Test:
    def __init__(self, number_threads, *args):
        # создаем экземпля класса очереди Queue
        self.queue = Queue()
        self.output = Queue()
        # заполняем очередь
        for item in args:
            self.queue.put(item)
        # определяем количество потоков которые будут обслуживать очередь
        self.NUMBER_THREADS = number_threads
        # список экземпляров класса потока, в последствии можно
        # обратиться к нему что бы получать сведения о состоянии потоков
        self.threads = []

    def execute(self):
        # создаем экземпляра классов потоков и запускаем их
        for i in range(self.NUMBER_THREADS):
            self.threads.append(Worker(self.queue))
            self.threads[-1].start()

        # Блокируем выполнение кода до тех пор пока не будут выполнены все
        # элементы очереди. Это означает что сколкьо раз были добавлены элементы
        # очереди, то столько же раз должен быть вызван task_done().
        self.queue.join()


if __name__ == '__main__':
    t = datetime.datetime.now()
    test = Test(range(100), 20)
    test.execute()
    print(f'the end in {datetime.datetime.now() - t}')
    # вывод debug информации
    print(len(list(test.output.__dict__['queue'])))
    print(sorted(list(test.output.__dict__['queue'])))
