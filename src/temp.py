from functools import reduce

strings = [[],
           ['SOC', 'family:tegra186', 'Machine:quill'],
           ['Online', 'CPUs:', '0-5'],
           ['CPU', 'Cluster', 'Switching:', 'Disabled'],
           ['cpu0:', 'Online=1', 'Governor=schedutil', 'MinFreq=2035200', 'MaxFreq=2035200', 'CurrentFreq=2035200',
            'IdleStates:', 'C1=0', 'c7=0'],
           ['cpu1:', 'Online=1', 'Governor=schedutil', 'MinFreq=2035200', 'MaxFreq=2035200', 'CurrentFreq=2035200',
            'IdleStates:', 'C1=0', 'c6=0', 'c7=0'],
           ['cpu2:', 'Online=1', 'Governor=schedutil', 'MinFreq=2035200', 'MaxFreq=2035200', 'CurrentFreq=2035200',
            'IdleStates:', 'C1=0', 'c6=0', 'c7=0'],
           ['cpu3:', 'Online=1', 'Governor=schedutil', 'MinFreq=2035200', 'MaxFreq=2035200', 'CurrentFreq=2035200',
            'IdleStates:', 'C1=0', 'c7=0'],
           ['cpu4:', 'Online=1', 'Governor=schedutil', 'MinFreq=2035200', 'MaxFreq=2035200', 'CurrentFreq=2035200',
            'IdleStates:', 'C1=0', 'c7=0'],
           ['cpu5:', 'Online=1', 'Governor=schedutil', 'MinFreq=2035200', 'MaxFreq=2035200', 'CurrentFreq=2035200',
            'IdleStates:', 'C1=0', 'c7=0'],
           ['GPU', 'MinFreq=1300500000', 'MaxFreq=1300500000', 'CurrentFreq=1300500000'],
           ['EMC', 'MinFreq=40800000', 'MaxFreq=1866000000', 'CurrentFreq=1866000000', 'FreqOverride=1'],
           ["Can't", 'access', 'Fan!'],
           ['NV', 'Power', 'Mode:', 'MAXN'],
           ['agrodroid@agrodroid-20071110:~$']]

[strings.remove(st) for st in strings if len(st) == 0]
print(strings)


def extend_and_return(x, y):
    x.extend(y)
    return x


temp = reduce(lambda x, y: extend_and_return(x, y), strings)

items = [10, 20, 30, 40, 50]
sum_all = reduce(lambda x, y: x + y, items)

print(temp)
