from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from django.db import IntegrityError
from django.db.models import Q
from django.contrib.auth.hashers import make_password
from .models import tabel_siswa, tahun_ajaran, tabel_admin, tahun_ajaran_aktif, mata_pelajaran, kumpulan_soal
from .functions import ratarata, tahunakhir, convertdate, nilaitertinggi
import math
import random

# Create your views here.


def register(request):
    if not request.user.is_authenticated:
        return redirect('adminPage:redirect_site')
    name = tabel_admin.objects.get(
        username=request.user).get_full_name()
    judul = 'Register Admin Baru'
    if request.method == 'POST':
        # print(request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('nama_depan')
        last_name = request.POST.get('nama_belakang')
        try:
            tabel_admin.objects.create_user(
                username, password, first_name, last_name)
            messages.success(request, f'Admin berhasil ditambahkan')
        except IntegrityError:
            messages.error(request, f'Username sudah ada')
            return redirect('adminPage:register')
        return redirect('adminPage:homepage')
    return render(request=request,
                  template_name='html/register.html',
                  context={'judul': judul, 'active': 'register', 'name': name})


def login(request):
    if request.method == 'POST':
        if request.POST.get('admin'):
            user = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=user, password=password)
            if user:
                request.session['user'] = user.username
                return redirect('adminPage:homepage')
            else:
                messages.error(request, f'Username atau password salah')
    return render(request=request,
                  template_name='html/login.html')


def redirect_site(request):
    if 'user' in request.session:
        return redirect('adminPage:homepage')
    else:
        return redirect('pagesiswa:login')


def homepage(request):
    if not request.user.is_authenticated:
        return redirect('adminPage:redirect_site')
    tahun_aktif = tahun_ajaran_aktif.objects.all()[0].tahun_aktif
    name = tabel_admin.objects.get(
        username=request.user).get_full_name()
    judul = 'Beranda Tahun Ajaran ' + \
        tahun_aktif.tahun + '-' + str(int(tahun_aktif.tahun) + 1)
    # model = tabel_siswa.objects.all().filter(tahun_ajaran__tahun='2017')
    model = tabel_siswa.objects.all().filter(tahun_ajaran=tahun_aktif)
    model = ratarata(model)
    thn = tahun_ajaran.objects.all()
    thn = tahunakhir(thn)
    data = {'jumlah': len(model),
            'laki': len(model.filter(jenis_kelamin='Laki-Laki')),
            'perempuan': len(model.filter(jenis_kelamin='Perempuan')),
            }
    rata = 0
    tahun = []
    laki_all = []
    perempuan_all = []
    for x in model:
        rata += x.rata
    for x in thn:
        tahun.append(int(x.tahun))
        laki_all.append(len(tabel_siswa.objects.all().filter(
            tahun_ajaran__tahun=x).filter(jenis_kelamin='Laki-Laki')))
        perempuan_all.append(len(tabel_siswa.objects.all().filter(
            tahun_ajaran__tahun=x).filter(jenis_kelamin='Perempuan')))
    if data['jumlah'] > 0:
        data.update({'rata': round(rata / data['jumlah'], 2),
                     'tahun': tahun,
                     'perempuan_all': perempuan_all,
                     'laki_all': laki_all})
    else:
        data['rata'] = 0
    return render(request=request,
                  template_name='html/beranda.html',
                  context={'judul': judul, 'data': data, 'active': 'beranda', 'name': name})


