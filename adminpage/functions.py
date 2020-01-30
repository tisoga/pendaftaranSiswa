from datetime import datetime

def ratarata(model):
    try:
        for x in range(len(model)):
            if model[x].nilai_mtk == None:
                model[x].nilai_mtk = 0
            if model[x].nilai_inggris == None:
                model[x].nilai_inggris = 0
            if model[x].nilai_indonesia == None:
                model[x].nilai_indonesia = 0
            avg = (model[x].nilai_mtk + model[x].nilai_inggris +
                   model[x].nilai_indonesia) / 3
            avg = round(avg, 2)
            model[x].rata = avg
    except TypeError:
        if model.nilai_mtk == None:
            model.nilai_mtk = 0
        if model.nilai_inggris == None:
            model.nilai_inggris = 0
        if model.nilai_indonesia == None:
            model.nilai_indonesia = 0
        avg = (model.nilai_mtk + model.nilai_inggris +
               model.nilai_indonesia) / 3
        avg = round(avg, 2)
        model.rata = avg
    return model


def tahunakhir(model):
    for x in range(len(model)):
        nw = int(model[x].tahun) + 1
        model[x].thn = model[x].tahun + "-" + str(nw)
    return model


def convertdate(date):
    date = datetime.strptime(date, '%d-%m-%Y')
    return date.strftime('%Y-%m-%d')


def nilaitertinggi(model):
    i = 0
    data = {}
    for x in model:
        data[i] = x.rata
        i += 1
    return data