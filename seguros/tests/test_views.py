from django.test import TestCase, Client
from seguros.models import Segurado, Veiculo, Apolice
from seguros.forms import ApoliceForm, VeiculoForm, SeguradoForm
from django.urls import reverse
from django.contrib.messages import get_messages


class IndexViewTest(TestCase):

    def setUp(self) -> None:
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
            vigencia = '2022-04-01',
            premio = 2000.00,
            perc_comissao = 10,            
        )
        Apolice.objects.create(
            segurado = segurado,
            veiculo = veiculo,
            codigo = 'TesteBusca',
            seguradora = 'AZ',
            vigencia = '2022-01-01',
            premio = 1000.00,
            perc_comissao = 10,            
        ) 

        self.client = Client()
        self.url = reverse('index')
        return super().setUp()
    
    def test_view_index_render_template_correto(self):
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'seguros/index.html')

    def test_view_index_contexto_correto(self):
        apolice = Apolice.objects.order_by('codigo')
        response = self.client.get(self.url)        
        
        self.assertEqual(response.status_code, 200)        
        self.assertQuerysetEqual(
            response.context['apolices'],
            apolice
        )        

    def test_busca_returns_searched_object(self):            
        response = self.client.get('/?search=busca')
        apolice = Apolice.objects.get(codigo='TesteCodigo') 
        busca_apolice = Apolice.objects.get(codigo='TesteBusca') 

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(apolice, response.context['apolices'])
        self.assertIn(busca_apolice, response.context['apolices'])        


class ListaSeguradosViewTest(TestCase):

    def setUp(self) -> None:
        Segurado.objects.create(
            id=1,
            nome = 'TesteNome',
            nascimento = '2000-01-01',
            telefone = 'TesteTelefone',            
            cpf = 'TesteCPF',
            endereco = 'TesteEndereço',
            estado_civil = 'NI'
        ) 
        Segurado.objects.create(
            id=2,
            nome = 'SeguradoBusca',
            nascimento = '2000-01-01',
            telefone = 'TesteTelefone',            
            cpf = 'TesteCPF',
            endereco = 'TesteEndereço',
            estado_civil = 'NI'
        ) 
        
        self.client = Client()
        self.url = reverse('lista_segurados')
        return super().setUp()

    def test_view_lista_segurados_render_template_correto(self):
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'seguros/lista_segurados.html')

    def test_view_lista_segurados_contexto_correto(self):
        segurado = Segurado.objects.order_by('nome')
        response = self.client.get(self.url)        
        
        self.assertEqual(response.status_code, 200)        
        self.assertQuerysetEqual(
            response.context['segurados'],
            segurado,
        )
        
    def test_busca_returns_searched_object(self):            
        response = self.client.get('/lista_segurados/?search=busca')
        segurado = Segurado.objects.get(id=1) 
        busca_segurado = Segurado.objects.get(id=2) 

        self.assertEqual(response.status_code, 200)
        self.assertIn(busca_segurado, response.context['segurados'])
        self.assertNotIn(segurado, response.context['segurados']) 


class NovaApoliceViewTest(TestCase):

    def setUp(self) -> None:
        self.segurado = Segurado.objects.create(
            id=1,
            nome = 'TesteNome',
            nascimento = '2000-01-01',
            telefone = 'TesteTelefone',            
            cpf = 'TesteCPF',
            endereco = 'TesteEndereço',
            estado_civil = 'NI'
        ) 

        self.valid_data = {
                    'modelo': 'testemodelo',
                    'placa': 'AAA000', 
                    'chassi': 'testechassi',
                    'ano_modelo': 2000,
                    'alienado': True,
                    'codigo': 'codigoteste',
                    'seguradora': 'BR', 
                    'vigencia': '2022-05-22',
                    'premio': 2000.00,
                    'perc_comissao': 10,                                    
                    }

        self.invalid_data = {
                            'codigo': 'codnovoteste',
                            'seguradora': 'BR', 
                            'vigencia': '2022-05-22',
                            'premio': 2000.00,
                            'perc_comissao': 10, 
                            }

        self.client = Client()
        self.url = reverse('nova_apolice', kwargs={"pk": self.segurado.id})
        return super().setUp()
    
    def test_get_method_render_correct_template(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'seguros/nova_apolice.html')
        
    def test_segurado_in_context_get_method(self):
        segurado = Segurado.objects.get(id=1)
        response = self.client.get(self.url)

        self.assertEqual(segurado, response.context['segurado'])

    def test_valid_form_apolice_and_veiculo_are_saved_in_post_request(self):
        self.client.post(self.url, self.valid_data)

        self.assertEqual(Apolice.objects.count(), 1)    
        self.assertEqual(Veiculo.objects.count(), 1)

    def test_apolice_instance_has_correct_foreign_keys(self):   
        segurado = Segurado.objects.get(id=1)
        self.client.post(self.url, self.valid_data)
        veiculo = Veiculo.objects.first()
        nova_apolice = Apolice.objects.first()        
             
        self.assertEqual(nova_apolice.segurado, segurado)
        self.assertEqual(nova_apolice.veiculo, veiculo)
    
    def test_post_method_redirects_correctly_after_form_is_valid(self):
        response = self.client.post(self.url, self.valid_data)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/")
    
    def test_post_method_render_correct_template_when_form_is_invalid(self):
        response = self.client.post(self.url, self.invalid_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "seguros/nova_apolice.html")

    def test_success_message_is_shown_to_user_when_forms_are_valid(self):
        response = self.client.post(self.url, self.valid_data)
        message = list(get_messages(response.wsgi_request))

        self.assertEqual(len(message), 1)
        self.assertEqual(str(message[0]), 'Cadastro efetuado.')        


