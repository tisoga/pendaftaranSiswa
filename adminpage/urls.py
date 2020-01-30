from django.urls import path
from . import views

app_name = 'adminPage'

urlpatterns = [
    path('', views.redirect_site, name='redirect_site'),
    path('beranda/', views.homepage, name='homepage'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('list_siswa/', views.listsiswa, name='semua_siswa'),
    path('list_siswa_kelas/', views.listsiswakelas, name='siswa_kelas'),
    path('tambah_siswa/', views.tambahsiswa, name='tambah'),
    path('list_siswa/detail/<nis>/', views.detailsiswa, name='detail'),
    path('list_siswa/edit/<nis>/', views.editsiswa, name='edit'),
    path('penentuan_kelas/', views.penentuankelas, name='penentuan'),
    path('set_tahun_ajaran/', views.setTahunAjaran, name='set_tahun'),
    path('tambah_tahun_ajaran/', views.tambahTahunAjaran, name='tambah_tahun'),
    path('lihat_soal/', views.pilihMatpel, name='pilih_soal'),
    path('lihat_soal/<matpel>', views.lihatSoal, name='lihat_soal'),
    path('tambah_soal/<matpel>/new', views.tambahSoal, name='buat_soal'),
    path('tambah_soal/<matpel>/edit/<kode_soal>', views.editSoal, name='edit_soal'),
]
