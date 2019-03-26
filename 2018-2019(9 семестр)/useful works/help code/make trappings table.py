import xlsxwriter
import glob, os

team = 2
res = [
    'team_name',

    '-',
    'domain',
    'dom_bi',
    'dom_tri',
    'domain_maps',
    'url_maps',
    'grams_pause',
    'url_bi',
    'url_tri',

    'alg ML',

    'vector_len',
    'middle FRR(5 click)',
    'middle FAR(5 click)',
    'reliability(5 click)',
    'add reliability(5 click)',

    'vector_len',
    'middle FRR(15 click)',
    'middle FAR(15 click)',
    'reliability(15 click)',
    'add reliability(15 click)',

    'vector_len',
    'middle FRR(30 click)',
    'middle FAR(30 click)',
    'reliability(30 click)',
    'add reliability(30 click)',
]
start_path = "D:/Documents/Github/NIR/2018-2019(9 семестр)/log_anal/dataset"
os.chdir(start_path)
filenames = []
permissions = [
            ['-'],
            ['domain'],
            ['domain', 'domain_maps'],
            ['domain', 'url_maps'],
            ['domain', 'url_maps', 'domain_maps'],
            ['domain', 'dom_bi'],
            ['domain', 'dom_bi', 'dom_tri'],
            ['domain', 'dom_bi', 'dom_tri', 'url_bi', 'url_tri'],
            ['domain', 'url_bi', 'url_tri'],
            ['domain', 'dom_bi', 'dom_tri', 'grams_pause'],
            ['domain', 'dom_bi', 'dom_tri', 'domain_maps', 'grams_pause'],
            ['domain', 'dom_bi', 'dom_tri', 'domain_maps', 'url_maps', 'grams_pause', 'url_bi', 'url_tri'],
        ]
file_perm = {}
for file in glob.glob("team " + str(team) + "*"):
    filenames.append(file)

file_perm = dict()
for p in permissions:
    file_perm[tuple(p)] = [file for file in filenames if file.find(str(p)) != -1]
print(file_perm)

words = [' 5cl', ' 15cl', ' 30cl']
result_mass = [res]
ML = ['RF', "LR", "SVM"]
start_reliability = [0, 0, 0]
# идем по признакам
# для каждого признака в таблице подует по три строки - на три алгоритма МО
for perm, files in file_perm.items():

    # команду заполняем признаки
    result = [team, '-', '-', '-', '-', '-', '-', '-', '-', '-']
    for p in perm:
        print(p)
        result[res.index(p)] = '+'

    alg = {
            0:[],
            1:[],
            2:[],
           }
    max_reliabilitys = {
        0: 0,
        1: 0,
        2: 0,
    }

    # проходимся по файлам с разным числом кликов
    for word in words:
        for f in files:
            if f.find(word) != -1:
                file = f
                break
        path = start_path + "/" + file + "/" + "otch.txt"

        with open(path) as f:
            content = f.readlines()

        len_vector = int(content[0].split(' ')[-1])

        text = ''.join(content)
        if text.find('точность:') == -1:
            mass = text.split('ошибается вообще:')
        else:
            mass = text.split('точность:')

        mass = mass[1:]
        n_alg = 0
        max_reliability = 0
        for errors in mass:
            j = 0
            FAR = 0
            FRR = 0
            strs = errors.split('\n')
            reliability = float(strs[0])
            if reliability > max_reliability:
                max_reliability = reliability

            strs = strs[1:]
            if errors.find("средний FAR:") == -1:
                for err in strs:
                    if err.find('FAR') != -1:
                        FAR += float(err.split(':')[1])
                    elif err.find('FRR') != -1:
                        FRR += float(err.split(':')[1])
                    j += 1
                alg[n_alg] += [len_vector, "%.1f" % (FAR/j*100), "%.1f" % (FRR/j*100), "%.1f" % (reliability*100), (-1)*(words.index(word)+1)]
            else:
                for err in strs:
                    if err.find('средний FAR:') != -1:
                        FAR = float(err.split(':')[1])
                    elif err.find('средний FRR:') != -1:
                        FRR = float(err.split(':')[1])
                alg[n_alg] += [len_vector, "%.1f" % (FAR*100), "%.1f" % (FRR*100), "%.1f" % (reliability*100), (-1)*(words.index(word)+1)]
            n_alg += 1
        max_reliabilitys[words.index(word)] = max_reliability

    print(perm)
    for i in alg:
        add_relabil = [0, 0, 0]
        if perm == ('-',):
            add_reliability = [0, 0, 0]
            start_reliability = [rel for k, rel in max_reliabilitys.items()]
        else:
            add_relabil = ["%.1f" % ((max_reliabilitys[ii] - start_reliability[ii]) * 100) for ii in range(3)]
        for ii in range(3):
            print(alg[i])
            num = alg[i].index((-1)*(ii+1))
            alg[i][num] = add_relabil[ii]
        mas1 = result + [ML[i]] + alg[i]
        result_mass.append(mas1.copy())







workbook = xlsxwriter.Workbook('Attributes' + str(team) + '.xlsx')
worksheet = workbook.add_worksheet()
row = 0
col = 0

# Iterate over the data and write it out row by row.
for str in result_mass:
    j = 0
    print(str)

    for i in str:
        worksheet.write(row, j, i)
        j += 1
    row += 1

workbook.close()
