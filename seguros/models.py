from django.db import models
from django.urls import reverse
from django.core.validators import MaxValueValidator


SEGURADORAS = [
    ('BR', 'Bradesco'),
    ('PS', 'Porto Seguro'),
    ('AZ', 'Azul Seguros'),
    ('MA', 'Mapfre'),
    ('SA', 'Santander'),
    ('TM', 'Tokio Marine'),
    ('AL', 'Allianz'),
]

ESTADO_CIVIL = [
    ('SL', 'Solteiro'),
    ('CS', 'Casado'),
    ('DV', 'Divorciado'),
    ('UE', 'União Estável'),
    ('NI', 'Não informado'),
]


class Segurado(models.Model):
    nome = models.CharField(max_length=50)
    nascimento = models.DateField('Data de Nascimento')
    telefone = models.CharField(max_length=14)
    email = models.EmailField('E-mail', max_length=75, null=True, blank=True)
    cpf = models.CharField('CPF', max_length=12)
    endereco = models.CharField('Endereço', max_length=50)
    estado_civil = models.CharField(max_length=2, choices=ESTADO_CIVIL, default='NI')

    def __str__(self):
        return self.nome

    def get_absolute_url(self):
        return reverse("ver_segurado", kwargs={"pk": self.pk})    


class Veiculo(models.Model):
    modelo = models.CharField(max_length=50)
    placa = models.CharField(max_length=7)
    chassi = models.CharField(max_length=17)
    ano_modelo = models.PositiveIntegerField(validators=[MaxValueValidator(2099)])
    alienado = models.BooleanField(null=True, default=False)

    def __str__(self):
        return self.placa


class Apolice(models.Model):
    segurado = models.ForeignKey(Segurado, on_delete=models.CASCADE)
    veiculo = models.ForeignKey(Veiculo, on_delete=models.CASCADE)
    codigo = models.CharField('Código', max_length=25, primary_key=True)
    seguradora = models.CharField(max_length=2, choices=SEGURADORAS)
    vigencia = models.DateField('Vigência')
    premio = models.DecimalField('Prêmio Líquido', max_digits=8, decimal_places=2)
    perc_comissao = models.PositiveIntegerField('Percentual Comissão', validators=[MaxValueValidator(50)])    

    def __str__(self):
        return f'{self.codigo}'
        
    def get_absolute_url(self):
        return reverse("ver_apolice", kwargs={"pk": self.codigo})    

    @property
    def total_comissao(self):
        valor = (self.premio * self.perc_comissao) / 100
        return valor