def listsiswa(request):
    if not request.user.is_authenticated:
        return redirect('adminPage:redirect_site')
    tahun_aktif = tahun_ajaran_aktif.objects.all()[0].tahun_aktif
    name = tabel_admin.objects.get(
        username=request.user).get_full_name()
    judul = 'Tabel List Semua Siswa Tahun Ajaran ' + \
        tahun_aktif.tahun + '-' + str(int(tahun_aktif.tahun) + 1)
    model = tabel_siswa.objects.all().filter(tahun_ajaran=tahun_aktif)
    thn = tahun_ajaran.objects.all()
    thn = tahunakhir(thn)
    if request.method == 'POST':
        if request.POST.get('detail'):
            data = request.POST.get('data')
            return redirect('adminPage:detail', data)
        elif request.POST.get('hapus'):
            data = request.POST.get('data')
            tabel_siswa.objects.get(nis=data).delete()
            messages.error(request, f'Data Siswa Berhasil di hapus!')
            return redirect('adminPage:semua_siswa')
        elif request.POST.get('edit'):
            data = request.POST.get('data')
            return redirect('adminPage:edit', data)
        elif request.POST.get('ganti'):
            tahun = request.POST.get('ganti')
            model = tabel_siswa.objects.all().filter(tahun_ajaran__tahun=tahun)
            judul = 'Tabel List Semua Siswa Tahun Ajaran ' + \
                tahun + '-' + str(int(tahun) + 1)
    model = ratarata(model)
    return render(request=request,
                  template_name='html/tabelSiswa.html',
                  context={'judul': judul, 'list_siswa': model, 'tahun_ajaran': thn, 'active': 'semua',
                           'name': name})


def detailsiswa(request, nis):
    if not request.user.is_authenticated:
        return redirect('adminPage:redirect_site')
    name = tabel_admin.objects.get(
        username=request.user).get_full_name()
    data = tabel_siswa.objects.get(nis=nis)
    judul = 'Detail Siswa ' + data.nama
    data = ratarata(data)
    if request.method == 'POST':
        if request.POST.get('edit'):
            return redirect('adminPage:edit', nis)
        elif request.POST.get('hapus'):
            data.delete()
            messages.error(request, f'Data Siswa berhasil dihapus!')
            return redirect('adminPage:semua_siswa')
    return render(request=request,
                  template_name='html/detailSiswa.html',
                  context={'judul': judul, 'data': data, 'name': name})


def editsiswa(request, nis):
    if not request.user.is_authenticated:
        return redirect('adminPage:redirect_site')
    name = tabel_admin.objects.get(
        username=request.user).get_full_name()
    data = tabel_siswa.objects.get(nis=nis)
    judul = 'Edit Data Siswa ' + data.nama
    data = ratarata(data)
    thn = tahun_ajaran.objects.all()
    thn = tahunakhir(thn)
    if request.method == 'POST':
        if request.POST.get('edit'):
            data.nama = request.POST.get('nama')
            data.jenis_kelamin = request.POST.get('jk')
            data.alamat = request.POST.get('alamat')
            data.tempat_lahir = request.POST.get('tempat')
            if request.POST.get('tanggal'):
                data.tanggal_lahir = convertdate(request.POST.get('tanggal'))
            data.nilai_mtk = request.POST.get('mtk')
            data.nilai_indonesia = request.POST.get('indo')
            data.nilai_inggris = request.POST.get('inggris')
            data.tahun_ajaran = tahun_ajaran.objects.get(
                tahun=request.POST.get('tahun'))
            data.save()
            messages.success(request, f'Data Siswa nomor induk ' +
                             data.nis+' berhasil diedit!')
            return redirect('adminPage:semua_siswa')
    return render(request=request,
                  template_name='html/editSiswa.html',
                  context={'judul': judul, 'data': data, 'tahun': thn, 'name': name})


