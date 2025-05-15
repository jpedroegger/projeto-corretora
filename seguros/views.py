from django.shortcuts import render, redirect, get_object_or_404
from .forms import SeguradoForm, ApoliceForm, VeiculoForm
from django.contrib import messages
from .models import Apolice, Segurado
from django.db.models import Q, Sum, F
from django.views.generic import ListView


class ApoliceListView(ListView):
    model = Apolice
    template_name = 'seguros/index.html'
    context_object_name = "apolices"

    def get_queryset(self, **kwargs):
        queryset = super().get_queryset(**kwargs)
        busca = self.request.GET.get('search')
        if busca:
            queryset = queryset.filter(
                Q(segurado__nome__icontains=busca) |
                Q(codigo__icontains=busca)
            )
        return queryset



def lista_segurados(request):
    
    segurados = Segurado.objects.order_by('nome')
    
    busca = request.GET.get('search')
    if busca:
        segurados = Segurado.objects.filter(nome__icontains=busca)

    return render(request, 'seguros/lista_segurados.html', {'segurados': segurados })


def nova_apolice(request, pk):    
    
    segurado = get_object_or_404(Segurado, id=pk)

    if request.method != 'POST':
        form_veiculo = VeiculoForm()
        form_apolice = ApoliceForm()

        contexto = {
            'form_veiculo': form_veiculo, 
            'form_apolice': form_apolice,
            'segurado': segurado
        }
        return render(request, 'seguros/nova_apolice.html', contexto)
    
    data = request.POST

    form_veiculo = VeiculoForm(data=data)
    form_apolice = ApoliceForm(data=data)
    
    contexto = {
            'form_veiculo': form_veiculo, 
            'form_apolice': form_apolice,
            'segurado': segurado
            }

    if form_veiculo.is_valid() and form_apolice.is_valid():

        veiculo = form_veiculo.save()
        apolice = form_apolice.save(commit=False)
        apolice.veiculo = veiculo
        apolice.segurado = segurado
        apolice.save()
        criado = messages.success(request, 'Cadastro efetuado.')
        return redirect('/', criado)            
    return render(request, 'seguros/nova_apolice.html', contexto)


def novo_segurado(request):    

    if request.method != 'POST':
        segurado_form = SeguradoForm()

        return render(request, 'seguros/novo_segurado.html', {'segurado_form': segurado_form})
    
    segurado_form = SeguradoForm(request.POST)

    if segurado_form.is_valid():
        segurado_form.save()

        criado = messages.success(request, 'Novo segurado cadastrado.')
        return redirect('/lista_segurados', criado)    
    
    return render(request, 'seguros/novo_segurado.html', {'segurado_form': segurado_form})


def ver_apolice(request, pk):

    apolice = get_object_or_404(Apolice, codigo=pk)
    return render(request, 'seguros/ver_apolice.html', {'apolice': apolice})


def ver_segurado(request, pk):

    segurado = get_object_or_404(Segurado, id=pk)
    apolices = segurado.apolice_set.all()       
        
    return render(request, 'seguros/ver_segurado.html', {'segurado': segurado, 'apolices': apolices})


def editar_apolice(request, pk):

    apolice = get_object_or_404(Apolice, codigo=pk)        

    apolice_form = ApoliceForm(instance=apolice)
    veiculo_form = VeiculoForm(instance=apolice.veiculo)    
    
    contexto = {'apolice_form': apolice_form,
                'veiculo_form': veiculo_form,
                'apolice': apolice}   

    if request.method == 'POST':
        data = request.POST

        apolice_form = ApoliceForm(data=data, instance=apolice)

        if apolice_form.is_valid():
            apolice_codigo = apolice_form.cleaned_data['codigo']

            if apolice_codigo != pk:
                erro = messages.error(request, 'Não é possível alterar o código da apólice.')
                return render(request, 'seguros/editar_apolice.html', contexto, erro)

            veiculo_form = VeiculoForm(data=data, instance=apolice.veiculo)
            if veiculo_form.is_valid():

                veiculo = veiculo_form.save()
                apolice = apolice_form.save(commit=False)
                apolice.veiculo = veiculo
                apolice_form.save()

            contexto = {'apolice_form': apolice_form, 'apolice': apolice}

            editado= messages.success(request, 'Apólice editada com sucesso.')
            return render(request, 'seguros/ver_apolice.html', contexto, editado)            
            
    return render(request, 'seguros/editar_apolice.html', contexto)


def editar_segurado(request, pk):

    segurado = get_object_or_404(Segurado, id=pk)        
    segurado_form = SeguradoForm(instance=segurado)                    

    if request.method == 'POST':
        data = request.POST

        segurado_form = SeguradoForm(data=data, instance=segurado)
        if segurado_form.is_valid():
                
            segurado.save()

            contexto = {'segurado_form': segurado_form, 'segurado': segurado}

            editado= messages.success(request, 'Segurado editado com sucesso.')
            return render(request, 'seguros/ver_segurado.html', contexto, editado)            
    
    contexto = {'segurado_form': segurado_form, 'segurado': segurado}   

    return render(request, 'seguros/editar_segurado.html', contexto)


def deletar_segurado(request, pk):

    segurado = get_object_or_404(Segurado, id=pk)    
    segurado.delete()
    excluido = messages.success(request, 'Segurado excluído com sucesso.')
    return redirect('/', excluido)


def deletar_apolice(request, pk):

    apolice = get_object_or_404(Apolice, codigo=pk)    
    apolice.delete()
    excluido = messages.success(request, 'Apólice excluída com sucesso.')
    return redirect('/', excluido)


def relatorio(request):        

    vigencia_mes = request.GET.get('mes')    
    vigencia_ano = request.GET.get('ano')    
    
    if vigencia_mes and vigencia_ano:               
        apolices = Apolice.objects.filter(vigencia__year=vigencia_ano, 
                                          vigencia__month=vigencia_mes).order_by('vigencia')    
        soma = Apolice.objects.filter(vigencia__year=vigencia_ano, vigencia__month=vigencia_mes).annotate(
            total=(F('premio') * F('perc_comissao')) / 100).aggregate(soma_com=Sum('total'))
                    
        return render(request, 'seguros/relatorio.html', {'apolices': apolices, 'soma': soma['soma_com']})

    return render(request, 'seguros/relatorio.html')
