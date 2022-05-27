from .models import Apolice, Segurado, Veiculo
from django import forms


class SeguradoForm(forms.ModelForm):
    class Meta:
        model = Segurado 
        fields = '__all__'
    

class ApoliceForm(forms.ModelForm):
    class Meta:
        model = Apolice 
        fields = ('codigo', 'seguradora', 'vigencia', 'premio', 'perc_comissao')
    

class VeiculoForm(forms.ModelForm):
    class Meta:
        model = Veiculo 
        fields = ('modelo', 'placa', 'chassi', 'ano_modelo', 'alienado')

    
