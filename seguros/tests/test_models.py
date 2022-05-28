from django.test import TestCase
from seguros.models import Segurado, Veiculo, Apolice
from django.core.exceptions import ValidationError


class ModelSeguradoTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Segurado.objects.create(
            id= 1,
            nome = 'TesteNome',
            nascimento = '2000-01-01',
            telefone = 'TesteTelefone',            
            cpf = 'TesteCPF',
            endereco = 'TesteEndereço',
            estado_civil = 'NI'
        )        

    def test_str_method_model_segurado(self):
        segurado = Segurado.objects.get(id=1)                
        self.assertEqual(str(segurado), segurado.nome)
    
    def test_absolute_url_model_segurado(self):
        segurado = Segurado.objects.get(id=1)
        self.assertEquals(segurado.get_absolute_url(), '/segurado/1')


class ModelVeiculoTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Veiculo.objects.create(
            id=1,
            modelo = 'TestModelo',
            placa = 'Placa',
            chassi = 'TestChassi',
            ano_modelo = 2000,
            alienado = True
        )        

    def test_str_method_model_veiculo(self):
        veiculo = Veiculo.objects.get(id=1)                
        self.assertEqual(str(veiculo), veiculo.placa)
    
    def test_veiculo_ano_modelo_validator(self):
        veiculo = Veiculo.objects.get(id=1)
        veiculo.full_clean() 
        veiculo.ano_modelo = 3000        
        self.assertRaises(ValidationError, veiculo.full_clean)


class ModelApoliceTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        segurado = Segurado.objects.create(
            nome = 'TesteNome',
            nascimento = '2000-01-01',
            telefone = 'TesteTelefone',            
            cpf = 'TesteCPF',
            endereco = 'TesteEndereço',
            estado_civil = 'NI'
        ) 

        veiculo = Veiculo.objects.create(
            modelo = 'TestModelo1',
            placa = 'Placa1',
            chassi = 'TestChassi1',
            ano_modelo = 2000,
            alienado = False
        )    
        
        Apolice.objects.create(
            segurado = segurado,
            veiculo = veiculo,
            codigo = 'TesteCodigo',
            seguradora = 'BR',
            vigencia = '2000-01-01',
            premio = 2000.00,
            perc_comissao = 10,            
        )    


    def test_str_method_model_apolice(self):
        apolice = Apolice.objects.get(codigo='TesteCodigo') 
        self.assertEqual(str(apolice), apolice.codigo)
        
    def test_absolute_url_model_apolice(self):
        apolice = Apolice.objects.get(codigo='TesteCodigo') 
        self.assertEquals(apolice.get_absolute_url(), f"/apolice/{apolice.codigo}")

    def test_property_total_comissao_apolice(self):
        apolice = Apolice.objects.get(codigo='TesteCodigo')         
        valor = (apolice.premio * apolice.perc_comissao) / 100
        self.assertEqual(apolice.total_comissao, valor)
    
    def test_perc_comissao_modelo_apolice_validator(self):
        apolice = Apolice.objects.get(codigo='TesteCodigo')
        apolice.full_clean() 
        apolice.perc_comissao = 51        
        self.assertRaises(ValidationError, apolice.full_clean)

