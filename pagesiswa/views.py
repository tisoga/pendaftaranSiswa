from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import check_password, make_password
from adminpage.models import tahun_ajaran_aktif, tabel_siswa, kumpulan_soal, mata_pelajaran, save_jawaban
import random
from faker import Faker
# Create your views here.

def redirect_site(request):
    if 'siswa' in request.session:
        return redirect('pagesiswa:profile')
    else:
        return redirect('pagesiswa:login')

def login_request(request):
    nis = False
    if request.method == 'GET':
        if request.GET.get('nis'):
            nis = request.GET.get('nis')
    if request.method == 'POST':
        if request.POST.get('admin'):
            user = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=user, password=password)
            if user:
                request.session['user'] = user.username
                login(request, user)
                return redirect('adminPage:homepage')
            else:
                messages.error(request, f'Username atau password salah')
        elif request.POST.get('siswa'):
            nis = request.POST.get('nis')
            password = request.POST.get('password')
            try:
                user = tabel_siswa.objects.get(nis = nis)
                if user.nis == nis and check_password(password, user.password):
                    request.session['siswa'] = user.nis
                    return redirect('pagesiswa:profile')
                else:
                    nis = ''
                    messages.error(request, f'Periksa Kembali NIS dan Password anda')    
            except ObjectDoesNotExist:
                nis = ''
                messages.error(request, f'Periksa Kembali NIS dan password anda')
    return render(request=request,
                  template_name='html/login.html',
                  context = {'nis': nis})


def logout_request(request):
    logout(request)
    messages.success(request, f'Logout Berhasil')
    return redirect('pagesiswa:login')


def register(request):
    tahun_aktif = tahun_ajaran_aktif.objects.all()[0]
    if request.method == 'POST':
        nis = tahun_aktif.tahun_aktif.tahun[-2:] + \
            str(int(tahun_aktif.tahun_aktif.tahun[-2:]) + 1) + \
            str(random.randint(1000, 9999))
        nama = request.POST.get('nama')
        alamat = request.POST.get('alamat')
        tempat = request.POST.get('tempat')
        tanggal = request.POST.get('tanggal')
        password = make_password(tanggal)
        gender = request.POST.get('jk')
        foto = request.FILES.get('foto')
        tabel_siswa.objects.create(
            nis=nis, nama=nama, password=password, foto=foto,
            jenis_kelamin=gender, alamat=alamat, tempat_lahir=tempat,
            tanggal_lahir=tanggal, tahun_ajaran=tahun_aktif.tahun_aktif)
        response = redirect('pagesiswa:login')
        response['location'] += '?nis=' + nis
        return response
    return render(request=request,
                  template_name='html/register_siswa.html',
                  context={'tahun_ajaran': tahun_aktif})

def profile_siswa(request):
    if 'siswa' not in request.session:
        messages.error(request, f'Silahkan Login Terlebih Dahulu')
        return redirect('pagesiswa:login')
    nis = request.session['siswa']
    user = tabel_siswa.objects.get(nis = nis)
    matpel = {'tahun': user.tahun_ajaran.tahun[-2:]}
    if request.GET.get('selesai'):
        nama = request.GET.get('selesai')
        nilai = request.GET.get('nilai')
        matpel.update({'nama': nama, 'nilai': nilai})
    if request.method == 'POST':
        request.session['ujian'] = request.POST.get('matpel')
        return redirect('pagesiswa:ujian')

    return render(request = request,
                  template_name = 'html/profile_siswa.html',
                  context={'user': user, 'matpel': matpel})

