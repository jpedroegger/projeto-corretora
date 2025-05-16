from django.shortcuts import render, redirect, get_object_or_404
from .forms import SeguradoForm, ApoliceForm, VeiculoForm
from django.contrib import messages
from .models import Apolice, Segurado
from django.db.models import Q, Sum, F, QuerySet
from django.views.generic import ListView, CreateView, DetailView, DeleteView
from typing import Any, Dict, Optional
from django.urls import reverse_lazy


class ApoliceListView(ListView):
    """
    A view that lists all Apolice instances with optional search functionality.
    
    Inherits from Django's ListView to display paginated results. Supports filtering
    by segurado's name or apolice code via URL query parameter (`?search=...`).

    Attributes:
        model: The model class (Apolice).
        template_name: Path to the template rendering the list.
        context_object_name: Variable name for the queryset in the template.
    """
    model = Apolice
    template_name = 'seguros/index.html'
    context_object_name = "apolices"

    def get_queryset(self, **kwargs: Any) -> QuerySet[Apolice]:
        """
        Filters queryset based on URL search parameter.
            
        Returns:
            QuerySet filtered by:
            - segurado__nome (partial match)
            - codigo (partial match)
        """
        queryset = super().get_queryset(**kwargs)
        if search_term := self.request.GET.get('search'):
            queryset = queryset.filter(
                Q(segurado__nome__icontains=search_term) |
                Q(codigo__icontains=search_term)
            )
        return queryset


class ClientListView(ListView):
    """
    A view that lists all Clients instances with optional search functionality.

    Inherits from Django's ListView to display paginated results. Supports filtering
    by clients's name via URL query parameter (`?search=...`).
    """
    model = Segurado
    template_name = "seguros/lista_segurados.html"
    context_object_name = "segurados"
    ordering = ["nome"]

    def get_queryset(self, **kwargs: Any) -> QuerySet[Segurado]:
        """
        Filters queryset based on URL search parameter.
            
        Returns:
            QuerySet filtered by:
            - nome (partial match)
        """
        queryset = super().get_queryset(**kwargs)
        if search_term := self.request.GET.get('search'):
            queryset = queryset.filter(
                nome__icontains=search_term
            ).order_by('nome')
        return queryset


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


class ClientCreateView(CreateView):
    model = Segurado
    form_class = SeguradoForm
    template_name = 'seguros/novo_segurado.html'
    success_url = reverse_lazy('clients_create')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Novo segurado cadastrado.')
        return response


class ClientDetailView(DetailView):
    model = Segurado
    template_name = 'seguros/ver_segurado.html'

    def get_queryset(self):
        return Segurado.objects.prefetch_related('apolices')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        segurado = self.object
        context['apolices'] = segurado.apolices.all()
        return context


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
