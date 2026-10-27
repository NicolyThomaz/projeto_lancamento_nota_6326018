import lancamento
import consulta

def exibir_menu():
    print("\n" + "=" * 35)
    print("  SISTEMA DE LANÇAMENTO DE NOTAS")
    print("=" * 35)
    print("1 - Preencher formulários")
    print("2 - Consultar informações dos alunos")
    print("0 - Sair")
    print("=" * 35)

def main():
    while True:
        exibir_menu()

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            lancamento.executar()
        elif opcao == "2":
            consulta.executar()
        elif opcao == "0":
            print("Encerrando o sistema...")
            break
        else:
            print("Opção inválida! Escolha 1, 2 ou 0.")

if __name__ == "__main__":
    main()