def penentuankelas(request):
    if not request.user.is_authenticated:
        return redirect('adminPage:redirect_site')
    tahun_aktif = tahun_ajaran_aktif.objects.all()[0].tahun_aktif
    name = tabel_admin.objects.get(
        username=request.user).get_full_name()
    judul = 'Penentuan Kelas untuk Tahun Ajaran ' + \
        tahun_aktif.tahun + '-' + str(int(tahun_aktif.tahun) + 1)
    model = tabel_siswa.objects.all().filter(tahun_ajaran=tahun_aktif)
    model = ratarata(model)
    thn = tahun_ajaran.objects.all()
    thn = tahunakhir(thn)
    kelas = []
    if request.method == 'POST':
        if request.POST.get('penentuan') == 'kelas':
            jumlah = int(request.POST.get('jumlah_kelas'))
            pembagian = request.POST.get('kriteria')
            batas = math.ceil(len(model) / jumlah)
            pembatas = 1
            if jumlah != 0:
                pass
            else:
                messages.error(request, f'Jumlah Kelas tidak boleh 0')
                return redirect('adminPage:penentuan')
        elif request.POST.get('penentuan') == 'siswa':
            jumlah = int(request.POST.get('jumlah_siswa'))
            pembagian = request.POST.get('kriteria')
            pembatas = 1
            if jumlah != 0:
                if len(model) == 0:
                    messages.error(request, f'Tidak Ada Siswa')
                    return redirect('adminPage:penentuan')
                elif pembagian == 'nilai':
                    data = nilaitertinggi(model)
                    for x in sorted(data.items(), reverse=True, key=lambda kv: (kv[1], kv[0])):
                        kelas.append(x[0])
                    kls = 'A'
                    for x in kelas:
                        if pembatas <= jumlah:
                            model[x].kelas = kls
                            model[x].save()
                            pembatas += 1
                        else:
                            kls = chr(ord(kls)+1)
                            model[x].kelas = kls
                            model[x].save()
                            pembatas = 2
                    messages.success(request, 'Penentuan Kelas Berhasil')
                    return redirect('adminPage:siswa_kelas')
                elif pembagian == 'jk':
                    kls = 'A'
                    data_laki = tabel_siswa.objects.all().filter(
                        tahun_ajaran=tahun_aktif).filter(jenis_kelamin='Laki-Laki')
                    data_perempuan = tabel_siswa.objects.all().filter(
                        tahun_ajaran=tahun_aktif).filter(jenis_kelamin='Perempuan')
                    for data in data_laki:
                        if pembatas <= jumlah:
                            data.kelas = kls
                            data.save()
                            pembatas += 1
                        else:
                            kls = chr(ord(kls) + 1)
                            data.kelas = kls
                            data.save()
                            pembatas = 2
                    pembatas = 1
                    kls = chr(ord(kls) + 1)
                    for data in data_perempuan:
                        if pembatas <= jumlah:
                            data.kelas = kls
                            data.save()
                            pembatas += 1
                        else:
                            kls = chr(ord(kls) + 1)
                            data.kelas = kls
                            data.save()
                            pembatas = 2
                    messages.success(request, 'Penentuan Kelas Berhasil')
                    return redirect('adminPage:siswa_kelas')
                elif pembagian == 'acak':
                    kls = 'A'
                    pembatas = 1
                    for x in range(len(model)):
                        kelas.append(x)
                    random.shuffle(kelas)
                    for i in kelas:
                        if pembatas <= jumlah:
                            model[i].kelas = kls
                            model[i].save()
                            pembatas += 1
                        else:
                            kls = chr(ord(kls)+1)
                            model[i].kelas = kls
                            model[i].save()
                            pembatas = 2
                    messages.success(request, 'Penentuan Kelas Berhasil')
                    return redirect('adminPage:siswa_kelas')

            else:
                messages.error(
                    request, f'Maksimal jumlah siswa perkelas minimal 1 Siswa')
                return redirect('adminPage:penentuan')
    return render(request=request,
                  template_name='html/penentuanKelas.html',
                  context={'judul': judul, 'tahun_ajaran': thn, 'list_siswa': model, 'active': 'penentuan',
                           'name': name})


