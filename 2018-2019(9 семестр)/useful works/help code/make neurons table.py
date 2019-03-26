import xlsxwriter
import glob, os

def to_rus(str_float):
    return str_float[:len(str_float)-2] + ',' + str_float[-1]

if __name__ == "__main__":
    team = (1, 47)

    res = [
        'team_name',

        'clicks in vector',
        'iters',

        'middle FRR for set 0',
        'middle FAR for set 0',
        'reliability for set 0',

        'middle FRR for set 1',
        'middle FAR for set 1',
        'reliability for set 1',

        'middle FRR for set 2',
        'middle FAR for set 2',
        'reliability for set 2',

        'middle FRR for set 3',
        'middle FAR for set 3',
        'reliability for set 3',

        'middle FRR for set 4',
        'middle FAR for set 4',
        'reliability for set 4',
    ]

    s_path = "D:\\Documents\\Github\\NIR\\2018-2019(9 семестр)\\log_anal\\dataset\\"
    paths = [
        "team {} perm ['-'] 8t {}cl {}",
        "team {} perm ['domain', 'domain_maps'] 8t {}cl {}",
        "team {} perm ['domain', 'url_maps', 'domain_maps'] 8t {}cl {}",
        "team {} perm ['domain', 'dom_bi', 'dom_tri', 'domain_maps', 'grams_pause'] 8t {}cl {}",
        "team {} perm ['domain', 'dom_bi', 'dom_tri', 'domain_maps', 'url_maps', 'grams_pause', 'url_bi', 'url_tri'] 8t {}cl {}",
    ]

    words = [' 5cl', ' 15cl', ' 30cl']
    result_mass = [res]
    start_reliability = [0, 0, 0]

    iters_num = [5, 10, 15, 25, 50, 75, 100, 150]
    for word in words:
        result = [team[0], word[:len(word) - 2], ]
        iters = {
                    0:[],
                    1:[],
                    2:[],
                    3: [],
                    4: [],
                    5: [],
                    6: [],
                    7: [],
                   }
        for pt in paths:
            path = s_path + pt.format(team[0], int(word[:len(word) - 2]), team[1]) + '\\nej_otch.txt'
            with open(path) as f:
                content = f.readlines()
            text = ''.join(content)
            text = text.split('эпохи:')

            for i in range(8):
                data = text[i+1]
                #print ((data.split('средний FRR:')[1]).split('\n')[0])
                fl = 100*float((data.split('средний FRR:')[1]).split('\n')[0])
                iters[i].append(to_rus("%.1f" % fl))
                fl = 100 * float((data.split('средний FAR:')[1]).split('\n')[0])
                iters[i].append(to_rus("%.1f" % fl))
                fl = 100*float((data.split('точность:')[1]).split('\n')[0])
                iters[i].append(to_rus("%.1f" % fl))
        for i in range(8):
            result_mass.append(result + [iters_num[i]] + iters[i])


    workbook = xlsxwriter.Workbook('Attributes neurons' + str(team[0]) + '.xlsx')
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
