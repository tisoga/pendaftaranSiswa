from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
# Create your models here.


def images_directory_path(instance, filename):
    return 'images/{0}/{1}'.format(instance.tahun_ajaran.tahun, "foto_"+instance.nis+".jpg")


class CustomUserManager(BaseUserManager):
    def create_user(self, username, password, first_name, last_name):
        if not username:
            raise ValueError(_('Silahkan Masukan Username'))
        user = self.model(username=username,
                          first_name=first_name,
                          last_name=last_name)
        user.set_password(password)
        user.save()
        return user


class tabel_admin(AbstractUser):
    email = None
    is_superuser = None
    is_staff = None
    date_joined = None

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    class Meta:
        db_table = 'tabel_admin'

    def __str__(self):
        return self.username


class tahun_ajaran(models.Model):
    tahun = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'tabel_tahun_ajaran'

    def __str__(self):
        return self.tahun


class tabel_siswa(models.Model):
    nis = models.CharField(max_length=255, primary_key=True, unique=True)
    nama = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    foto = models.ImageField(upload_to=images_directory_path)
    jenis_kelamin = models.CharField(max_length=255)
    alamat = models.TextField()
    tempat_lahir = models.CharField(max_length=255)
    tanggal_lahir = models.DateField()
    nilai_mtk = models.FloatField(blank=True, null=True)
    nilai_inggris = models.FloatField(blank=True, null=True)
    nilai_indonesia = models.FloatField(blank=True, null=True)
    kelas = models.CharField(max_length=10, blank=True, null=True)
    tahun_ajaran = models.ForeignKey(tahun_ajaran, on_delete=models.PROTECT)

    class Meta:
        db_table = 'tabel_siswa'

    def __str__(self):
        return self.nis


class tahun_ajaran_aktif(models.Model):
    tahun_aktif = models.ForeignKey(tahun_ajaran, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'tabel_tahun_ajaran_aktif'


class mata_pelajaran(models.Model):
    kode_matpel = models.CharField(
        max_length=255, primary_key=True, unique=True)
    tahun_ajaran = models.ForeignKey(tahun_ajaran, on_delete=models.PROTECT)

    class Meta:
        db_table = 'tabel_mata_pelajaran'

    def __str__(self):
        return self.kode_matpel


class kumpulan_soal(models.Model):
    kode_matpel = models.ForeignKey(mata_pelajaran, on_delete=models.PROTECT)
    kode_soal = models.CharField(max_length=255, primary_key=True, unique=True)
    soal = models.TextField()
    pilihan_1 = models.CharField(max_length=255)
    pilihan_2 = models.CharField(max_length=255)
    pilihan_3 = models.CharField(max_length=255)
    pilihan_4 = models.CharField(max_length=255)
    pilihan_5 = models.CharField(max_length=255)
    jawaban = models.CharField(max_length=255)

    class Meta:
        db_table = 'tabel_kumpulan_soal'
        
    def __str__(self):
        return self.kode_soal

class save_jawaban(models.Model):
    kode_soal = models.ForeignKey(kumpulan_soal, on_delete = models.PROTECT)
    nis = models.ForeignKey(tabel_siswa, on_delete=models.PROTECT)
    jawaban_pilih = models.CharField(max_length=255)

    class Meta:
        db_table = 'tabel_save_jawaban'

    def __str__(self):
        return self.jawaban_pilih