def listsiswakelas(request):
    if not request.user.is_authenticated:
        return redirect('adminPage:redirect_site')
    tahun_aktif = tahun_ajaran_aktif.objects.all()[0].tahun_aktif
    name = tabel_admin.objects.get(
        username=request.user).get_full_name()
    judul = 'Tabel List Semua Siswa Tahun Ajaran ' + \
        tahun_aktif.tahun + '-' + str(int(tahun_aktif.tahun) + 1)
    model = tabel_siswa.objects.all().filter(tahun_ajaran=tahun_aktif)
    kelas = []
    semua = []
    if request.method == 'POST':
        if request.POST.get('ganti'):
            tahun = request.POST.get('ganti')
            tahun_aktif = tahun_ajaran.objects.get(tahun = tahun)
            model = tabel_siswa.objects.all().filter(tahun_ajaran=tahun_aktif)
            judul = 'Tabel List Semua Siswa Tahun Ajaran ' + \
                tahun + '-' + str(int(tahun) + 1)
    for kls in model:
        namaKelas = ''
        if kls.kelas:
            namaKelas = kls.kelas
        else:
            namaKelas = 'zzz'
        if namaKelas not in kelas:
            kelas.append(namaKelas)
    for kls in sorted(kelas):
        data = {}
        if kls == 'zzz':
            data['namaKelas'] = "Belum Mendapatkan kelas"
            mdl = tabel_siswa.objects.all().filter(
                tahun_ajaran=tahun_aktif).filter(Q(kelas=None) | Q(kelas=''))
            mdl = ratarata(mdl)
        else:
            data['namaKelas'] = "Kelas " + kls
            mdl = tabel_siswa.objects.all().filter(
                tahun_ajaran=tahun_aktif).filter(kelas=kls)
            mdl = ratarata(mdl)
        data['jumlah'] = len(mdl)
        data['siswa'] = mdl
        data['laki'] = len(mdl.filter(jenis_kelamin='Laki-Laki'))
        data['perempuan'] = len(mdl.filter(jenis_kelamin='Perempuan'))
        semua.append(data)
    thn = tahun_ajaran.objects.all()
    thn = tahunakhir(thn)
    return render(request=request,
                  template_name='html/tabelSiswaKelas.html',
                  context={'judul': judul, 'tahun': thn, 'semua': semua, 'active': 'kelas', 'name': name})


def tambahsiswa(request):
    if not request.user.is_authenticated:
        return redirect('adminPage:redirect_site')
    tahun_aktif = tahun_ajaran_aktif.objects.all()[0].tahun_aktif
    # print(type(tahun_aktif.tahun)
    name = tabel_admin.objects.get(
        username=request.user).get_full_name()
    judul = 'Tambah Siswa untuk Tahun Ajaran ' + \
        tahun_aktif.tahun + '-' + str(int(tahun_aktif.tahun) + 1)
    thn = tahun_ajaran.objects.all()
    if request.method == 'POST':
        # nis = request.POST.get('nis')
        nis = tahun_aktif.tahun[-2:] + \
            str(int(tahun_aktif.tahun[-2:]) + 1) + \
            str(random.randint(1000, 9999))
        nama = request.POST.get('nama')
        jk = request.POST.get('jk')
        tanggal = convertdate(request.POST.get('tanggal'))
        alamat = request.POST.get('alamat')
        tempat = request.POST.get('tempat')
        password = make_password(tanggal)
        mtk = request.POST.get('mtk')
        indo = request.POST.get('indo')
        inggris = request.POST.get('inggris')
        foto = request.FILES.get('foto')
        # tahun = tahun_ajaran.objects.get(tahun=request.POST.get('tahun'))
        tahun = tahun_aktif
        tabel_siswa.objects.create(
            nis=nis, nama=nama, password = password, jenis_kelamin=jk, alamat=alamat, tempat_lahir=tempat,
            nilai_mtk=mtk, nilai_indonesia=indo, nilai_inggris=inggris, tanggal_lahir=tanggal,
            tahun_ajaran=tahun, foto=foto)
        messages.success(request, f'Data Siswa '+nama+' Berhasil ditambahkan')
        return redirect('adminPage:semua_siswa')
    thn = tahunakhir(thn)
    return render(request=request,
                  template_name='html/tambahSiswa.html',
                  context={'judul': judul, 'tahun': thn, 'active': 'tambah', 'name': name})

