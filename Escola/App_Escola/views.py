from django.shortcuts import get_object_or_404, redirect, render
from hashlib import sha256
from .models import Professor, Turma, Atividade
from django.db import connection, transaction
from django.contrib import messages
from django.http import HttpResponse
import os
import mimetypes
import openpyxl

def initial_population():
    print("vou pular")
    
    cursor = connection.cursor()
    
    senha = "123456"
    senha_armazenar = sha256(senha.encode()).hexdigest()
    
    insert_sql_professor = "INSERT INTO App_Escola_professor (nome,email,senha) VALUES"
    insert_sql_professor = insert_sql_professor + "('Prof. Barak Obama', 'barak.obama@gmail.com', '" + senha_armazenar + "' ),"
    insert_sql_professor = insert_sql_professor + "('Profa. Angela Merkel', 'angela.merkel@gmail.com', '" + senha_armazenar + "' ),"
    insert_sql_professor = insert_sql_professor + "('Prof. Xi Jinping', 'xi.jinping@gmail.com', '" + senha_armazenar + "' )"
    
    cursor.execute(insert_sql_professor)
    transaction.atomic() #seria como um commit para o insert e update
    
    #tabela Turma
    insert_sql_turma = "INSERT INTO App_Escola_turma(nome_turma,id_professor_id) VALUES"
    insert_sql_turma = insert_sql_turma + "('1o semestre - Desenvolvimento de Sistemas', 1),"
    insert_sql_turma = insert_sql_turma + "('2o semestre - Desenvolvimento de Sistemas', 2),"
    insert_sql_turma = insert_sql_turma + "('3o semestre - Desenvolvimento de Sistemas', 3)"
    
    cursor.execute(insert_sql_turma)
    transaction.atomic()
    
    #tabela de atividade
    insert_sql_atividade = "INSERT INTO App_Escola_atividade (nome_atividade,id_turma_id) VALUES"
    insert_sql_atividade = insert_sql_atividade + "('Apresentar Fundamentos de programação', 1),"
    insert_sql_atividade = insert_sql_atividade + "('Apresentar FrameWork Django', 2),"
    insert_sql_atividade = insert_sql_atividade + "('Apresentar conceito de Gerenciamento de Projetos', 3)"
    
    cursor.execute(insert_sql_atividade)
    transaction.atomic()
    
    print("funfa")
    

def abre_index(request):
    # return render(request, 'index.html')
    dado_pesquisa = 'Obama'
    
    verifica_populado = Professor.objects.filter(nome__icontains = dado_pesquisa)
    
    if len(verifica_populado) == 0:
        print("não esta populado")
        initial_population()
    else:
        print("Achei o Obama", verifica_populado)
    
    usuario_logado = request.user.username
    return render(request, 'index.html', {'usuario_logado': usuario_logado})
        

def enviar_login(request):
    
    if (request.method == 'POST'):
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        senha_criptografada = sha256(senha.encode()).hexdigest()
        dados_professor = Professor.objects.filter(email=email).values("nome", "senha", "id")
        print(dados_professor)
        print("dados do professor", dados_professor)
        
        if dados_professor:
            senha = dados_professor[0]
            senha = senha['senha']
            usuario_logado = dados_professor[0]
            usuario_logado = usuario_logado['nome']
            if (senha == senha_criptografada):
                #se logou corretamente, traz as turmas do professor
                #para isso estanciamos o model turmas do professor
                id_logado = dados_professor[0]
                id_logado = id_logado['id']
                turmas_do_professor = Turma.objects.filter(id_professor=id_logado)
                print("Turma do professor", turmas_do_professor)
                return render(request, 'Cons_Turma_Lista.html', {'usuario_logado':usuario_logado,
                                                                 'turmas_do_professor': turmas_do_professor,
                                                                 "id_logado": id_logado})
            else:
                messages.info(request, 'Usuario ou senha incorretos, Tente noamente')
                return render(request, 'login.html')
            
    messages.info(request, "Olá "  + email + ", seja bem vindo! Percebmos que voce é novo aqui. Complete o seu cadastro")
    return render(request, 'cadastro.html',{'login':email})

def confirmar_cadastro(request):
    if(request.method == 'POST'):
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        senha_criptografada = sha256(senha.encode()).hexdigest()
        
        grava_professor = Professor(
            nome=nome,
            email=email,
            senha=senha_criptografada
        )
        grava_professor.save()
        
        mensagem = "Olá Professor" + nome + "seja bem vindo"
        return HttpResponse(mensagem)

def cad_turma(request, id_professor):
    usuario_logado = Professor.objects.filter(id=id_professor).values("nome", "id")
    usuario_logado = usuario_logado[0]
    usuario_logado = usuario_logado['nome']
    return render(request, 'Cad_turma.html', {'usuario_logado': usuario_logado, 'id_logado':id_professor})

def salvar_turma_nova(request):
    if (request.method == 'POST'):
        nome_turma = request.POST.get('nome_turma')
        id_professor = request.POST.get('id_professor')
        professor = Professor.objects.get(id=id_professor)
        grava_turma =Turma(
            nome_turma = nome_turma,
            id_professor = professor
        )
        
        grava_turma.save()
        messages.info(request, 'Turma' + nome_turma + 'cadastrado com sucesso.')
        return redirect('lista_turma', id_professor=id_professor)

