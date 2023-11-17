from flask import Flask, render_template, request, redirect, url_for
import requests
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html

app = Flask(__name__)

# Dados de exemplo (substitua por um sistema de autenticação real)
allowed_domain = 'thomsonreuters.com'


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']

        # Verificar se o e-mail possui o domínio correto
        if email.endswith('@' + allowed_domain):
            # Autenticação bem-sucedida, redirecione para a página de pesquisa
            return redirect(url_for('pesquisa'))
        else:
            # Autenticação falhou, você pode adicionar uma mensagem de erro
            return render_template('login.html', error='E-mail não permitido')

    return render_template('login.html')

api_url = "https://api.everest.validity.com/api/2.0/prospect/search"
headers = {"X-API-KEY": "f1c6cf8f0f27f4057f5787158fc7fac85602a1ec"}

def obter_graficos(domain):
    payload = {"domain": domain}
    
    # Fazer a chamada à API para obter dados
    response = requests.post(api_url, headers=headers, json=payload)

    if response.status_code == 200:
        data = response.json()
        day_data = data["results"]["day"]
        subject_data = data["results"]["subject"]

        # Criar um gráfico de barras para os dados do dia
        fig_day = px.bar(x=list(day_data.keys()), y=list(day_data.values()), labels={'x': 'Dia', 'y': 'Quantidade de Envios'})
        fig_day.update_layout(title='Envios por Dia')

        # Ordenar os dados dos assuntos com base na quantidade de envios
        subject_data.sort(key=lambda x: x["count"], reverse=True)

        # Selecionar apenas os 5 principais assuntos
        top_10_subjects = subject_data[:10]

        # Criar um gráfico de barras para os 5 assuntos com os maiores envios
        fig_bars = px.bar(x=[info['subject'] for info in top_10_subjects], y=[info['count'] for info in top_10_subjects],
                          labels={'x': 'Assunto', 'y': 'Quantidade de Envios'})
        fig_bars.update_layout(title='10 Assuntos com Maior Quantidade de Envios')

        return fig_day, fig_bars

    else:
        print(f"Erro ao chamar a API: {response.status_code}")
        return None, None

def obter_graficos(domain):
    # Fazer a chamada à primeira API para obter dados
    api_url = "https://api.everest.validity.com/api/2.0/prospect/search"
    headers = {"X-API-KEY": "f1c6cf8f0f27f4057f5787158fc7fac85602a1ec"}

    payload = {"domain": domain}
    response = requests.post(api_url, headers=headers, json=payload)

    if response.status_code == 200:
        data = response.json()
        id_resgatado = data["results"]["id"]

        print(f"ID resgatado: {id_resgatado}")

        # Fazer a chamada à segunda API usando o ID obtido
        api_url_2 = f"https://api.everest.validity.com/api/2.0/prospect/search/{id_resgatado}/traps"
        response_2 = requests.get(api_url_2, headers=headers)

        if response_2.status_code == 200:
            data_2 = response_2.json()
            day_data = data_2["results"]["day"]
            subject_data = data_2["results"]["subject"]

            # Criar um gráfico de barras para os dados do dia
            fig_day = px.bar(x=list(day_data.keys()), y=list(day_data.values()), labels={'x': 'Dia', 'y': 'Quantidade de Envios'})
            fig_day.update_layout(title='Envios por Dia')

            # Ordenar os dados dos assuntos com base na quantidade de envios
            subject_data.sort(key=lambda x: x["count"], reverse=True)

            # Selecionar apenas os 5 principais assuntos
            top_10_subjects = subject_data[:10]

            # Criar um gráfico de barras para os 5 assuntos com os maiores envios
            fig_bars = px.bar(x=[info['subject'] for info in top_10_subjects], y=[info['count'] for info in top_10_subjects],
                              labels={'x': 'Assunto', 'y': 'Quantidade de Envios'})
            fig_bars.update_layout(title='10 Assuntos com Maior Quantidade de Envios')

            return dcc.Graph(figure=fig_day), dcc.Graph(figure=fig_bars)

        else:
            print(f"Erro ao chamar a segunda API: {response_2.status_code}")
            return None, None

    else:
        print(f"Erro ao chamar a primeira API: {response.status_code}")
        return None, None

@app.route('/pesquisa', methods=['GET', 'POST'])
def pesquisa():
    if request.method == 'POST':
        domain = request.form['domain']

        # Chamar a função para obter os gráficos
        grafico_day, grafico_bars = obter_graficos(domain)

        return render_template('pesquisa_resultado.html', grafico_day=grafico_day, grafico_bars=grafico_bars)

    return render_template('pesquisa.html')


if __name__ == '__main__':
    app.run(debug=True)