def setTahunAjaran(request):
    if not request.user.is_authenticated:
        return redirect('adminPage:redirect_site')
    judul = 'Setting Tahun Ajaran'
    name = tabel_admin.objects.get(
        username=request.user).get_full_name()
    thn = tahun_ajaran.objects.all()
    thn = tahunakhir(thn)
    tahun_aktif = tahun_ajaran_aktif.objects.all()[0]
    if request.method == 'POST':
        tahun = request.POST.get('tahun')
        tahun_aktif.tahun_aktif = tahun_ajaran.objects.get(tahun = tahun)
        tahun_aktif.is_active = request.POST.get('pendaftaraan')
        tahun_aktif.save()
        messages.success(request, f'Tahun Ajaran Berhasil diganti')
        return redirect('adminPage:homepage')
    return render(request = request,
                  template_name = 'html/setting_tahun_ajaran.html',
                  context= {'judul': judul, 'tahun': thn, 'tahun_aktif': tahun_aktif, 'name': name,
                            'active': 'set_tahun'})

def tambahTahunAjaran(request):
    if not request.user.is_authenticated:
        return redirect('adminPage:redirect_site')
    if request.method == 'POST':
        try:
            tahun_ajaran.objects.create(tahun = request.POST.get('tahun_baru'))
            messages.success(request, f'Penambahan Tahun Ajaran Berhasil')
            return redirect('adminPage:set_tahun')
        except IntegrityError:
            messages.error(request, f'Gagal! Tahun Ajaran Sudah ada')
    judul = 'Tahun Ajaran Baru '
    name = tabel_admin.objects.get(
        username=request.user).get_full_name()
    return render(request = request,
                  template_name = 'html/tahun_ajaran_baru.html',
                  context= {'judul': judul, 'name': name, 'active': 'tambah_tahun'})

def pilihMatpel(request):
    if not request.user.is_authenticated:
        return redirect('adminPage:redirect_site')
    name = tabel_admin.objects.get(
        username=request.user).get_full_name()
    tahun_aktif = tahun_ajaran_aktif.objects.all()[0].tahun_aktif
    # judul = 'Buat Soal untuk Test Tahun Ajaran ' + \
    #     tahun_aktif.tahun + '-' + str(int(tahun_aktif.tahun) + 1)
    judul = 'Pilih Mata Pelajaran'
    if request.method == 'POST':
        matpel = request.POST.get('matpel')
        try:
            mata_pelajaran.objects.create(kode_matpel = matpel, tahun_ajaran = tahun_aktif)
            return redirect('adminPage:lihat_soal', matpel)
        except IntegrityError:
            return redirect('adminPage:lihat_soal', matpel)
    return render(request = request,
                  template_name = 'html/pilih_matpel.html',
                  context= {'judul': judul, 'name': name, 'active': 'pilih_soal', 'tahun':tahun_aktif.tahun[-3:]})