def ujian(request):
    if 'ujian' not in request.session:
        return redirect('pagesiswa:profile')
    matpel = request.session['ujian']
    matpel = mata_pelajaran.objects.get(kode_matpel = matpel)
    start = True
    no = 0
    nis = request.session['siswa']
    user = tabel_siswa.objects.get(nis = nis)
    soal = kumpulan_soal.objects.all().filter(kode_matpel = matpel)
    jawab = save_jawaban.objects.all().filter(nis = nis)
    try:
        # jawaban = save_jawaban.objects.all().filter(kode_soal = soal[no]).filter(nis = user)
        # jawaban = jawaban[0]
        jawaban = save_jawaban.objects.get(kode_soal = soal[no], nis = user)
    except ObjectDoesNotExist:
        jawaban = ""
    jumlah_soal = len(soal)
    if request.method == 'POST':
        start = False
        # print(request.POST)
        if request.POST.get('next'):
            no = int(request.POST.get('no_soal'))
            no += 1
            if no == jumlah_soal:
                no -= 1
            try:
                jawaban = save_jawaban.objects.get(kode_soal = soal[no], nis = user)
            except ObjectDoesNotExist:
                jawaban = ""
        elif request.POST.get('prev'):
            no = int(request.POST.get('no_soal'))
            no -= 1
            if no == -1:
                no = 0
            try:
                jawaban = save_jawaban.objects.get(kode_soal = soal[no], nis = user)
            except ObjectDoesNotExist:
                jawaban = ""
        elif request.POST.get('review'):
            if len(soal) == len(jawab):
                return redirect('pagesiswa:review')
            else:
                messages.error(request, f'Soal Belum dikerjakan semua, harap kerjakan semua soal terlebih dahulu')
                no = int(request.POST.get('no_soal'))
        elif request.POST.get('navigate'):
            no = int(request.POST.get('navigate')) - 1
            try:
                jawaban = save_jawaban.objects.get(kode_soal = soal[no], nis = user)
            except ObjectDoesNotExist:
                jawaban = ""
        elif request.POST.get('soal'):
            no = int(request.POST.get('no_soal'))
            kode_soal = kumpulan_soal.objects.get(kode_soal = request.POST.get('kode_soal'))
            jawaban_soal = request.POST.get('soal')
            try:
                update_jawaban = save_jawaban.objects.get(kode_soal = kode_soal, nis = user)
                update_jawaban.jawaban_pilih = jawaban_soal
                update_jawaban.save()
            except ObjectDoesNotExist:
                save_jawaban.objects.create(kode_soal = kode_soal, nis = user, jawaban_pilih = jawaban_soal)
            try:
                jawaban = save_jawaban.objects.get(kode_soal = soal[no], nis = user)
            except ObjectDoesNotExist:
                jawaban = ""
    return render(request = request,
                  template_name = 'html/test.html',
                  context={'user': user, 'soal': soal, 'no': no, 'start': start, 'jumlah': jumlah_soal-1,
                            'jawaban': jawaban, 'all_soal': range(jumlah_soal)})

def review(request):
    nis = request.session['siswa']
    user = tabel_siswa.objects.get(nis = nis)
    if 'ujian' not in request.session:
        return redirect('pagesiswa:profile')
    matpel = request.session['ujian']
    matpel = mata_pelajaran.objects.get(kode_matpel = matpel)
    soal = kumpulan_soal.objects.all().filter(kode_matpel = matpel)
    jawaban = save_jawaban.objects.all().filter(nis = user)
    jumlah_soal = len(soal)
    if request.method == 'POST':
        nilai = 0
        persoal = 100 / jumlah_soal
        if request.POST.get('selesai'):
            for x in soal:
                for y in jawaban:
                    if x.kode_soal == y.kode_soal.kode_soal:
                        if x.jawaban == y.jawaban_pilih:
                            nilai += persoal
                        else:
                            continue
                    else:
                        continue
            nilai = round(nilai, 2)
            pelajaran = matpel.kode_matpel[0:3]
            if pelajaran == 'mtk':
                user.nilai_mtk = nilai
                pelajaran = 'matematika'
                user.save()
            elif pelajaran == 'ind':
                user.nilai_indonesia = nilai
                pelajaran = 'Bahasa Indonesia'
                user.save()
            elif pelajaran == 'ing':
                user.nilai_inggris = nilai
                pelajaran = 'Bahasa Inggris'
                user.save()
            jawaban.delete()
            del request.session['ujian']
            response = redirect('pagesiswa:profile')
            response['location'] += '?selesai=' + pelajaran + '&nilai=' + str(nilai)
            return response
    return render(request = request,
                  template_name = 'html/review_jawaban.html',
                  context={'user': user, 'soal': soal, 'jawaban': jawaban, 'jumlah': jumlah_soal})

def faker(request):
    tahun_aktif = tahun_ajaran_aktif.objects.all()[0]
    if request.method == 'POST':
        jumlah = request.POST.get('jumlah')
        fake = Faker(['id_ID'])
        gd = ['Laki-Laki','Perempuan']
        # kls = ['A','B','C','D']
        for _ in range(int(jumlah)):
            nis = tahun_aktif.tahun_aktif.tahun[-2:] + \
                str(int(tahun_aktif.tahun_aktif.tahun[-2:]) + 1) + \
                str(random.randint(1000, 9999))
            nama = fake.name()
            alamat = fake.address()
            tempat = fake.city()
            tanggal = fake.date()
            password = make_password(tanggal)
            kelas = ""
            gender = random.choice(gd)
            mtk = random.randint(0, 100)
            indo = random.randint(0, 100)
            inggris = random.randint(0, 100)
            tabel_siswa.objects.create(
                nis=nis, nama=nama, password = password, jenis_kelamin=gender, alamat=alamat, tempat_lahir=tempat,
                nilai_mtk=mtk, nilai_indonesia=indo, nilai_inggris=inggris, tanggal_lahir=tanggal,
                tahun_ajaran = tahun_aktif.tahun_aktif, kelas = kelas)
        messages.success(request, f'Data Berhasil Ditambahkan')
        return redirect('adminPage:homepage')
    return render(request = request,
                  template_name = 'html/faker.html')