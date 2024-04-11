from django.http import HttpResponse
from django.shortcuts import render
from hashlib import sha256
from .models import Professor, Turma, Atividade
from django.db import connection, transaction
from django.contrib import messages # biblioteca de mensagens do Django

def initial_population():

    print("Vou Popular")

    cursor = connection.cursor()

    # Popular Tabela Professor
    senha = "123456" # senha inicial para todos os usuários
    senha_armazenar = sha256(senha.encode()).hexdigest()
    # Montamos aqui nossa intrução SQL
    insert_sql_professor = "INSERT INTO App_Escola_professor (nome, email, senha) VALUES"
    insert_sql_professor = insert_sql_professor + "('Prof. Barak Obama', 'barak.obama@gmail.com', '" + senha_armazenar + "'),"
    insert_sql_professor = insert_sql_professor + "('Profa. Angela Merkel', 'angela.merkel@gmail.com', '" + senha_armazenar + "'),"
    insert_sql_professor = insert_sql_professor + "('Prof. Xi Jinping', 'xi.jinping@gmail.com', '" + senha_armazenar + "')"

    cursor.execute(insert_sql_professor)
    transaction.atomic() # Necessário commit para insert e update
    # Fim da População da tabela Professor

    #----------------------------------------------------------------------------------------

    # Popular Tabela Turma
    # Montamos aqui nossa instrução SQL
    insert_sql_turma = "INSERT INTO App_Escola_turma (nome_turma, id_professor_id) VALUES"
    insert_sql_turma = insert_sql_turma + "('1° Semestre - Desenvolvimento de Sistemas', 1), "
    insert_sql_turma = insert_sql_turma + "('2° Semestre - Desenvolvimento de Sistemas', 2), "
    insert_sql_turma = insert_sql_turma + "('3° Semestre - Desenvolvimento de Sistemas', 3) "

    cursor.execute(insert_sql_turma)
    transaction.atomic() # Necessário commit para insert e update

    # Fim da população da tabela Turma
    
    #-----------------------------------------------------------------------------------------

    # Popular Tabela Atividade
    # Montamos aqui nossa instrução SQL
    insert_sql_atividade = "INSERT INTO App_Escola_atividade (nome_atividade, id_turma_id) VALUES"
    insert_sql_atividade = insert_sql_atividade + "('Apresentar Fundamentos de Programação', 1), "
    insert_sql_atividade = insert_sql_atividade + "('Apresentar FrameWork Django', 2), "
    insert_sql_atividade = insert_sql_atividade + "('Apresentar conceitos de Gerenciamento de Projetos ', 3) "

    cursor.execute(insert_sql_atividade)
    transaction.atomic() # Necessário commit para insert e update

    # Fim da população da tabela Atividade

    print("Populei")

def abre_index(request):
    # return render(request, 'index.html')
    # mensagem = " OLÁ TURMA, MUITO BOM DIA!"
    # return HttpResponse(mensagem)

    # query set Tipos de Look Up
    # nome__exact='SS' - tem que ser exatamento igual
    # nome__contains='H' - contem o H maiusculo
    # nome__icontains='H' - ignora se maiúsculo ou minúsculo
    # nome startswith='M' - traz o que começa com a letra M ou sequencia de letras
    # nome istartswith='M' - traz o que começa com a letra ignorando se maiusculo ou minusculo ou sequencia de letras
    # nome__endswith='a' - traz o que termina com a letra a minusculo ou sequencia de letras
    # nome__iendswith='a' - traz o que termina com a letra a ignorando maiusculo ou minusculo
    # nome__ind=['Michael', 'Obama']) - traz somente os nomes que estão na lista
    #Pode ser feito uma composição 'and' utilizando , (virgula entre os campos) ou 'or' utilizando | (pipe entre os campos)  

    dado_pesquisa = 'Obama'

    verifica_populado = Professor.objects.filter(nome__icontains=dado_pesquisa)
    # verifica_populado = Professor.objects.filter(nome='Prof. Barak Obama')

    if len(verifica_populado) == 0:
        print("Não está populado")
        initial_population()
    else:
        print("Achei Obama", verifica_populado)

    return render(request, 'login.html')

def enviar_login(request):

    if request.method == "POST":
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        senha_criptografada = sha256(senha.encode()).hexdigest()
        dados_professor = Professor.objects.filter(email=email).values("nome", "senha", "id")
        print("Dados do Professor ", dados_professor)

        #if len(dados_professor) > 0:
        if dados_professor:
            senha = dados_professor[0]
            senha = senha['senha']
            usuario_logado = dados_professor[0]
            usuario_logado = usuario_logado['nome']
        
            if senha == senha_criptografada:
                # Se logou corretamente, traz as turmas do professor
                # Para isso instanciamos o model turmas do professor
                id_logado = dados_professor[0]
                id_logado = id_logado['id']
                turmas_do_professor = Turma.objects.filter(id_professor=id_logado)
                print("Turma do Professor ", turmas_do_professor)
                return render(request, 'Cons_Turma_Lista.html', {'usuario_logado': usuario_logado, 'turmas_do_professor': turmas_do_professor, 'id_logado': id_logado})
            else:
                messages.info(request, "Usuário ou senha incorretos. Tente novamente.")
                return render(request, 'login.html')
        
        messages.info(request, "Olá " + email + ", seja bem-vindo! Percebemos que você é novo por aqui. Complete seu cadastro.")
        return render(request, 'cadastro.html', {'login': email})
    
def confirmar_cadastro(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        email = request.POST.get('login')
        senha = request.POST.get('senha')
        senha_criptografada = sha256(senha.encode()).hexdigest()

        grava_professor = Professor(
            nome=nome,
            email=email,
            senha=senha_criptografada
        )
        grava_professor.save()

        mensagem = "OLÁ PROFESSOR " + nome + ", SEJA BEM VINDO!"
        return HttpResponse(mensagem)