def tambahSoal(request, matpel):
    if not request.user.is_authenticated:
        return redirect('adminPage:redirect_site')
    try:
        matpel = mata_pelajaran.objects.get(kode_matpel = matpel)
    except ObjectDoesNotExist:
        messages.error(request, f'Error! Soal Tidak ada')
        return redirect('adminPage:pilih_soal')
    if matpel.kode_matpel[:3] == 'mtk':
        pelajaran = 'Matematika'
    elif matpel.kode_matpel[:3] == 'ind':
        pelajaran = 'Indonesia'
    elif matpel.kode_matpel[:3] == 'ing':
        pelajaran = 'Inggris'
    name = tabel_admin.objects.get(
        username=request.user).get_full_name()
    tahun_aktif = tahun_ajaran_aktif.objects.all()[0].tahun_aktif
    judul = 'Buat Soal untuk Mata Pelajaran ' +pelajaran+ ' Tahun Ajaran ' + \
        tahun_aktif.tahun + '-' + str(int(tahun_aktif.tahun) + 1)
    matpel = mata_pelajaran.objects.get(kode_matpel = matpel)
    if request.method == 'POST':
        try:
            kode = kumpulan_soal.objects.all().filter(kode_matpel = matpel).latest('kode_soal').kode_soal
            if int(kode[-3:]) < 9:
                kode_soal = str(matpel) + '_' + '00' + str(int(kode[-3:]) + 1)
            elif int(kode[-3:]) < 99:
                kode_soal = str(matpel) + '_' + '0' + str(int(kode[-3:]) + 1)
            elif int(kode[-3:]) < 999:
                kode_soal = str(matpel) + '_' + str(int(kode[-3:]) + 1)
        except ObjectDoesNotExist:
            kode_soal = str(matpel) + '_' + '001'
        pertanyaan = request.POST.get('pertanyaan')
        pilihan_1 = request.POST.get('pilihan_1')
        pilihan_2 = request.POST.get('pilihan_2')
        pilihan_3 = request.POST.get('pilihan_3')
        pilihan_4 = request.POST.get('pilihan_4')
        pilihan_5 = request.POST.get('pilihan_5')
        if request.POST.get('jawaban') == '1':
            jawaban = pilihan_1
        elif request.POST.get('jawaban') == '2':
            jawaban = pilihan_2
        elif request.POST.get('jawaban') == '3':
            jawaban = pilihan_3
        elif request.POST.get('jawaban') == '4':
            jawaban = pilihan_4
        elif request.POST.get('jawaban') == '5':
            jawaban = pilihan_5
        if request.POST.get('selesai'):
            kumpulan_soal.objects.create(kode_soal= kode_soal, soal = pertanyaan, pilihan_1 = pilihan_1 , 
                                        pilihan_2 = pilihan_2, pilihan_3 = pilihan_3, 
                                        pilihan_4 = pilihan_4, pilihan_5 = pilihan_5,
                                        jawaban = jawaban, kode_matpel = matpel)
            messages.success(request, 'Soal Berhasil ditambahkan')
            return redirect('adminPage:lihat_soal', matpel.kode_matpel)
        elif request.POST.get('next'):
            kumpulan_soal.objects.create(kode_soal= kode_soal, soal = pertanyaan, pilihan_1 = pilihan_1 , 
                                        pilihan_2 = pilihan_2, pilihan_3 = pilihan_3, 
                                        pilihan_4 = pilihan_4, pilihan_5 = pilihan_5,
                                        jawaban = jawaban, kode_matpel = matpel)
            messages.success(request, 'Soal Berhasil ditambahkan')
    soal = kumpulan_soal.objects.all().filter(kode_matpel = matpel)
    return render(request = request,
                  template_name = 'html/tambah_soal.html',
                  context= {'judul': judul, 'name': name, 'active': 'pilih_soal', 
                            'kumpulan_soal': soal})

