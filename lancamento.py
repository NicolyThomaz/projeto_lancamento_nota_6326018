import pandas as pd
import pyautogui
import time
import subprocess
import pyperclip
from pathlib import Path

CAMINHO_CSV = Path(__file__).resolve().parent / "dados" / "notas_alunos.csv"
URL_FORMULARIO = "https://forms.gle/rpMbT3eceiMtbhBaA"

pyautogui.PAUSE = 0.4
pyautogui.FAILSAFE = True

def carregar_alunos():
    df = pd.read_csv(
        CAMINHO_CSV,
        sep=";",
        dtype=str,
        keep_default_na=False,
        encoding="utf-8-sig"
    )

    df.columns = df.columns.str.strip()

    for coluna in df.columns:
        nome = coluna.lower().replace(" ", "")
        if nome in {"notao2", "nota02", "nota2"}:
            df = df.rename(columns={coluna: "Notao2"})
            break

    for coluna in df.columns:
        df[coluna] = df[coluna].str.strip()

    return df

def converter_nota(valor):
    valor = str(valor).strip().replace(",", ".")

    if valor.upper() in {
        "", "FALTOU", "FALTA", "NONE", "NAN", "NULL", "-"
    }:
        return 0.0

    try:
        nota = float(valor)
    except ValueError:
        return 0.0

    if nota < 0 or nota > 10:
        return None

    return nota

def formatar_nota(valor):
    nota = converter_nota(valor)

    if nota is None:
        return None

    return str(nota).replace(".", ",")

def preparar_aluno(aluno):
    nome = str(aluno.get("Nome", "")).strip()
    ra = str(aluno.get("RA", "")).strip()

    if not nome:
        nome = "Não encontrado"

    if not ra:
        ra = "Não encontrado"

    colunas_notas = ["Nota01", "TF01", "Notao2", "TF02"]
    notas_formatadas = {}

    for coluna in colunas_notas:
        valor_original = str(aluno.get(coluna, "")).strip()
        valor = converter_nota(valor_original)

        try:
            numero = float(valor_original.replace(",", "."))
            if numero < 0 or numero > 10:
                notas_formatadas[coluna] = ""
                print(
                    f"[AVISO] {nome}: nota inválida em {coluna}. "
                    "O campo será enviado vazio."
                )
                continue
        except ValueError:
            pass

        if valor is None:
            notas_formatadas[coluna] = ""
        else:
            notas_formatadas[coluna] = str(valor).replace(".", ",")

    return {
        "Nome": nome,
        "RA": ra,
        **notas_formatadas
    }

def ir_para_primeiro_campo():
    time.sleep(3)

    pyautogui.press("esc")

    for _ in range(3):
        pyautogui.press("tab")
        time.sleep(0.2)

def abrir_formulario():
    subprocess.Popen(
        ["cmd", "/c", "start", "", "chrome", URL_FORMULARIO],
        shell=False
    )
    time.sleep(2)
    ir_para_primeiro_campo()

def preencher_campo(texto):
    pyperclip.copy(str(texto))
    pyautogui.hotkey("ctrl", "v")

def preencher_formulario(aluno):
    campos = [
        aluno["Nome"],
        aluno["RA"],
        aluno["Nota01"],
        aluno["TF01"],
        aluno["Notao2"],
        aluno["TF02"]
    ]

    for indice, valor in enumerate(campos):
        preencher_campo(valor)

        if indice < len(campos) - 1:
            pyautogui.press("tab")

def enviar_formulario():
    pyautogui.press("tab")
    pyautogui.press("enter")
    time.sleep(3)
    
def executar():
    try:
        df = carregar_alunos()
    except FileNotFoundError:
        print(f"CSV não encontrado: {CAMINHO_CSV}")
        return
    except (OSError, pd.errors.ParserError) as erro:
        print(f"Erro ao ler o CSV: {erro}")
        return

    if df.empty:
        print("Não há alunos para lançar.")
        return

    print(f"Alunos encontrados: {len(df)}")
    print("A automação começará em 5 segundos.")
    print("Para interromper, mova o mouse para o canto superior esquerdo da tela.")
    time.sleep(5)

    abrir_formulario()

    for indice, (_, linha) in enumerate(df.iterrows(), start=1):
        aluno = preparar_aluno(linha)

        if aluno is None:
            continue

        print(f"[{indice}/{len(df)}] Preenchendo: {aluno['Nome']}")

        if indice > 1:
            pyautogui.hotkey("ctrl", "l")
            pyautogui.write(URL_FORMULARIO, interval=0.01)
            pyautogui.press("enter")
            time.sleep(5)
            ir_para_primeiro_campo()

        preencher_formulario(aluno)
        enviar_formulario()

        print(f"[OK] Envio solicitado para {aluno['Nome']}.")

        time.sleep(2)

    print("\nProcessamento concluído.")

if __name__ == "__main__":
    executar()