class NovoSeguradoViewTest(TestCase):

    def setUp(self) -> None:
        self.data = {            
                    'nome': 'TesteNome',
                    'nascimento': '2000-01-01',
                    'telefone': 'TesteTelefone',            
                    'cpf': 'TesteCPF',
                    'endereco': 'TesteEndereço',
                    'estado_civil': 'NI'
                    }
        self.invalid_data = {            
                            'nome': 'TesteNome',
                            'nascimento': '2000-01-01',
                            }
        self.client = Client()
        self.url = reverse('novo_segurado')                
        return super().setUp()

    def test_get_method_render_correct_template(self):
        response = self.client.get(self.url)        

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'seguros/novo_segurado.html')

    def test_valid_form_segurado_is_saved_in_post_request(self):
        self.client.post(self.url, data=self.data)
        segurado = Segurado.objects.first()

        self.assertEqual(Segurado.objects.count(), 1)
        self.assertEqual(segurado.nome, 'TesteNome')
        
    def test_post_method_redirects_correctly_after_form_is_valid(self):
        response = self.client.post(self.url, self.data)
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/lista_segurados", target_status_code=301)
    
    def test_post_method_render_correct_template_when_segurado_form_is_invalid(self):
        response = self.client.post(self.url, data=self.invalid_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "seguros/novo_segurado.html")

    def test_success_message_is_shown_to_user_when_segurado_form_is_valid(self):
        response = self.client.post(self.url, self.data)
        message = list(get_messages(response.wsgi_request))

        self.assertEqual(len(message), 1)
        self.assertEqual(str(message[0]), 'Novo segurado cadastrado.')


class VerApoliceViewTest(TestCase):

    def setUp(self) -> None:
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
        
        apolice = Apolice.objects.create(
            segurado = segurado,
            veiculo = veiculo,
            codigo = 'TesteCodigo',
            seguradora = 'BR',
            vigencia = '2000-01-01',
            premio = 2000.00,
            perc_comissao = 10,            
        )
        self.client = Client()
        self.url = reverse('ver_apolice', kwargs={'pk': apolice.codigo})
        return super().setUp()

    def test_apolice_get_render_correct_template(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'seguros/ver_apolice.html')
    
    def test_apolice_get_invalid_object(self):
        response = self.client.get(reverse('ver_apolice',kwargs={'pk': 'codigoinvalido'}))

        self.assertEqual(response.status_code, 404)

    def test_apolice_in_context(self):
        response = self.client.get(self.url)
        apolice = Apolice.objects.get(codigo='TesteCodigo')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(apolice, response.context['apolice'])