def editSoal(request, matpel, kode_soal):
    if not request.user.is_authenticated:
        return redirect('adminPage:redirect_site')
    try:
        matpel = mata_pelajaran.objects.get(kode_matpel = matpel)
        soal = kumpulan_soal.objects.get(kode_soal = kode_soal)
    except ObjectDoesNotExist:
        messages.error(request, f'Error! Soal Tidak ada')
        return redirect('adminPage:pilih_soal')
    if matpel.kode_matpel[:3] == 'mtk':
        pelajaran = 'Matematika'
    elif matpel.kode_matpel[:3] == 'ind':
        pelajaran = 'Indonesia'
    elif matpel.kode_matpel[:3] == 'ing':
        pelajaran = 'Inggris'
    name = tabel_admin.objects.get(
        username=request.user).get_full_name()
    tahun_aktif = tahun_ajaran_aktif.objects.all()[0].tahun_aktif
    judul = 'Edit Soal untuk Mata Pelajaran ' +pelajaran+ ' Tahun Ajaran ' + \
        tahun_aktif.tahun + '-' + str(int(tahun_aktif.tahun) + 1)
    matpel = mata_pelajaran.objects.get(kode_matpel = matpel)
    if request.method == 'POST':
        if request.POST.get('save'):
            pertanyaan = request.POST.get('pertanyaan')
            pilihan_1 = request.POST.get('pilihan_1')
            pilihan_2 = request.POST.get('pilihan_2')
            pilihan_3 = request.POST.get('pilihan_3')
            pilihan_4 = request.POST.get('pilihan_4')
            pilihan_5 = request.POST.get('pilihan_5')
            if request.POST.get('jawaban') == '1':
                jawaban = pilihan_1
            elif request.POST.get('jawaban') == '2':
                jawaban = pilihan_2
            elif request.POST.get('jawaban') == '3':
                jawaban = pilihan_3
            elif request.POST.get('jawaban') == '4':
                jawaban = pilihan_4
            elif request.POST.get('jawaban') == '5':
                jawaban = pilihan_5
            soal.pertanyaan = pertanyaan
            soal.pilihan_1 = pilihan_1
            soal.pilihan_2 = pilihan_2
            soal.pilihan_3 = pilihan_3
            soal.pilihan_4 = pilihan_4
            soal.pilihan_5 = pilihan_5
            soal.jawaban = jawaban
            soal.save()
            messages.success(request, 'Soal Berhasil diEdit')
            return redirect('adminPage:lihat_soal', matpel.kode_matpel)
    return render(request = request,
                  template_name = 'html/edit_soal.html',
                  context= {'judul': judul, 'name': name, 'active': 'pilih_soal', 
                            'kumpulan_soal': soal})

def lihatSoal(request, matpel):
    if not request.user.is_authenticated:
        return redirect('adminPage:redirect_site')
    try:
        matpel = mata_pelajaran.objects.get(kode_matpel = matpel)
    except ObjectDoesNotExist:
        messages.error(request, f'Error! Soal Tidak ada')
        return redirect('adminPage:pilih_soal')
    name = tabel_admin.objects.get(
        username=request.user).get_full_name()
    thn = tahun_ajaran.objects.all()
    thn = tahunakhir(thn)
    tahun_aktif = tahun_ajaran_aktif.objects.all()[0].tahun_aktif
    if matpel.kode_matpel[:3] == 'mtk':
        pelajaran = 'Matematika'
    elif matpel.kode_matpel[:3] == 'ind':
        pelajaran = 'Indonesia'
    elif matpel.kode_matpel[:3] == 'ing':
        pelajaran = 'Inggris'
    judul = 'Soal untuk Mata Pelajaran '+pelajaran+' untuk Tahun Ajaran ' + \
        tahun_aktif.tahun + '-' + str(int(tahun_aktif.tahun) + 1)
    if request.method == 'POST':
        if request.POST.get('hapus'):
            kode = request.POST.get('kode_soal')
            kumpulan_soal.objects.get(kode_soal = kode).delete()
            messages.success(request, f'Soal Berhasil Dihapus')
        elif request.POST.get('ganti'):
            tahun = request.POST.get('ganti')
            judul = 'Soal untuk Mata Pelajaran '+pelajaran+' untuk Tahun Ajaran ' + \
                tahun + '-' + str(int(tahun) + 1)
            kode = matpel.kode_matpel[:5] + tahun[-2:]
            return redirect('adminPage:lihat_soal', kode)
        elif request.POST.get('tambah'):
            return redirect('adminPage:buat_soal', matpel.kode_matpel)
        # elif request.POST.get('edit'):
        #     kode = request.POST.get('kode_soal')
        #     return redirect('adminPage:edit_soal', matpel.kode_matpel, kode)
    soal = kumpulan_soal.objects.all().filter(kode_matpel = matpel)
    return render(request = request,
                  template_name = 'html/lihatSoal.html',
                  context= {'judul': judul, 'name': name, 'active': 'pilih_soal','tahun_ajaran': thn,
                            'kumpulan_soal': soal})