def lista_turma(request, id_professor):
    dados_professor = Professor.objects.filter(id=id_professor).values("nome", "id")
    usuario_logado = dados_professor[0]
    usuario_logado = usuario_logado['nome']
    id_logado = dados_professor[0]
    id_logado = id_logado['id']
    turmas_do_professor = Turma.objects.filter(id_professor=id_logado)
    return render(request, 'Cons_Turma_Lista.html',
                  {'usuario_logado':usuario_logado, 'turmas_do_professor':turmas_do_professor,
                   'id_logado':id_logado})
    
# def ver_atividades(request):
#     id_turma = request.GET('id')
#     dados_turma = Turma.objects.filter(id=id_turma).values("nome_turma", "id")
#     turma_logada = dados_turma[0]
#     turma_logada = turma_logada['nome_turma']
#     id_turma_logado = dados_turma[0]
#     id_turma_logado = id_turma_logado['id']
#     lista_atividade = Atividade.objects.filter(id_turma=id_turma_logado)
#     return render(request, 'Lista_Atividade',
#                   {'turma_logada': turma_logada, 'lista_atividade': lista_atividade,
#                    'id_turma':id_turma})

def ver_atividades(request,id_turma):
    print(f'get do id{id_turma}')
    dados_turma = Turma.objects.filter(id=id_turma).values("nome_turma", "id")
    print(dados_turma)
    turma_logada = dados_turma[0]
    turma_logada = turma_logada['nome_turma']
    id_turma_logado = dados_turma[0]
    id_turma_logado = id_turma_logado['id']
    lista_atividade = Atividade.objects.filter(id_turma=id_turma_logado)
    return render(request, 'Lista_Atividade.html',
                  {'turma_logada': turma_logada, 'lista_atividade': lista_atividade,
                   'id_turma':id_turma})
 
def cad_atividade(request, id_turma):
    turma_logada = Turma.objects.filter(id=id_turma).values("nome_turma", "id")
    turma_logada = turma_logada[0]
    turma_logada = turma_logada['nome']
    return render(request, 'Lista_Atividade.html', {'turma_logada':turma_logada, 'id_logado':turma_logada})
     
def salvar_atividade(request):
    if (request.method == 'POST'):
        atividade_nome = request.POST.get('atividade_nome')
        id_turma = request.POST.get('id_turma_logado')
        print("cheguei aqui")
        turma = Turma.objects.get(id=id_turma)
        arquivo = request.FILES.get('arquivo')
        print(arquivo) # Obtém o arquivo enviado pelo formulário
        grava_atividade = Atividade(
            nome_atividade = atividade_nome,
            id_turma = turma,
            arquivo = arquivo # Associa o arquivo á atividade
        )
       
        grava_atividade.save()
        messages.info(request, 'Atividade ' + atividade_nome + ' cadastrada com sucesso')
        return redirect('ver_atividades/' + id_turma)

def valida_excluir(request, id_turma):
    id_professor = request.GET.get('id_professor')
    turma = get_object_or_404(Turma, id=id_turma)
    if Atividade.objects.filter(id_turma=turma.id):
        messages.info(request, 'Turma' + turma.nome_turma + 'possui atividades cadastradas, não pode excluir')
        return redirect('lista_turma', id_professor=id_professor)
    turma.delete()
    return redirect('lista_turma', id_professor=id_professor)

def exibir_arquivo(request, nome_arquivo):
    caminho_arquivo = os.path.join('atividades_arquivos/', nome_arquivo)

    if os.path.exists(caminho_arquivo):
        with open(caminho_arquivo, 'rb') as arquivo:
            conteudo = arquivo.read()

        tipo_mimetype, _ = mimetypes.guess_type(caminho_arquivo)

        resposta = HttpResponse(conteudo, content_type = tipo_mimetype)

        resposta['Content-Disposition'] = 'inline; filename="' + nome_arquivo + '"'
        return resposta
    else:
        return HttpResponse('Arquivo não encontrado', status=404)
    
def exportar_para_excel_turmas(request):
    # Consulta para obter os dados que deseja exportar
    dados_turma = Turma.objects.all()

    # Criando um novo arquivo Excel
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Turmas"

    # Escrevendo cabeçalhos
    sheet['A1'] = "ID"
    sheet['B1'] = "Nome da Turma"

    # Escrevendo os dados
    for index, turma in enumerate(dados_turma, start=2):
        sheet[f'A{index}'] = turma.id
        sheet[f'B{index}'] = turma.nome_turma

    # Salvando o arquivo excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=turma.xlsx'
    workbook.save(response)
    return response

def exportar_para_excel_Atividades(request):
    # Consulta para obter os dados que deseja exportar
    dados_atividades = Atividade.objects.all()

    # Criando um novo arquivo Excel
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Atividades"

    # Escrevendo cabeçalhos
    sheet['A1'] = "ID"
    sheet['B1'] = "Nome da Atividade"
    sheet['C1'] = "Turma"

    # Escrevendo os dados
    for index, atividade in enumerate(dados_atividades, start=2):
        sheet[f'A{index}'] = atividade.id
        sheet[f'B{index}'] = atividade.nome_atividade
        sheet[f'C{index}'] = atividade.id_turma.nome_turma

    # Salvando o arquivo excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=atividades.xlsx'
    workbook.save(response)
    return response