class VerSeguradoViewTest(TestCase):
    
    def setUp(self) -> None:
        segurado = Segurado.objects.create(
            id= 1,
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
        self.client = Client()
        self.url = reverse('ver_segurado', kwargs={'pk': segurado.id})
        return super().setUp()

    def test_segurado_get_render_correct_template(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'seguros/ver_segurado.html')
    
    def test_segurado_get_invalid_object(self):
        response = self.client.get(reverse('ver_segurado', kwargs={'pk': 2}))

        self.assertEqual(response.status_code, 404)

    def test_segurado_in_context(self):
        response = self.client.get(self.url)
        segurado = Segurado.objects.get(id=1)
        apolice = Apolice.objects.get(codigo='TesteCodigo')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(segurado, response.context['segurado'])
        self.assertQuerysetEqual(
            response.context['apolices'],
            [apolice],
        )
    
    def test_apolices_in_context(self):
        response = self.client.get(self.url)
        apolice = Apolice.objects.get(codigo='TesteCodigo')

        self.assertQuerysetEqual(
            response.context['apolices'],
            [apolice],
        )


class EditarApoliceViewTest(TestCase):

    def setUp(self) -> None:
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
        
        self.apolice = Apolice.objects.create(
            segurado = segurado,
            veiculo = veiculo,
            codigo = 'TesteCodigo',
            seguradora = 'BR',
            vigencia = '2000-01-01',
            premio = 2000.00,
            perc_comissao = 10,            
        ) 

        self.valid_data = {
                    'modelo': 'modeloeditado',
                    'placa': 'EDI000', 
                    'chassi': 'chassieditado',
                    'ano_modelo': 2021,
                    'alienado': False,
                    'codigo': 'TesteCodigo',
                    'seguradora': 'AZ', 
                    'vigencia': '2022-05-22',
                    'premio': 2000.00,
                    'perc_comissao': 15,                                    
                    }

        self.invalid_data = {
                            'codigo': 'invalidcod',
                            'seguradora': 'BR', 
                            'vigencia': '2022-05-22',
                            'premio': 2000.00,
                            'perc_comissao': 10, 
                            }

        self.client = Client()
        self.url = reverse('editar_apolice', kwargs={"pk": self.apolice.codigo})
        return super().setUp()
    
    def test_get_method_render_correct_template(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'seguros/editar_apolice.html')
      
    def test_apolice_in_context_get_method(self):
        apolice = Apolice.objects.get(codigo=self.apolice.codigo)
        response = self.client.get(self.url)

        self.assertEqual(apolice, response.context['apolice'])
  
    def test_forms_instances_in_context_get_method(self):
        response = self.client.get(self.url)

        self.assertIn('apolice_form', response.context)
        self.assertIn('veiculo_form', response.context)

    def test_if_view_has_edited_objects_and_not_created_in_post_request(self):
        response = self.client.post(self.url, data=self.valid_data)
        #print(response.content.decode())
        #print(apolice.veiculo.modelo)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Apolice.objects.count(), 1)    
        self.assertEqual(Veiculo.objects.count(), 1)

    def test_new_data_in_objects_match_after_edited(self):
        self.client.post(self.url, data=self.valid_data)
        apolice = Apolice.objects.first()

        self.assertEqual(apolice.veiculo.modelo, 'modeloeditado')
        self.assertEqual(apolice.seguradora, 'AZ')

    def test_post_method_with_invalid_data(self):
        self.client.post(self.url, data=self.invalid_data)
        apolice = Apolice.objects.first()

        self.assertEqual(apolice.veiculo.modelo, 'TestModelo1')
        self.assertEqual(apolice.seguradora, 'BR')

    def test_success_message_is_shown_to_user_when_forms_are_valid(self):
        response = self.client.post(self.url, self.valid_data)
        message = list(get_messages(response.wsgi_request))

        self.assertEqual(len(message), 1)
        self.assertEqual(str(message[0]), 'Apólice editada com sucesso.')        


class EditarSeguradoViewTest(TestCase):

    def setUp(self) -> None:

        self.segurado = Segurado.objects.create(
            nome = 'TesteNome',
            nascimento = '2000-01-01',
            telefone = 'TesteTelefone',            
            cpf = 'TesteCPF',
            endereco = 'TesteEndereço',
            estado_civil = 'NI'
        ) 

        self.valid_data = {            
                    'nome': 'NomeEditado',
                    'nascimento': '2000-01-01',
                    'telefone': 'TelefoneEdit',            
                    'cpf': 'NovoCPF',
                    'endereco': 'TesteEndereço',
                    'estado_civil': 'NI'
                    }
        self.invalid_data = {            
                            'nome': 'TesteInvalidNome',
                            'nascimento': '2000-01-01',
                            }
        self.client = Client()
        self.url = reverse('editar_segurado', kwargs={'pk': self.segurado.id})    
        return super().setUp()

    def test_get_method_render_correct_template(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'seguros/editar_segurado.html')
      
    def test_segurado_in_context_get_method(self):
        segurado = Segurado.objects.get(id=self.segurado.id)
        response = self.client.get(self.url)

        self.assertEqual(segurado, response.context['segurado'])
  
    def test_form_segurado_in_context_get_method(self):
        response = self.client.get(self.url)

        self.assertIn('segurado_form', response.context)        

    def test_if_view_has_edited_object_and_not_created(self):
        response = self.client.post(self.url, data=self.valid_data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Segurado.objects.count(), 1)            

    def test_new_data_in_segurado_match_after_edited(self):
        self.client.post(self.url, data=self.valid_data)
        segurado = Segurado.objects.first()

        self.assertEqual(segurado.nome, 'NomeEditado')        

    def test_post_method_with_invalid_data(self):
        self.client.post(self.url, data=self.invalid_data)
        segurado = Segurado.objects.first()

        self.assertEqual(segurado.nome, 'TesteNome')        

    def test_success_message_is_shown_to_user_when_forms_are_valid(self):
        response = self.client.post(self.url, self.valid_data)
        message = list(get_messages(response.wsgi_request))

        self.assertEqual(len(message), 1)
        self.assertEqual(str(message[0]), 'Segurado editado com sucesso.')        


class DeletarSeguradoViewTest(TestCase):
    
    def setUp(self):

        self.segurado = Segurado.objects.create(
            id= 1,
            nome = 'TesteNome',
            nascimento = '2000-01-01',
            telefone = 'TesteTelefone',            
            cpf = 'TesteCPF',
            endereco = 'TesteEndereço',
            estado_civil = 'NI'
        )

        self.url = reverse('deletar_segurado', kwargs={'pk': self.segurado.id})
        self.client = Client()
        return super().setUp()

    def test_if_view_redirects_correctly(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')
    
    def test_if_view_gets_404_when_id_is_invalid(self):
        response = self.client.get(reverse('deletar_segurado', kwargs={'pk': 2}))

        self.assertEqual(response.status_code, 404)        
    
    def test_if_segurado_was_deleted(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Segurado.objects.count(), 0)        
    
    def test_success_message_is_shown_to_user_when_segurado_is_deleted(self):
        response = self.client.post(self.url)
        message = list(get_messages(response.wsgi_request))

        self.assertEqual(len(message), 1)
        self.assertEqual(str(message[0]), 'Segurado excluído com sucesso.')        


class DeletarApoliceViewTest(TestCase):
    
    def setUp(self):

        segurado = Segurado.objects.create(
            id= 1,
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
        self.apolice = Apolice.objects.create(
            segurado = segurado,
            veiculo = veiculo,
            codigo = 'TesteCodigo',
            seguradora = 'BR',
            vigencia = '2000-01-01',
            premio = 2000.00,
            perc_comissao = 10,            
        )

        self.url = reverse('deletar_apolice', kwargs={'pk': self.apolice.codigo})
        self.client = Client()
        return super().setUp()

    def test_if_view_redirects_correctly(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')
    
    def test_if_view_gets_404_when_id_is_invalid(self):
        response = self.client.get(reverse('deletar_apolice', kwargs={'pk': 'naoencontrado'}))

        self.assertEqual(response.status_code, 404)        
    
    def test_if_segurado_was_deleted(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Apolice.objects.count(), 0)        
    
    def test_success_message_is_shown_to_user_when_segurado_is_deleted(self):
        response = self.client.post(self.url)
        message = list(get_messages(response.wsgi_request))

        self.assertEqual(len(message), 1)
        self.assertEqual(str(message[0]), 'Apólice excluída com sucesso.')        


class RelatorioViewTest(TestCase):
    
    def setUp(self) -> None:
        segurado = Segurado.objects.create(
            id= 1,
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
        self.apolice_1 = Apolice.objects.create(
            segurado = segurado,
            veiculo = veiculo,
            codigo = 'TesteCodigo',
            seguradora = 'BR',
            vigencia = '2022-05-01',
            premio = 2000.00,
            perc_comissao = 10,            
        )           
        self.apolice_2 = Apolice.objects.create(
            segurado = segurado,
            veiculo = veiculo,
            codigo = 'TesteCodigo2',
            seguradora = 'AZ',
            vigencia = '2022-05-01',
            premio = 1000.00,
            perc_comissao = 15,            
        )
        
        self.url = reverse('relatorio')

        return super().setUp()
    
    def test_view_render_correct_template(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'seguros/relatorio.html')

    def test_view_render_correct_template_with_vigencia_ano_mes(self):
        response = self.client.get('/relatorio?mes=05&ano=2022')

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'seguros/relatorio.html')

    def test_view_has_context_with_vigencia_ano_mes(self):
        response = self.client.get('/relatorio?mes=05&ano=2022')
        
        self.assertIn('apolices', response.context)
        self.assertIn('soma', response.context)        
     
    def test_view_soma_objects_correctly(self):
        response = self.client.get('/relatorio?mes=05&ano=2022')

        self.assertEqual(response.context['soma'], 350.00)
 