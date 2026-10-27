import pandas as pd
from pathlib import Path

CAMINHO_CSV = Path(__file__).resolve().parent / "dados" / "notas_alunos.csv"

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
        df[coluna] = df[coluna].str.strip()

    return df

def normalizar_ra(ra):
    ra = str(ra).strip().upper().replace(" ", "")

    if ra.startswith("RA"):
        ra = ra[2:]

    return ra

def buscar_alunos(df, termo):
    termo = termo.strip()

    if not termo:
        return df.iloc[0:0]

    nome = df["Nome"].str.contains(
        termo,
        case=False,
        na=False,
        regex=False
    )

    ra = df["RA"].apply(normalizar_ra)
    termo_ra = normalizar_ra(termo)

    encontrado_ra = ra.str.contains(
        termo_ra,
        case=False,
        regex=False
    )

    return df[nome | encontrado_ra]

def converter_nota(valor):
    valor = str(valor).strip().replace(",", ".")

    if valor.upper() in {"", "FALTOU", "FALTA", "NONE", "NAN", "NULL", "-"}:
        return 0.0

    try:
        nota = float(valor)
    except ValueError:
        return 0.0

    if nota < 0 or nota > 10:
        return None

    return nota

def calcular_resultado(aluno):
    nota01 = converter_nota(aluno.get("Nota01", ""))
    nota02 = converter_nota(aluno.get("Nota02", ""))
    tf01 = converter_nota(aluno.get("TF01", ""))
    tf02 = converter_nota(aluno.get("TF02", ""))

    notas = [nota01, nota02, tf01, tf02]

    notas = [nota01, nota02, tf01, tf02]

    if any(nota is None for nota in notas):
        return None, "NÃO É POSSÍVEL CALCULAR: UMA NOTA ESTÁ FORA DOS VALORES PERMITIDOS"

    media_notas = (nota01 + nota02) / 2
    media_tf = (tf01 + tf02) / 2

    nota_final = (media_notas * 8 + media_tf * 2) / 10

    if nota_final >= 6:
        situacao = "APROVADO"
    else:
        situacao = "REPROVADO"

    return nota_final, situacao

def exibir_aluno(aluno):
    nota_final, situacao = calcular_resultado(aluno)

    print("\n" + "-" * 40)
    print(f"Nome:   {aluno.get('Nome', '')}")
    print(f"RA:     {aluno.get('RA', '')}")
    print(f"Nota 1: {aluno.get('Nota01', '')}")
    print(f"TF 1:   {aluno.get('TF01', '')}")
    print(f"Nota 2: {aluno.get('Nota02', '')}")
    print(f"TF 2:   {aluno.get('TF02', '')}")

    if nota_final is not None:
        print(f"Nota final: {nota_final:.2f}")
    else:
        print("Nota final: Indisponível")

    print(f"Situação: {situacao}")
    print("-" * 40)

def executar():
    try:
        df = carregar_alunos()
    except FileNotFoundError:
        print(f"CSV não encontrado: {CAMINHO_CSV}")
        return
    except (OSError, pd.errors.ParserError) as erro:
        print(f"Erro ao ler o CSV: {erro}")
        return

    while True:
        print("\n--- CONSULTA DE ALUNOS ---")
        termo = input(
            "Digite o nome ou RA (0 para voltar): "
        ).strip()

        if termo == "0":
            break

        encontrados = buscar_alunos(df, termo)

        if encontrados.empty:
            print("Nenhum aluno encontrado.")
            continue

        print(f"\nAlunos encontrados: {len(encontrados)}")

        for _, aluno in encontrados.iterrows():
            exibir_aluno(aluno)
