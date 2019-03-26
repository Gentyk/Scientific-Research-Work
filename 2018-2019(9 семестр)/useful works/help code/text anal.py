ss = """bv FAR:0.07169056352117373
bv FRR:0.17808904452226113
im FAR:0.11628876292097366
im FRR:0.2003000750187547
ro FAR:0.10795265088362788
ro FRR:0.5093773443360841
/
bv FAR:0.06243747915971991
bv FRR:0.05952976488244122
im FAR:0.09503167722574192
im FRR:0.2565641410352588
ro FAR:0.09511503834611537
ro FRR:0.44161040260065015
/
bv FAR:0.07060686895631878
bv FRR:0.13981990995497748
im FAR:0.09469823274424809
im FRR:0.22555638909727432
ro FAR:0.09944981660553517
ro FRR:0.4288572143035759"""

al = 0
for s in ss.split('\n/\n'):
    print(al)
    mass = s.split('\n')
    FRR = 0
    FAR = 0
    j = 0
    for i in mass:
        if j % 2 == 0:
            FAR += float(i.split(':')[1])
        else:
            FRR += float(i.split(':')[1])
        j += 1
    print('FRR {}'.format(FRR/(len(mass)//2)))
    print('FAR {}'.format(FAR/(len(mass)//2)))
    al += 1